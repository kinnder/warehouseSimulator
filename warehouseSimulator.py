import concurrent.futures
import json
import logging
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
    'activity_202': {'video': 'Container_02_MoveToRack.mp4', 'duration': 16}
}


class WebServiceHTTPRequestHandler(BaseHTTPRequestHandler):
    _c_operationId = 'operationId'
    _c_containerId = 'containerId'

    _c_status = 'status'
    _c_status_playing = 'playing'
    _c_status_finished = 'finished'
    _c_status_started = 'started'

    _c_timeEstimated = 'timeEstimated'

    def log_message(self, format, *args):
        logging.info(f"{self.client_address[0]} - {args[0]}")
        # BaseHTTPRequestHandler.log_message(self, format, *args)

    def do_GET(self):
        if self.path.startswith('/command'):
            self._do_command()
        elif self.path.startswith('/status'):
            self._do_status()
        else:
            self._do_usage()

    def _do_usage(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        result = f"""Wellcome to WarehouseSimulator, list of supported requests:
/
    show usage help
/status
    check status of warehouse
/command?{self._c_operationId}=1&{self._c_containerId}=1
    call the operation, where
    {self._c_operationId}: [1, 2]
        1 - move container to table
        2 - move container to rack
    {self._c_containerId}: [1, 60]
"""
        self.wfile.write(result.encode('utf-8'))

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def _do_status(self):
        # processing request
        status = self._c_status_playing if videoPlayer.is_playing else self._c_status_finished
        #
        result = {f'{self._c_status}': status}
        self._set_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))

    def _do_command(self):
        parameters = parse_qs(urlparse(self.path).query)
        operationId = 0
        if self._c_operationId in parameters.keys():
            if parameters[self._c_operationId][0].isdigit():
                operationId = int(parameters[self._c_operationId][0])
        containerId = 0
        if self._c_containerId in parameters.keys():
            if parameters[self._c_containerId][0].isdigit():
                containerId = int(parameters[self._c_containerId][0])
        # processing request
        activity = f'activity_{operationId * 100 + containerId}'
        if activity not in activities.keys():
            activity = NO_OPERATION
            operationId = 0
            containerId = 0
        timeEstimated = activities[activity]['duration']
        result = {f'{self._c_operationId}': operationId,
                  f'{self._c_containerId}': containerId,
                  f'{self._c_timeEstimated}': timeEstimated,
                  f'{self._c_status}': self._c_status_started}
        if videoPlayer.is_playing:
            result = {f'{self._c_status}': self._c_status_playing}
        else:
            videoPlayer.schedule_video(activities[activity]['video'])
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
        requests.get(f'http://localhost:{self._serverPort}')


class VideoPlayer:
    _frameName = "visualization"
    is_playing = False

    def schedule_video(self, video_name):
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
    logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO, datefmt="%H:%M:%S")
    logging.getLogger().setLevel(logging.INFO)
    # logging.getLogger().setLevel(logging.DEBUG)

    videoPlayer = VideoPlayer()
    webService = WebService(videoPlayer)
    event = threading.Event()

    videoPlayer.schedule_video(activities[NO_OPERATION]['video'])

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(webService.run, event)
        executor.submit(videoPlayer.run, event)
        logging.info("WarehouseSimulator started")

        input("Press Enter to stop...\n")
        event.set()
        webService.stop()
        videoPlayer.stop()
        logging.info("WarehouseSimulator finished")
