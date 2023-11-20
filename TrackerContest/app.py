import glfw
import imgui
from enum import Enum
from typing import Optional
import cv2
import numpy as np

from TrackerContest.gui import ImGuiApp
from TrackerContest.gui.objects.windows.image_windows import ZoomImageWindow
from TrackerContest.gui.objects.windows.control_windows import ControlWindow

from TrackerContest.core.video import VideoPlayer
from TrackerContest.core.network import TrackerBroker
from TrackerContest.core.utils import Drawer
from TrackerContest.core import Bus


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
        self.tracker_broker.start()
        Bus.subscribe("changed-address-server", self.tracker_broker.server_address)

    def _terminate(self):
        super()._terminate()
        self.video_player.stop()

    def _update(self):
        super()._update()

    def draw_content(self):
        if self.video_player.on_playing:
            if self.state == States.PLAYING:
                self._key_control_video()
                if imgui.is_key_pressed(glfw.KEY_S):
                    self.video_player.pause()
                    cv2.imshow(VideoPlayer.ROI_SELECTION_WINDOW_NAME, self._frame)
                    gt_bbox = tuple(cv2.selectROI(VideoPlayer.ROI_SELECTION_WINDOW_NAME,
                                                  self._frame,
                                                  fromCenter=False))
                    cv2.destroyWindow(VideoPlayer.ROI_SELECTION_WINDOW_NAME)
                    self.video_player.start()
                    self.tracker_broker.init_all_tracker(gt_bbox)
                    self.state = States.TRACKING

            if self.state == States.TRACKING:
                if imgui.is_key_pressed(glfw.KEY_V):
                    self.video_player.pause()
                    self.state = States.VIEWING
                if imgui.is_key_pressed(glfw.KEY_E):
                    self.state = States.PLAYING

                if self._frame is not None:
                    self.tracker_broker.send_frame_all_clients(self._frame, self._nf)
                    all_bbox = self.tracker_broker.get_all_bbox()
                    self._frame = Drawer.draw_bboxes(self._frame, all_bbox)

            if self.state == States.VIEWING:
                self._key_control_video()
                if imgui.is_key_pressed(glfw.KEY_V):
                    self.state = States.PLAYING

                if self._frame is not None:
                    all_bbox = self.tracker_broker.get_all_bbox(self._nf)
                    self._frame = Drawer.draw_bboxes(self._frame, all_bbox)

            if self._frame is not None:
                self._image_window.upload_image(self._frame)

        self._image_window.draw()
        self._camera_window.draw()

    def _key_control_video(self):
        if imgui.is_key_pressed(glfw.KEY_SPACE):
            if self.video_player.on_pause:
                self.video_player.start()
            else:
                self.video_player.pause()
        if imgui.is_key_pressed(glfw.KEY_R):
            self.video_player.restart()
        if imgui.is_key_pressed(glfw.KEY_RIGHT):
            self.video_player.seek_forward(50)
        if imgui.is_key_pressed(glfw.KEY_LEFT):
            self.video_player.seek_backward(50)

    def _new_frame(self, frame: np.ndarray, nf: int):
        self._frame = frame
        self._nf = nf


