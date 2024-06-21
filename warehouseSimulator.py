import concurrent.futures
import json
import logging
import queue
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import List, Dict
from urllib.parse import parse_qs, urlparse

import cv2
import requests

NO_OPERATION = "activity_0"

activities = {
    "activity_0": {"video": "NoOperation.mp4", "duration": 5},
    "activity_101": {"video": "Container_01_MoveToTable.mp4", "duration": 15},
    "activity_201": {"video": "Container_01_MoveToRack.mp4", "duration": 15},
    "activity_102": {"video": "Container_02_MoveToTable.mp4", "duration": 16},
    "activity_202": {"video": "Container_02_MoveToRack.mp4", "duration": 16},
    "activity_103": {"video": "Container_03_MoveToTable.mp4", "duration": 17},
    "activity_203": {"video": "Container_03_MoveToRack.mp4", "duration": 17},
    "activity_104": {"video": "Container_04_MoveToTable.mp4", "duration": 18},
    "activity_204": {"video": "Container_04_MoveToRack.mp4", "duration": 18},
    "activity_105": {"video": "Container_05_MoveToTable.mp4", "duration": 18},
    "activity_205": {"video": "Container_05_MoveToRack.mp4", "duration": 18},
    "activity_106": {"video": "Container_06_MoveToTable.mp4", "duration": 19},
    "activity_206": {"video": "Container_06_MoveToRack.mp4", "duration": 19},
    "activity_107": {"video": "Container_07_MoveToTable.mp4", "duration": 19},
    "activity_207": {"video": "Container_07_MoveToRack.mp4", "duration": 19},
    "activity_108": {"video": "Container_08_MoveToTable.mp4", "duration": 20},
    "activity_208": {"video": "Container_08_MoveToRack.mp4", "duration": 20},
    "activity_109": {"video": "Container_09_MoveToTable.mp4", "duration": 21},
    "activity_209": {"video": "Container_09_MoveToRack.mp4", "duration": 21},
    "activity_110": {"video": "Container_10_MoveToTable.mp4", "duration": 22},
    "activity_210": {"video": "Container_10_MoveToRack.mp4", "duration": 22},
}


