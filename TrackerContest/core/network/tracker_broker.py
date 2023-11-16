from typing import Optional, List, Tuple

import threading
import socket
import pickle
import numpy as np
import time

from numpy import ndarray

from TrackerContest.core import Bus


class TrackerClient:
    def __init__(self, client_socket: socket.socket, address: str, name: str, color: np.ndarray):
        self._name: str = name
        self._color: np.ndarray = color
        self._address: str = address
        self._current_bbox: Optional[np.ndarray] = None
        self._draw = True
        self._current_fps = 0

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
    def current_box(self):
        return self._current_bbox

    @property
    def draw(self) -> bool:
        return self._draw

    @draw.setter
    def draw(self, draw: bool):
        self._draw = draw

    def start_track(self, frame: np.ndarray):
        self._client_thread = threading.Thread(target=self._track, daemon=True, args=frame)
        self._client_thread.start()

    def _track(self, frame: np.ndarray):
        try:
            self._send_data(frame)
            t1 = time.time()
            self._receive_data()
            t2 = time.time()
            self._current_fps = 1/(t1-t2)
            print(f"Frames sent to {self.address} ({self.name})")
        except Exception as e:
            print(f"Error sending frames to {self.address} ({self.name}): {e}")



    def _send_data(self, frame: np.ndarray):
        serialized_array = pickle.dumps(frame)
        self._client_socket.send(serialized_array)

    def _receive_data(self):
        response = self._client_socket.recv(self._receive_buffer)
        self._current_bbox = pickle.loads(response)


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
                name = client_socket.recv(1024).decode('utf-8')
                color = pickle.loads(client_socket.recv(1024))
                tracker_client = TrackerClient(client_socket, address, name, color)
                self._clients.append(tracker_client)
                Bus.publish("connected-new-tracker", {"name": name, "color": color, "address": address})
                print(f"Connection established with {address} ({name})")
            except Exception as e:
                print("", e)

    def send_frame_all_clients(self, frame: np.ndarray):
        for client in self._clients:
            client.start_track(frame)

    def get_all_bbox(self) -> list[tuple[ndarray | None, ndarray]]:
        bbox_list = [(client.current_box, client.color) for client in self._clients]
        return bbox_list

    def start(self):
        self._server_thread.start()

    def change_client_draw_mode(self, name: str, draw: bool):
        for client in self._clients:
            if client.name == name:
                client.draw = draw
                break
