from typing import Optional

import cv2
import threading
import queue
import time

import numpy as np

from TrackerContest.core import Bus


class VideoPlayer:
    ROI_SELECTION_WINDOW_NAME = "Select ROI"

    def __init__(self, queue_size=2000):
        self._cap: Optional[cv2.VideoCapture] = None
        self._fps: int = 0
        self._frame_size: Optional[tuple[int]] = None

        self._frame_queue = queue.Queue(maxsize=queue_size)
        self._playing = False
        self._paused = True
        self._current_frame = 0

        self._frame_lock = threading.Lock()
        self._frame_thread = threading.Thread(target=self._load_frames)
        self._frame_thread.daemon = True
        self._frame_thread.start()

        Bus.subscribe("set-fps", self.set_fps)

    def init_video(self, file_path: str):
        self._cap = cv2.VideoCapture(file_path)
        self._fps = int(self._cap.get(cv2.CAP_PROP_FPS))
        self._frame_size = (int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        self.start()
        Bus.publish("set-init-fps", self._fps)

    def _load_frames(self):
        while True:
            if self._playing and not self._paused:
                ret, frame = self._cap.read()
                if not ret:
                    self.playing = False
                    break
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self._current_frame += 1
                Bus.publish("new-frame", frame, self._current_frame)
                self._frame_queue.put((self._current_frame, frame))
                time.sleep(1/self._fps)
            else:
                time.sleep(0.1)

    @property
    def fps(self) -> int:
        return self._fps

    @property
    def frame_size(self) -> tuple[int]:
        return self._frame_size

    @property
    def on_pause(self) -> bool:
        return self._paused

    @property
    def on_playing(self) -> bool:
        return self._playing

    def set_fps(self, fps: int):
        self._fps = fps

    def set_frame_size(self, frame_size: tuple[int]):
        self._frame_size = frame_size

    def start(self):
        self._playing = True
        self._paused = False

    def pause(self):
        self._paused = True

    def stop(self):
        self._playing = False
        self._paused = False
        self._cap.release()

    def get_frame(self) -> np.ndarray:
        if not self._frame_queue.empty():
            return self._frame_queue.get()[1]
        else:
            return None

    def restart(self):
        self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def seek_forward(self, fn: int):
        target_frame = int(self._current_frame + fn)
        self.pause()
        self._cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        self._current_frame = target_frame
        self.start()

    def seek_backward(self, fn: int):
        target_frame = int(self._current_frame - fn)
        if target_frame < 0:
            target_frame = 0
        self.pause()
        self._cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        self._current_frame = target_frame
        self.start()