import concurrent.futures
import json
import logging
import queue
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

import cv2
import requests

NO_OPERATION = 'activity_0'

activities = {
    'activity_0': {'video': 'NoOperation.mp4', 'duration': 5},
    'activity_101': {'video': 'Container_01_MoveToTable.mp4', 'duration': 15},
    'activity_201': {'video': 'Container_01_MoveToRack.mp4', 'duration': 15},
    'activity_102': {'video': 'Container_02_MoveToTable.mp4', 'duration': 16},
    'activity_202': {'video': 'Container_02_MoveToRack.mp4', 'duration': 16},
    'activity_103': {'video': 'Container_03_MoveToTable.mp4', 'duration': 17},
    'activity_203': {'video': 'Container_03_MoveToRack.mp4', 'duration': 17},
    'activity_104': {'video': 'Container_04_MoveToTable.mp4', 'duration': 18},
    'activity_204': {'video': 'Container_04_MoveToRack.mp4', 'duration': 18},
    'activity_105': {'video': 'Container_05_MoveToTable.mp4', 'duration': 18},
    'activity_205': {'video': 'Container_05_MoveToRack.mp4', 'duration': 18},
    'activity_106': {'video': 'Container_06_MoveToTable.mp4', 'duration': 19},
    'activity_206': {'video': 'Container_06_MoveToRack.mp4', 'duration': 19},
    'activity_107': {'video': 'Container_07_MoveToTable.mp4', 'duration': 19},
    'activity_207': {'video': 'Container_07_MoveToRack.mp4', 'duration': 19},
    'activity_108': {'video': 'Container_08_MoveToTable.mp4', 'duration': 20},
    'activity_208': {'video': 'Container_08_MoveToRack.mp4', 'duration': 20},
    'activity_109': {'video': 'Container_09_MoveToTable.mp4', 'duration': 21},
    'activity_209': {'video': 'Container_09_MoveToRack.mp4', 'duration': 21},
    'activity_110': {'video': 'Container_10_MoveToTable.mp4', 'duration': 22},
    'activity_210': {'video': 'Container_10_MoveToRack.mp4', 'duration': 22}
}


