import threading
import time
from typing import Optional

import cv2

from TrackerContest.core import Bus


class VideoPlayer:
    ROI_SELECTION_WINDOW_NAME = "Select ROI"
    VIDEO_SHIFT = 10

    def __init__(self, queue_size=2000):
        self._cap: Optional[cv2.VideoCapture] = None
        self._fps: int = 0
        self._frame_size: Optional[tuple[int]] = None

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
        if self._cap:
            self._cap.release()

    def restart(self):
        self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def seek(self, shift: int):
        target_frame = int(self._current_frame + shift)
        if target_frame < 0:
            target_frame = 0
        if target_frame >= self._cap.get(cv2.CAP_PROP_FRAME_COUNT):
            target_frame = self._cap.get(cv2.CAP_PROP_FRAME_COUNT)
        start = True
        if self._paused:
            start = False
        else:
            self.pause()
        self._cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        self._current_frame = target_frame
        if start:
            self.start()
        else:
            ret, frame = self._cap.read()
            if not ret:
                return
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            Bus.publish("new-frame", frame, self._current_frame)

    def _load_frames(self):
        while True:
            if self._playing and not self._paused:
                ret, frame = self._cap.read()
                if not ret:
                    self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self._current_frame += 1
                Bus.publish("new-frame", frame, self._current_frame)
                time.sleep(1 / self._fps)
            else:
                time.sleep(0.1)
