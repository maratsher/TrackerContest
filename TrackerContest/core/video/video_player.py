from typing import Optional

import cv2
import threading
import queue
import time

import numpy as np

from TrackerContest.core import Bus

class VideoPlayer:
    def __init__(self, queue_size=100):
        self._cap: Optional[cv2.VideoCapture] = None
        self._fps: int = 0
        self._frame_size: Optional[tuple[int]] = None

        self._frame_queue = queue.Queue(maxsize=queue_size)
        self._playing = False
        self._paused = False
        self._current_frame = 0
        #self._target_fps = target_fps

        self._frame_lock = threading.Lock()
        self._frame_thread = threading.Thread(target=self._load_frames)
        self._frame_thread.daemon = True
        self._frame_thread.start()

        Bus.subscribe("set-fps", self.set_fps)

    def init_video(self, file_path: str):
        self._cap = cv2.VideoCapture(file_path)
        self._fps = int(self._cap.get(cv2.CAP_PROP_FPS))
        self._frame_size = (int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        Bus.publish("set-init-fps", self._fps)

    def _load_frames(self):
        while True:
            if self._playing and not self._paused:
                ret, frame = self._cap.read()
                if not ret:
                    self.playing = False
                    break
                self._frame_queue.put((self._current_frame, frame))
                self._current_frame += 1
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

    def seek_forward(self, seconds):
        target_frame = int(self._current_frame + seconds * self._fps)
        with self._frame_lock:
            self._cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
            self._current_frame = target_frame

    def seek_backward(self, seconds):
        target_frame = int(self._current_frame - seconds * self._fps)
        if target_frame < 0:
            target_frame = 0
        with self._frame_lock:
            self._cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
            self._current_frame = target_frame


if __name__ == "__main__":
    video_path = "/home/maratsher/Work/omen-viewer/TrackerContest/core/video/test.mp4"
    target_fps = 30  # Set your desired target fps
    player = VideoPlayer(video_path, target_fps=target_fps)

    player.start()

    while player.playing:
        frame_info = player.get_frame()
        if frame_info:
            frame_number, frame = frame_info
            cv2.imshow("Video Player", frame)

            # Calculate delay based on target_fps
            delay = int(1000 / player.target_fps)

            key = cv2.waitKey(delay) & 0xFF
            if key == ord("q"):
                break
            elif key == 81:  # Left arrow key
                player.seek_backward(5)  # Adjust the seek duration as needed
            elif key == 83:  # Right arrow key
                player.seek_forward(5)  # Adjust the seek duration as needed

    cv2.destroyAllWindows()
    player.stop()