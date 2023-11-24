import os
import socket
import threading
from typing import Optional, List

import numpy as np

from TrackerContest.core import Bus
from TrackerContest.core.network.tracker_client import TrackerClient


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

    def remove_tracker(self, name: str):
        for i in range(len(self._clients)):
            if self._clients[i].name == name:
                self._clients.pop(i)
                Bus.publish("remove-tracker", name)

    def close(self):
        for client in self._clients:
            client.close()
        self._server_socket.close()
        try:
            os.remove(self._socket_path)
        except OSError:
            pass

    def _start_server(self):
        self._server_socket.listen(TrackerBroker.N_MAX_TRACKER)

        print(f"[INFO] Server listening on {self._socket_path}")

        while True:
            try:
                client_socket, address = self._server_socket.accept()
                tracker_client = TrackerClient(client_socket)
                tracker_client.first_meeting()
                tracker_client.address = "".join(map(str, address))
                self._clients.append(tracker_client)
                Bus.publish("connected-new-tracker", tracker_client.name, tracker_client.color, tracker_client.address)
                print(f"[INFO] Connection established with {tracker_client.name}")
            except Exception as e:
                print("[ERROR] Server error: ", e)

    def _join(self):
        for client in self._clients:
            client.client_thread.join()

    def _change_client_draw_mode(self, name: str, draw: bool):
        for client in self._clients:
            if client.name == name:
                client.draw = draw
                break

    def _stop_tracking(self):
        for client in self._clients:
            client.stop_tracking()
