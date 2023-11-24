import pickle
import socket
import threading
import time
from typing import Optional, Dict

import msgpack_numpy as mp
import numpy as np

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

        self._receive_buffer = 1024

    @property
    def name(self):
        return self._name

    @property
    def color(self):
        return self._color

    @property
    def client_thread(self) -> threading.Thread:
        return self._client_thread

    @property
    def draw(self) -> bool:
        return self._draw

    @draw.setter
    def draw(self, draw: bool):
        self._draw = draw

    @property
    def address(self):
        return self._address

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

    def start_init(self, frame: np.ndarray, gt_bbox: tuple):
        self._client_thread = threading.Thread(target=self._init, daemon=True, args=(frame, gt_bbox,))
        self._client_thread.start()

    def stop_tracking(self):
        self._client_thread.join()
        self._send_data("stop")

    def get_bbox(self, nf):
        return self._bboxes.get(nf)

    def close(self):
        self._client_socket.close()

    def _track(self, frame: np.ndarray, nf: int):
        try:
            self._send_data(frame)
            self._receive_data(nf)
        except Exception as e:
            print(f"[Error] Failed track ({self.name}): {e}")

    def _init(self, frame: np.ndarray, gt_bbox: tuple):
        try:
            self._send_data(frame)
            time.sleep(0.1)
            self._send_data(gt_bbox)
            time.sleep(0.1)
        except Exception as e:
            print(f"[Error] Failed init ({self.name}): {e}")

    def _send_data(self, frame):
        try:
            serialized_array = mp.packb(frame, default=mp.encode)
            self._client_socket.send(serialized_array)
        except BrokenPipeError or ConnectionResetError:
            Bus.publish("error-tracking", self._name)

    def _receive_data(self, nf: int):
        response_dict = pickle.loads(self._client_socket.recv(self._receive_buffer))
        self._current_fps = response_dict.get("fps")
        self._bboxes[nf] = response_dict.get("bbox")
        Bus.publish("update-tracker-fps", self._name, self._current_fps)
