import concurrent.futures
import json
import logging
import queue
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
    'activity_203': {'video': 'Container_03_MoveToRack.mp4', 'duration': 17}
}


class WebServiceHTTPRequestHandler(BaseHTTPRequestHandler):
    URL_COMMAND = '/command'
    URL_STATUS = '/status'
    URL_USAGE = '/'
    URL_SIMULATE = '/simulate'

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
        status = self.STATUS_PLAYING if videoPlayer.is_playing else self.STATUS_FINISHED
        #
        result = {f'{self.STATUS}': status}
        self._set_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))

    def _do_command(self):
        # TODO: сделать параметры запросов глобальными и перенести их вычленение в отдельную функцию
        parameters = parse_qs(urlparse(self.path).query)
        operationId = 0
        if self.OPERATION_ID in parameters.keys():
            if parameters[self.OPERATION_ID][0].isdigit():
                operationId = int(parameters[self.OPERATION_ID][0])
        containerId = 0
        if self.CONTAINER_ID in parameters.keys():
            if parameters[self.CONTAINER_ID][0].isdigit():
                containerId = int(parameters[self.CONTAINER_ID][0])
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
        if videoPlayer.is_playing:
            result = {f'{self.STATUS}': self.STATUS_PLAYING}
        else:
            videoPlayer.schedule_video(activities[activity]['video'])
        #
        self._set_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))

    def _do_simulate(self):
        # TODO: сделать параметры запросов глобальными и перенести их вычленение в отдельную функцию
        parameters = parse_qs(urlparse(self.path).query)
        containerId = 0
        if self.CONTAINER_ID in parameters.keys():
            if parameters[self.CONTAINER_ID][0].isdigit():
                containerId = int(parameters[self.CONTAINER_ID][0])
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
        if videoPlayer.is_playing:
            result = {f'{self.STATUS}': self.STATUS_PLAYING}
        else:
            videoPlayer.schedule_video(activities[activity_1]['video'])
            videoPlayer.schedule_video(activities[activity_2]['video'])
        #
        self._set_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))


class WebService:
    # _serverName = '0.0.0.0'
    _serverName = 'localhost'
    _serverPort = 8000

    def __init__(self, videoPlayer):
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
    is_playing = False

    def schedule_video(self, video_name):
        # TODO: добавить планирование нескольких видео
        with self._lock:
            self._video_name = video_name

    def play_video(self):
        self.is_playing = True
        cap = cv2.VideoCapture(self._video_name)
        logging.info(f'playing video: {self._video_name}')
        logging.debug(f'{self._video_name}: started')
        while cap.isOpened():
            ret, frame = cap.read()
            if frame is None:
                break
            cv2.imshow(self._frameName, frame)
            cv2.waitKey(1)
        logging.debug(f'{self._video_name}: finished')
        cap.release()
        self.is_playing = False

    _lock = threading.Lock()
    _video_queue = queue.Queue()
    _video_name = None

    def run(self, event):
        cv2.namedWindow(self._frameName, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(self._frameName, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        logging.debug("VideoPlayer started")
        while not event.is_set():
            if self._video_name is not None:
                self.play_video()
                self._video_name = None
            else:
                pass
        cv2.destroyAllWindows()
        logging.debug("VideoPlayer finished")

    def stop(self):
        pass


if __name__ == "__main__":
    # TODO: Добавить разные параметры запуска
    logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO, datefmt="%H:%M:%S")
    logging.getLogger().setLevel(logging.INFO)
    # logging.getLogger().setLevel(logging.DEBUG)

    videoPlayer = VideoPlayer()
    webService = WebService(videoPlayer)
    stopEvent = threading.Event()

    videoPlayer.schedule_video(activities[NO_OPERATION]['video'])

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(webService.run, stopEvent)
        executor.submit(videoPlayer.run, stopEvent)
        logging.info("WarehouseSimulator started")

        input("Press Enter to stop...\n")
        stopEvent.set()
        webService.stop()
        videoPlayer.stop()
        logging.info("WarehouseSimulator finished")