class WebServiceHTTPRequestHandler(BaseHTTPRequestHandler):
    URL_COMMAND = '/command'
    URL_STATUS = '/status'
    URL_USAGE = '/'
    URL_SIMULATE = '/simulate'
    URL_UI = '/ui'

    OPERATION_ID = 'operationId'
    CONTAINER_ID = 'containerId'

    STATUS = 'status'
    STATUS_PLAYING = 'playing'
    STATUS_FINISHED = 'finished'
    STATUS_STARTED = 'started'

    TIME_ESTIMATED = 'timeEstimated'

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
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Access-Control-Allow-Origin')
        self.end_headers()

    def _do_usage(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.send_header('Access-Control-Allow-Origin', '*')
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
        self.wfile.write(result.encode('utf-8'))

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def _do_status(self):
        # processing request
        status = self.STATUS_PLAYING if videoPlayer._has_Task else self.STATUS_FINISHED
        #
        result = {f'{self.STATUS}': status}
        self._set_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))

    def _do_command(self):
        parameters = parse_qs(urlparse(self.path).query)
        operationId = self._get_parameter(parameters, self.OPERATION_ID)
        containerId = self._get_parameter(parameters, self.CONTAINER_ID)
        # processing request
        activity = f'activity_{operationId * 100 + containerId}'
        if activity not in activities.keys():
            activity = NO_OPERATION
            operationId = 0
            containerId = 0
        timeEstimated = activities[activity]['duration']
        result = {f'{self.OPERATION_ID}': operationId,
                  f'{self.CONTAINER_ID}': containerId,
                  f'{self.TIME_ESTIMATED}': timeEstimated,
                  f'{self.STATUS}': self.STATUS_STARTED}
        if videoPlayer._has_Task:
            result = {f'{self.STATUS}': self.STATUS_PLAYING}
        else:
            videoPlayer.schedule_videos([
                activities[activity]['video']
            ])
        #
        self._set_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))

    def _get_parameter(self, parameters: dict[str, list[str]], parameter_name: str) -> int:
        return int(parameters[parameter_name][0]) \
            if (parameter_name in parameters.keys() and parameters[parameter_name][0].isdigit()) \
            else 0

    def _do_simulate(self):
        parameters = parse_qs(urlparse(self.path).query)
        containerId = self._get_parameter(parameters, self.CONTAINER_ID)
        # processing request
        activity_1 = f'activity_{1 * 100 + containerId}'
        if activity_1 not in activities.keys():
            activity_1 = NO_OPERATION
            containerId = 0
        activity_2 = f'activity_{2 * 100 + containerId}'
        if activity_2 not in activities.keys():
            activity_2 = NO_OPERATION
            containerId = 0
        timeEstimated = 0
        timeEstimated += activities[activity_1]['duration']
        timeEstimated += activities[activity_2]['duration']
        result = {f'{self.CONTAINER_ID}': containerId,
                  f'{self.TIME_ESTIMATED}': timeEstimated,
                  f'{self.STATUS}': self.STATUS_STARTED}
        if videoPlayer._has_Task:
            result = {f'{self.STATUS}': self.STATUS_PLAYING}
        else:
            videoPlayer.schedule_videos([
                activities[activity_1]['video'],
                activities[activity_2]['video']
            ])
        #
        self._set_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))

    def _do_ui(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        result = """
<!doctype html>
<html>
<head>
	<title>Warehouse Simulator</title>
</head>
<body>
<table>
	<tr><td colspan="2"><input type="range" min="1" max="60" value="1" id="containerId" oninput="chooseContainer()"><p>Value: <span id="containerIdValue">1</span></p></td></tr>
	<tr><td><button onclick="moveToTable()">To Table</button></td><td><button onclick="moveToRack()">To Rack</button></td></tr>
	<tr><td colspan="2"><button onclick="simulate()">Simulate</button></td></tr>
	<tr><td colspan="2"><button onclick="status()">Status</button></td></tr>
	<tr><td colspan="2"><p id="statusValue"></p></td></tr>
</table>
</body>
<script>
function moveToTable() {
	var containerId = document.getElementById("containerId").value;
	makeRequest(`/command?operationId=1&containerId=${containerId}`);
}
function moveToRack() {
	var containerId = document.getElementById("containerId").value;
	makeRequest(`/command?operationId=2&containerId=${containerId}`);
}
function simulate() {
	var containerId = document.getElementById("containerId").value;
	makeRequest(`/simulate?containerId=${containerId}`);
}
function status() {
	makeRequest("/status");
}
function makeRequest(request) {
	const xhr = new XMLHttpRequest();
	xhr.open("GET", "http://localhost:8000" + request);
	xhr.setRequestHeader('Access-Control-Allow-Origin', 'localhost:8000');
	xhr.send()
	xhr.onreadystatechange = () => {
		if (xhr.readyState == 4 && xhr.status == 200) {
			var status = document.getElementById("statusValue")
			status.innerHTML = xhr.response
		}
	};
}
function chooseContainer() {
	var slider = document.getElementById("containerId")
	var output = document.getElementById("containerIdValue")
	output.innerHTML = slider.value;
}
</script>
</html>
"""
        self.wfile.write(result.encode('utf-8'))


class WebService:
    _serverName = 'localhost'
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
        requests.post(f'http://localhost:{self._serverPort}')


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
        logging.info(f'playing video: {video_name}')
        logging.debug(f'{video_name}: started')
        while cap.isOpened():
            ret, frame = cap.read()
            if frame is None:
                break
            cv2.imshow(self._frameName, frame)
            cv2.waitKey(1)
        logging.debug(f'{video_name}: finished')
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

    if len(sys.argv) > 1 and sys.argv[1] == 'release':
        app_mode = APP_MODE_RELEASE
        print(sys.argv[1])

    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        app_mode = APP_MODE_DEBUG
        print(sys.argv[1])

    logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO, datefmt="%H:%M:%S")
    serverName = None
    serverPort = 8000
    if app_mode == APP_MODE_DEBUG:
        logging.getLogger().setLevel(logging.DEBUG)
        serverName = 'localhost'
    else:
        logging.getLogger().setLevel(logging.INFO)
        serverName = '0.0.0.0'
    logging.info(f"Application started in {'debug' if app_mode == APP_MODE_DEBUG else 'release'} mode")

    videoPlayer = VideoPlayer()
    webService = WebService(serverName, serverPort, videoPlayer)
    stopEvent = threading.Event()

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(webService.run, stopEvent)
        executor.submit(videoPlayer.run, stopEvent)
        logging.info("WarehouseSimulator started")

        videoPlayer.schedule_videos([
            activities[NO_OPERATION]['video']
        ])

        input("Press Enter to stop...\n")
        stopEvent.set()
        webService.stop()
        videoPlayer.stop()
        logging.info("WarehouseSimulator finished")
