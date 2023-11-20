from typing import Optional, List, Tuple, Dict

import threading
import socket
import pickle
import numpy as np
import time

from numpy import ndarray

from TrackerContest.core import Bus


class TrackerClient:

    def __init__(self, client_socket: socket.socket):
        self._name: str = ""
        self._color: tuple = ()
        self._address: str = ""
        self._draw = True
        self._current_fps = 0

        self._bboxes: Dict = {}

        self._client_thread: Optional[threading.Thread] = None
        self._client_socket: socket.socket = client_socket

        self._receive_buffer = 100

    @property
    def name(self):
        return self._name

    @property
    def address(self):
        return self._address

    @property
    def color(self):
        return self._color
    
    @property
    def get_bbox(self, nf: int = -1):
        if nf == -1:
            return self._bboxes.popitem()
        else:
            return self._bboxes.get(nf)

    @property
    def draw(self) -> bool:
        return self._draw

    @draw.setter
    def draw(self, draw: bool):
        self._draw = draw

    @address.setter
    def address(self, address: str):
        self._address = address

    def first_meeting(self):
        data = self._client_socket.recv(1024)
        info = pickle.loads(data)
        self._name = info.get("name")
        self._color = info.get("color")

    def start_track(self, frame: np.ndarray, nf: int):
        self._client_thread = threading.Thread(target=self._track, daemon=True, args=(frame, nf))
        self._client_thread.start()

    def start_init(self, gt_bbox: tuple):
        self._client_thread = threading.Thread(target=self._init, daemon=True, args=gt_bbox)

    def _track(self, frame: np.ndarray, nf: int):
        try:
            self._send_data(frame)
            t1 = time.time()
            self._receive_data(nf)
            t2 = time.time()
            self._current_fps = 1/(t1-t2)
            print(f"Frames sent to {self.address} ({self.name})")
        except Exception as e:
            print(f"Error sending frames to {self.address} ({self.name}): {e}")

    def _init(self, gt_bbox):
        try:
            self._send_data(gt_bbox)
            print(f"Init tracker {self.address} ({self.name})")
        except Exception as e:
            print(f"Error init tracker {self.address} ({self.name}): {e}")

    def _send_data(self, frame: np.ndarray):
        serialized_array = pickle.dumps(frame)
        self._client_socket.send(serialized_array)

    def _receive_data(self, nf: int):
        response = self._client_socket.recv(self._receive_buffer)
        self._bboxes[nf] = pickle.loads(response)


class TrackerBroker:

    N_MAX_TRACKER = 10

    def __init__(self, host='localhost', port=8080):
        self._host: str = host
        self._port: int = port
        self._clients: List[TrackerClient] = []
        self._server_thread: threading.Thread = threading.Thread(target=self._start_server, daemon=True)
        self._server_socket: Optional[socket] = None

        Bus.subscribe("changed-draw-mode", self.change_client_draw_mode)

    @property
    def server_address(self):
        return self._host, self._port

    @server_address.setter
    def server_address(self, new_address: tuple):
        self._host, self._port = new_address

    def setup_server(self):
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind((self._host, self._port))

    def _start_server(self):
        self._server_socket.listen(TrackerBroker.N_MAX_TRACKER)

        print(f"Server listening on {self._host}:{self._port}")

        while True:
            try:
                client_socket, address = self._server_socket.accept()
                tracker_client = TrackerClient(client_socket)
                tracker_client.first_meeting()
                tracker_client.address = "".join(map(str, address))
                self._clients.append(tracker_client)
                print(tracker_client.color)
                Bus.publish("connected-new-tracker", tracker_client.name, tracker_client.color, tracker_client.address)
                print(f"Connection established with {tracker_client.name}")
            except Exception as e:
                print("", e)

    def send_frame_all_clients(self, frame: np.ndarray, nf: int):
        for client in self._clients:
            client.start_track(frame, nf)

    def init_all_tracker(self, gt_bbox: tuple):
        for client in self._clients:
            client.start_init(gt_bbox)

    def get_all_bbox(self, nf: int = -1) -> list:
        return [(client.get_bbox(nf), client.color) for client in self._clients]

    def start(self):
        self._server_thread.start()

    def change_client_draw_mode(self, name: str, draw: bool):
        for client in self._clients:
            if client.name == name:
                client.draw = draw
                break
