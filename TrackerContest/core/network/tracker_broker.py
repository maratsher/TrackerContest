from typing import Optional, List, Tuple, Dict

import threading
import socket
import pickle
import numpy as np
import time
import os
import msgpack_numpy as mp

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
    def address(self):
        return self._address

    @property
    def color(self):
        return self._color
    
    def get_bbox(self, nf):
        return self._bboxes.get(nf)

    @property
    def draw(self) -> bool:
        return self._draw

    @property
    def client_thread(self) -> threading.Thread:
        return self._client_thread

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

    def start_init(self, frame: np.ndarray, gt_bbox: tuple):
        self._client_thread = threading.Thread(target=self._init, daemon=True, args=(frame, gt_bbox, ))
        self._client_thread.start()

    def _track(self, frame: np.ndarray, nf: int):
        try:
            self._send_data(frame)
            self._receive_data(nf)
        except Exception as e:
            print(f"Error _track ({self.name}): {e}")

    def _init(self, frame: np.ndarray, gt_bbox: tuple):
        try:
            self._send_data(frame)
            time.sleep(0.1)
            self._send_data(gt_bbox)
            time.sleep(0.1)
            print("data sent")
        except Exception as e:
            print(f"Error init tracker ({self.name}): {e}")

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
        print(f"receive bbox {self._bboxes[nf]}")
        print(f"fps {self._bboxes[nf]}")

    def stop_tracking(self):
        self._client_thread.join()
        self._send_data("stop")

    def close(self):
        self._client_socket.close()


class TrackerBroker:

    N_MAX_TRACKER = 10

    def __init__(self, socket_path: str = "/tmp/server_socket"):
        self._socket_path = socket_path
        self._clients: List[TrackerClient] = []
        self._server_thread: threading.Thread = threading.Thread(target=self._start_server, daemon=True)
        self._server_socket: Optional[socket] = None

        Bus.subscribe("changed-draw-mode", self._change_client_draw_mode)
        Bus.subscribe("stop-tracking", self._stop_tracking)

    @property
    def server_address(self):
        return self._socket_path

    @server_address.setter
    def server_address(self, new_address: str):
        self._socket_path = new_address

    @property
    def num_clients(self):
        return len(self._clients)

    def setup_server(self):
        try:
            os.remove(self._socket_path)
        except OSError:
            pass
        self._server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind(self._socket_path)
        self._server_thread.start()

    def _start_server(self):
        self._server_socket.listen(TrackerBroker.N_MAX_TRACKER)

        print(f"Server listening on {self._socket_path}")

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

        self._join()

    def init_all_tracker(self, frame: np.ndarray, gt_bbox: tuple):
        for client in self._clients:
            client.start_init(frame, gt_bbox)

        self._join()

    def get_all_bbox(self, nf: int = -1) -> list:
        return [(client.get_bbox(nf), client.color) for client in self._clients if client.draw]

    def _join(self):
        for client in self._clients:
            client.client_thread.join()

    def _change_client_draw_mode(self, name: str, draw: bool):
        for client in self._clients:
            if client.name == name:
                client.draw = draw
                break

    def close(self):
        for client in self._clients:
            client.close()
        self._server_socket.close()
        try:
            os.remove(self._socket_path)
        except OSError:
            pass

    def _stop_tracking(self):
        for client in self._clients:
            client.stop_tracking()

    def remove_tracker(self, name: str):
        for i in range(len(self._clients)):
            if self._clients[i].name == name:
                self._clients.pop(i)
                Bus.publish("remove-tracker", name)

