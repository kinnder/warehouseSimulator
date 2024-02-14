import concurrent.futures
import json
import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import cv2

activities = {'activity_101': {'video': 'Container_01_MoveToTable.mp4', 'duration': 40},
              'activity_201': {'video': 'Container_01_MoveToRack.mp4', 'duration': 40},
              'activity_300': {'video': 'NoOperation.mp4', 'duration': 15}
              }


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
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
        result = "usage: /command?parameter1=1&parameter2=2 or /status"
        self.wfile.write(result.encode('utf-8'))

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def _do_status(self):
        # TODO: переделать на очередь сообщений
        # operation
        status = 'playing' if videoPlayer.is_playing else 'finished'
        #
        result = {'status': status}
        self._set_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))

    def _do_command(self):
        parameters = parse_qs(urlparse(self.path).query)
        parameter1 = int(parameters['parameter1'][0]) if parameters['parameter1'][0].isdigit() else None
        parameter2 = int(parameters['parameter2'][0]) if parameters['parameter2'][0].isdigit() else None
        # TODO: переделать на очередь сообщений
        # operation
        activity_id = parameter1 * 100 + parameter2
        activity = f'activity_{activity_id}'
        timeEstimated = activities[activity]['duration']
        result = {'parameter1': parameter1, 'parameter2': parameter2, 'timeEstimated': timeEstimated}
        if videoPlayer.is_playing:
            result = {'status': 'playing'}
        else:
            videoPlayer.show_activity(activity)
        #
        self._set_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))


class WebService:
    videoPlayer: None

    def run(self, event):
        httpd = HTTPServer(('localhost', 8000), SimpleHTTPRequestHandler)
        httpd.serve_forever()
        # TODO : сюда не доходит
        # https://stackoverflow.com/questions/268629/how-to-stop-basehttpserver-serve-forever-in-a-basehttprequesthandler-subclass
        logging.info("WebService started")
        while not event.is_set():
            pass
        logging.info("WebService finished")


class VideoPlayer:
    win_name = "visualization"
    is_playing = False

    def show_activity(self, activity_name):
        self.show_video_and_wait(activities[activity_name]['video'])

    def show_video_and_wait(self, videoName: str):
        self.is_playing = True
        cap = cv2.VideoCapture(videoName)
        while cap.isOpened():
            ret, frame = cap.read()
            if frame is None:
                break
            cv2.imshow(self.win_name, frame)
            cv2.waitKey(1)
        # TODO: видеопоток должен закрываться только при открытии нового или закрытии приложения
        cap.release()
        self.is_playing = False

    def run(self, event):
        cv2.namedWindow(self.win_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(self.win_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        logging.info("VideoPlayer started")
        self.show_video_and_wait(activities['activity_300']['video'])
#        self.show_video_and_wait(activities['activity_101']['video'])
#        self.show_video_and_wait(activities['activity_201']['video'])
        while not event.is_set():
            cv2.destroyAllWindows()
        logging.info("VideoPlayer finished")


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO, datefmt="%H:%M:%S")

    webService = WebService()
    videoPlayer = VideoPlayer()
    event = threading.Event()

    webService.videoPlayer = videoPlayer
    logging.info("WarehouseSimulator started")

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(webService.run, event)
        executor.submit(videoPlayer.run, event)

        #input("Press Enter to continue...")
        os.system('pause')
        event.set()

    logging.info("WarehouseSimulator finished")
