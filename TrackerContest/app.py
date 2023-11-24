import time
from enum import Enum
from typing import Optional

import cv2
import glfw
import imgui
import numpy as np

from TrackerContest.core import Bus
from TrackerContest.core.network import TrackerBroker
from TrackerContest.core.video import VideoPlayer
from TrackerContest.gui import ImGuiApp
from TrackerContest.gui.objects.windows.control_windows import ControlWindow
from TrackerContest.gui.objects.windows.image_windows import ZoomImageWindow
from TrackerContest.gui.utils import Drawer


class States(Enum):
    PLAYING = 1
    TRACKING = 2
    VIEWING = 3


class TrackerContest(ImGuiApp):
    def __init__(self, window_width, window_height, fullscreen):
        super().__init__(window_width, window_height, fullscreen)

        self._image_window = ZoomImageWindow()
        self._camera_window = ControlWindow(x=420, y=0)

        self._frame: Optional[np.ndarray] = None
        self._nf = 0
        Bus.subscribe("new-frame", self._new_frame)

        self.state: Optional[States] = States.PLAYING

        self.video_player = VideoPlayer()
        Bus.subscribe("init-video", self.video_player.init_video)

        self.tracker_broker = TrackerBroker()
        self.tracker_broker.setup_server()
        Bus.subscribe("error-tracking", self.tracker_broker.remove_tracker)

    def _terminate(self):
        super()._terminate()
        self.video_player.stop()
        self.tracker_broker.close()

    def _update(self):
        super()._update()

    def draw_content(self):
        if self.video_player.on_playing:
            if self.state == States.PLAYING:
                self._keys_control_video()
                self._keys_select_roi()

            if self.state == States.TRACKING:
                if self.tracker_broker.num_clients == 0:
                    self.state = States.PLAYING

                self._keys_tracking_control()

            if self.state == States.VIEWING:
                self._keys_control_video()
                self._keys_view_control()

            if self._frame is not None:
                self._image_window.upload_image(self._frame)

        self._image_window.draw()
        self._camera_window.draw()

    def _keys_control_video(self):
        if imgui.is_key_pressed(glfw.KEY_SPACE):
            if self.video_player.on_pause:
                self.video_player.start()
            else:
                self.video_player.pause()
        if imgui.is_key_pressed(glfw.KEY_R):
            self.video_player.restart()
        if imgui.is_key_down(glfw.KEY_RIGHT):
            self.video_player.seek(VideoPlayer.VIDEO_SHIFT)
        if imgui.is_key_down(glfw.KEY_LEFT):
            self.video_player.seek(-VideoPlayer.VIDEO_SHIFT)

    def _keys_tracking_control(self):
        if imgui.is_key_pressed(glfw.KEY_V):
            self.state = States.VIEWING
            self.video_player.pause()
            Bus.publish("stop-tracking")
        if imgui.is_key_pressed(glfw.KEY_E):
            self.state = States.PLAYING
            Bus.publish("stop-tracking")

    def _keys_select_roi(self):
        if imgui.is_key_pressed(glfw.KEY_S):
            if self.tracker_broker.num_clients:
                self.video_player.pause()
                init_frame = self._frame.copy()
                init_frame = cv2.cvtColor(init_frame, cv2.COLOR_RGB2BGR)
                gt_bbox = Drawer.select_roi(init_frame,
                                            window_name=VideoPlayer.ROI_SELECTION_WINDOW_NAME,
                                            h=self._window_height,
                                            w=self._window_width)
                self.tracker_broker.init_all_tracker(self._frame, gt_bbox)
                self.state = States.TRACKING
                self.video_player.start()

    def _keys_view_control(self):
        if imgui.is_key_pressed(glfw.KEY_E):
            self.state = States.PLAYING

    def _new_frame(self, frame: np.ndarray, nf: int):
        self._nf = nf

        if self.state == States.PLAYING:
            self._frame = frame

        if self.state == States.TRACKING:
            t1 = time.time()
            self.tracker_broker.send_frame_all_clients(frame, nf)
            all_bbox = self.tracker_broker.get_all_bbox(self._nf)
            self._frame = Drawer.draw_bboxes(frame, all_bbox)
            t2 = time.time()

            Bus.publish("update-real-fps", int(1 / (t2 - t1)))

        if self.state == States.VIEWING:
            all_bbox = self.tracker_broker.get_all_bbox(self._nf)
            self._frame = Drawer.draw_bboxes(frame, all_bbox)