class WebServiceHTTPRequestHandler(BaseHTTPRequestHandler):
    URL_COMMAND = "/command"
    URL_STATUS = "/status"
    URL_USAGE = "/"
    URL_SIMULATE = "/simulate"
    URL_UI = "/ui"

    OPERATION_ID = "operationId"
    CONTAINER_ID = "containerId"

    STATUS = "status"
    STATUS_PLAYING = "playing"
    STATUS_FINISHED = "finished"
    STATUS_STARTED = "started"

    TIME_ESTIMATED = "timeEstimated"

    def log_message(self, format, *args):
        logging.info(f"{self.client_address[0]} - {args[0]}")

    def do_POST(self):
        self._set_headers()

    def do_GET(self):
        if self.path.startswith(self.URL_COMMAND):
            self._do_command()
        elif self.path.startswith(self.URL_STATUS):
            self._do_status()
        elif self.path.startswith(self.URL_SIMULATE):
            self._do_simulate()
        elif self.path.startswith(self.URL_UI):
            self._do_ui()
        else:
            self._do_usage()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Methods", "GET")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Access-Control-Allow-Origin")
        self.end_headers()

    def _do_usage(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        result = f"""Wellcome to WarehouseSimulator, list of supported requests:
{self.URL_USAGE}
    show usage help
{self.URL_UI}
    show web interface
{self.URL_STATUS}
    check status of warehouse
{self.URL_COMMAND}?{self.OPERATION_ID}=1&{self.CONTAINER_ID}=1
    call the operation, where
    {self.OPERATION_ID}: [1, 2]
        1 - move container to table
        2 - move container to rack
    {self.CONTAINER_ID}: [1, 60]
{self.URL_SIMULATE}?{self.CONTAINER_ID}=1
    call the simulation of pick and place cycle
    {self.CONTAINER_ID}: [1, 60]
"""
        self.wfile.write(result.encode("utf-8"))

    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def _do_status(self):
        # processing request
        status = self.STATUS_PLAYING if videoPlayer._has_Task else self.STATUS_FINISHED
        #
        result = {f"{self.STATUS}": status}
        self._set_headers()
        self.wfile.write(json.dumps(result).encode("utf-8"))

    def _do_command(self):
        parameters = parse_qs(urlparse(self.path).query)
        operationId = self._get_parameter(parameters, self.OPERATION_ID)
        containerId = self._get_parameter(parameters, self.CONTAINER_ID)
        # processing request
        activity = f"activity_{operationId * 100 + containerId}"
        if activity not in activities.keys():
            activity = NO_OPERATION
            operationId = 0
            containerId = 0
        timeEstimated = activities[activity]["duration"]
        result = {
            f"{self.OPERATION_ID}": operationId,
            f"{self.CONTAINER_ID}": containerId,
            f"{self.TIME_ESTIMATED}": timeEstimated,
            f"{self.STATUS}": self.STATUS_STARTED,
        }
        if videoPlayer._has_Task:
            result = {f"{self.STATUS}": self.STATUS_PLAYING}
        else:
            videoPlayer.schedule_videos([activities[activity]["video"]])
        #
        self._set_headers()
        self.wfile.write(json.dumps(result).encode("utf-8"))

    def _get_parameter(self, parameters: Dict[str, List[str]], parameter_name: str) -> int:
        return (
            int(parameters[parameter_name][0])
            if (parameter_name in parameters.keys() and parameters[parameter_name][0].isdigit())
            else 0
        )

    def _do_simulate(self):
        parameters = parse_qs(urlparse(self.path).query)
        containerId = self._get_parameter(parameters, self.CONTAINER_ID)
        # processing request
        activity_1 = f"activity_{1 * 100 + containerId}"
        if activity_1 not in activities.keys():
            activity_1 = NO_OPERATION
            containerId = 0
        activity_2 = f"activity_{2 * 100 + containerId}"
        if activity_2 not in activities.keys():
            activity_2 = NO_OPERATION
            containerId = 0
        timeEstimated = 0
        timeEstimated += activities[activity_1]["duration"]
        timeEstimated += activities[activity_2]["duration"]
        result = {
            f"{self.CONTAINER_ID}": containerId,
            f"{self.TIME_ESTIMATED}": timeEstimated,
            f"{self.STATUS}": self.STATUS_STARTED,
        }
        if videoPlayer._has_Task:
            result = {f"{self.STATUS}": self.STATUS_PLAYING}
        else:
            videoPlayer.schedule_videos([activities[activity_1]["video"], activities[activity_2]["video"]])
        #
        self._set_headers()
        self.wfile.write(json.dumps(result).encode("utf-8"))

    def _do_ui(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        result = """
<!doctype html>
<html lang="ru">
<head>
	<meta name="viewport" content="width=device-width, initial-scale=1">
    <meta content="text/html;charset=utf-8" http-equiv="Content-Type">
	<meta content="utf-8" http-equiv="encoding">
	<title>Warehouse Simulator</title>
	<link
		rel="stylesheet"
		href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css"
	/>
	<!-- <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script> -->
</head>
<body>
	<main class="container">
		<nav>
			<ul>
				<li><strong>Warehouse</strong></li>
			</ul>
			<ul>
				<li>
					<a href="#" class="secondary" data-tooltip="Статус обновляется каждые 0.5 секунд" data-placement="bottom" onclick="updateStatus()">
						<span id="statusIcon">🔴</span>
						<span id="status">Disconnected</span>
					</a>
				</li>
			</ul>
			<ul>
				<li><a href="#" class="contrast" onclick="goTo('control')">Управление</a></li>
				<li><a href="#" class="contrast" onclick="goTo('logs')">Логи</a></li>
			</ul>
		</nav>

		<div id="control" class="page active hor-if-pc">
			<div id="visualizer-grid">
				<input class="slider" type="range" min="1" max="6" step="1" value="1" id="containerY">
				<div id="visualizer"></div>
				<div><input id="containerIdValue" type="number" max="60" min="1" value=""></div>
				<input class="slider" type="range" min="1" max="10" step="1" value="1" id="containerX">
			</div>
			<div class="right-side">
				<div role="group" style="margin-bottom: 0;">
					<button id="moveToTable" onclick="moveToTable()">Забрать на стол</button>
					<button class="secondary" id="moveToRack" onclick="moveToRack()">Вернуть на склад</button>
				</div>
				<div role="group">
					<button class="contrast" id="simulate" onclick="simulate()">Симуляция цикла</button>
				</div>
				<!-- <p id="statusValue"></p> -->
				<progress id="progress" value="0" max="100" />
			</div>
		</div>

		<div id="logs" class="page">
			<div class="heading-button">
				<h2>Локальные логи</h2>
				<button class="contrast" onclick="clearLogs()">🗑️</button>
			</div>
			<div id="logbox">

			</div>
		</div>
	</main>
	

<style>
	@media (min-width: 1024px) {
		.hor-if-pc {
			display: flex;
			justify-content: space-between;
		}

		.right-side {
			width: 40%;
			margin-top: 30px;
			margin-inline: 20px;
		}
	}

	@media (min-width: 100px) and (max-width: 420px) {
		#status {
			display: none !important;
			visibility: hidden;
		}
	}

	@media (max-device-width: 768px) { 
		#containerY {
			height: 98% !important;
			margin-right: -2px !important;
		}

		#containerX {
			width: 97% !important;
			/* margin-top: 28px !important; */
		}

		#visualizer {
			grid-gap: 2px !important;
		}
	}

	.page {
		display: none;
	}

	.page.active {
		display: block;
	}

	#logbox {
		display: flex;
		flex-direction: column-reverse;
	}

	.heading-button {
		display: flex;
		justify-content: space-between;

		button {
			width: 40px;
			height: 40px;
			background-color: brown;
			border: 0;
			padding: 0;
		}
	
	}

	#logbox > p {
		margin-bottom: 0;
	}



	#control {
		margin-top: 20px;
	}

	#control .right-side {
		margin-top: 0;
	}

	a {
		text-decoration: none;
	}

	.container {
		padding-top: 0;
	}
	
	#status {
		color: lightcoral;
	}

	#visualizer-grid {
		display: grid;
		height: 55vh;
		grid-template-columns: 5vh auto;
		grid-template-rows: auto 5vh;
		width: 100%;
	}

	#containerY {
		writing-mode: vertical-lr;
		direction: rtl;
		width: 4vh;
		height: 89%;
		margin: auto auto;
	}


	input[type=range]::-webkit-slider-runnable-track  {
		background: transparent !important;
	}


	#containerX {
		margin: auto auto;
		width: 93%;
	}

	#containerIdValue {
		border: none;
		padding: 0px;
		border-radius: 0px;
		margin: auto auto;
		text-align: center;
		-moz-appearance: textfield;
		-webkit-appearance: none;
		appearance: none;
		height: 100%;
		background-color: transparent;
	}

	#visualizer {
		display: grid;
		grid-template-columns: repeat(10, 1fr);
		grid-gap: 4px;
		width: 100%;
		height: 100%;
		grid-auto-flow: dense;
  		direction: rtl;
	}

	.square {
		background-color: #017fc0;
		/* border: 1px solid black; */
		box-sizing: border-box;
	}

	.square.selected {
		background-color: #0197ff;
		/* border: 1px solid black; */
		box-sizing: border-box;
	}
	
	.square::after {
		content: "";
		display: block;
		height: 10%;
		width: 50%;
		margin: 20% auto;
		background-color: black;
		opacity: 30%;
	}
	
	progress {
		display: none;
	}
</style>


<script>

const url = "http://" + window.location.href.split("/")[2].split(":")[0] + ":8000";

var rows = 6;
var columns = 10;
var currContainer = 1
if (localStorage.currContainer) {
	currContainer = localStorage.currContainer;
}
if (localStorage.logbox) {
	document.getElementById('logbox').innerHTML = localStorage.logbox;
} else {
	document.getElementById('logbox').innerHTML = "";
}

var dontFinish = false;

var containerX = document.getElementById("containerX");
var containerY = document.getElementById("containerY");
var squares = document.getElementsByClassName('square');
var containerInput = document.getElementById('containerIdValue');
var statusIcon = document.getElementById('statusIcon');
var statusText = document.getElementById('status');
var appStatus = "";
var logbox = document.getElementById('logbox');
var currPage = "control";
if (localStorage.currPage) {
	currPage = localStorage.currPage;
} else {
	localStorage.currPage = currPage;
}

var moveToRackButton = document.getElementById('moveToRack');
var moveToTableButton = document.getElementById('moveToTable');
var simulateButton = document.getElementById('simulate');
var progress = document.getElementById('progress');
var buttons = document.getElementsByTagName('button');

window.addEventListener('DOMContentLoaded', function() {

	var visualizer = document.getElementById('visualizer');
	for (var i = 0; i < rows; i++) {
		for (var j = 0; j < columns; j++) {
			var square = document.createElement('div');
			square.classList.add('square');
			visualizer.appendChild(square);
		}
	}

	containerY.addEventListener('input', updateAxis);
	containerX.addEventListener('input', updateAxis);

	Array.from(visualizer.children).forEach((element, index) => {
		element.addEventListener('click', function() {
			currContainer = visualizer.children.length - index;
			updateAll();
		});
	});

	keepAspectRatio();
	updateAll();
	updateStatus();
	
	goTo(currPage);

	containerInput.addEventListener('change', function() {
		currContainer = containerInput.value;
		updateAll();
	});

	
});



function updateAxis(e) {
	currContainer = Number((containerY.value - 1) * 10) + Number(containerX.value);
	updateAll();
}



function updateAll(e=null) {
	localStorage.currContainer = currContainer;

	containerX.value = (currContainer - 1) % 10 + 1;

	containerY.value = Math.floor((currContainer - 1) / 10) + 1;
	
	for (var i = 0; i < squares.length; i++) {
		squares[i].classList.remove('selected');
	}
	
	squares[squares.length-currContainer].classList.add('selected');

	
	containerInput.value = currContainer;
}




window.addEventListener('resize', keepAspectRatio);

function keepAspectRatio(e=null) {
	var visualizerGrid = document.getElementById('visualizer-grid');
	var visualizer = document.getElementById('visualizer');
	position = visualizer.getBoundingClientRect();

	visualizerGrid.style.height = Math.round(position.width / 10 * 6) + "px";
}


function moveToTable() {
	moveToTableButton.setAttribute("aria-busy", "true")
	makeRequest(`/command?operationId=1&containerId=${currContainer}`);
}
function moveToRack() {
	moveToRackButton.setAttribute("aria-busy", "true")
	makeRequest(`/command?operationId=2&containerId=${currContainer}`);
}
function simulate() {
	simulateButton.setAttribute("aria-busy", "true")
	makeRequest(`/simulate?containerId=${currContainer}`);
}

function blockControls() {
	for (var i = 0; i < buttons.length; i++) {
		buttons[i].disabled = true;
	}
}


function afterAction(actionResult) {
	dontFinish = true
	setTimeout(function() {
		dontFinish = false;
	}, 2000);

	progress.value = 0;
	progress.style.display = "block";

	blockControls();
	
	var estimateInSeconds = actionResult.timeEstimated / 2.9; // Replace with your estimate in seconds
	var progressInterval = setInterval(updateProgress, 1000);

	function updateProgress() {
		progress.value += Math.floor(100 / estimateInSeconds);
		if (progress.value >= 100) {
			clearInterval(progressInterval);
			updateStatus();
		}
	}
}

function finishedAction() {
	for (var i = 0; i < buttons.length; i++) {
		buttons[i].disabled = false;
	}

	moveToRackButton.setAttribute("aria-busy", "false")
	moveToTableButton.setAttribute("aria-busy", "false")
	simulateButton.setAttribute("aria-busy", "false")
	
	progress.style.display = "none";
}

function makeRequest(request) {
	fetch(url + request)
		.then(response => response.json())
		.then(data => {
			if (request == "/status") {
				appStatus = data.status;
			} else {
				afterAction(data);
				var message = `${new Date().toLocaleTimeString()} — `
				if (data.operationId !== undefined) {
					var operation = data.operationId == 1 ? "выдвигается на стол" : "выдвигается на склад";
					message += `Контейнер ${data.containerId} ${operation}`;
				} else {
					message += `Контейнер ${data.containerId} проходит цикл`;
				}
				logbox.appendChild(document.createElement('p')).innerHTML = message;
				localStorage.logbox = logbox.innerHTML;
			}
		})
		.catch(error => {
			console.error("Error:", error);
			if (request == "/status") {
				appStatus = {status: "error"};
			}
		});
}

function updateStatus(e=null) {
	makeRequest("/status");
	if (appStatus == "finished") {
		statusIcon.innerHTML = "🟢";
		statusText.innerHTML = "Ready";
		statusText.style.color = "gray";
		if (!dontFinish) finishedAction();
	} else if (appStatus == "playing") {
		statusIcon.innerHTML = "🟡";
		statusText.innerHTML = "In progress";
		statusText.style.color = "gray";
		blockControls();
	} else {
		statusIcon.innerHTML = "🔴";
		statusText.innerHTML = "Disconnected";
		statusText.style.color = "lightcoral";
	}
}

function goTo(page) {
	var pages = document.getElementsByClassName('page');
	for (var i = 0; i < pages.length; i++) {
		pages[i].classList.remove('active');
	}
	localStorage.currPage = page;
	document.getElementById(page).classList.add('active');
}

function clearLogs() {
	logbox.innerHTML = "";
	localStorage.logbox = "";
}

statusInterval = setInterval(updateStatus, 500);


</script>



</body>
</html>
"""
        self.wfile.write(result.encode("utf-8"))


class WebService:
    _serverName = "localhost"
    _serverPort = 8000

    def __init__(self, serverName, serverPort, videoPlayer):
        self._serverName = serverName
        self._serverPort = serverPort
        self._videoPlayer = videoPlayer

    _videoPlayer: None
    _httpd: HTTPServer = None

    def run(self, event):
        self._httpd = HTTPServer((self._serverName, self._serverPort), WebServiceHTTPRequestHandler)
        logging.debug("WebService started")
        while not event.is_set():
            self._httpd.handle_request()
        self._httpd.server_close()
        logging.debug("WebService finished")

    def stop(self):
        requests.post(f"http://localhost:{self._serverPort}")


class VideoPlayer:
    _frameName = "visualization"

    def schedule_videos(self, video_names: list):
        with self._lock:
            for video_name in video_names:
                self._video_queue.put(video_name)
            self._has_Task = True

    def play_video(self):
        video_name = self._video_queue.get()
        cap = cv2.VideoCapture(video_name)
        logging.info(f"playing video: {video_name}")
        logging.debug(f"{video_name}: started")
        while cap.isOpened():
            ret, frame = cap.read()
            if frame is None:
                break
            cv2.imshow(self._frameName, frame)
            cv2.waitKey(1)
        logging.debug(f"{video_name}: finished")
        cap.release()

    _lock = threading.Lock()
    _video_queue = queue.Queue()
    _has_Task = False

    def run(self, event):
        cv2.namedWindow(self._frameName, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(self._frameName, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        logging.debug("VideoPlayer started")
        while not event.is_set():
            if self._has_Task:
                while not self._video_queue.empty():
                    self.play_video()
                self._has_Task = False
            else:
                pass
        cv2.destroyAllWindows()
        logging.debug("VideoPlayer finished")

    def stop(self):
        pass


APP_MODE_DEBUG = 1
APP_MODE_RELEASE = 2

if __name__ == "__main__":
    app_mode = APP_MODE_DEBUG

    if len(sys.argv) > 1 and sys.argv[1] == "release":
        app_mode = APP_MODE_RELEASE
        print(sys.argv[1])

    if len(sys.argv) > 1 and sys.argv[1] == "debug":
        app_mode = APP_MODE_DEBUG
        print(sys.argv[1])

    logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO, datefmt="%H:%M:%S")
    serverName = None
    serverPort = 8000
    if app_mode == APP_MODE_DEBUG:
        logging.getLogger().setLevel(logging.DEBUG)
        serverName = "localhost"
    else:
        logging.getLogger().setLevel(logging.INFO)
        serverName = "0.0.0.0"
    logging.info(f"Application started in {'debug' if app_mode == APP_MODE_DEBUG else 'release'} mode")

    videoPlayer = VideoPlayer()
    webService = WebService(serverName, serverPort, videoPlayer)
    stopEvent = threading.Event()

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(webService.run, stopEvent)
        executor.submit(videoPlayer.run, stopEvent)
        logging.info("WarehouseSimulator started")

        videoPlayer.schedule_videos([activities[NO_OPERATION]["video"]])

        input("Press Enter to stop...\n")
        stopEvent.set()
        webService.stop()
        videoPlayer.stop()
        logging.info("WarehouseSimulator finished")
