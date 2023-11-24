import time

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
                self._key_control_video()
                if imgui.is_key_pressed(glfw.KEY_S):
                    if self.tracker_broker.num_clients:
                        self.video_player.pause()
                        init_frame = self._frame.copy()
                        init_frame = cv2.cvtColor(init_frame, cv2.COLOR_RGB2BGR)
                        # TODO
                        cv2.namedWindow(VideoPlayer.ROI_SELECTION_WINDOW_NAME, cv2.WINDOW_NORMAL)
                        cv2.resizeWindow(VideoPlayer.ROI_SELECTION_WINDOW_NAME, (self._window_width,
                                         self._window_width))

                        cv2.imshow(VideoPlayer.ROI_SELECTION_WINDOW_NAME, init_frame)
                        gt_bbox = tuple(cv2.selectROI(VideoPlayer.ROI_SELECTION_WINDOW_NAME,
                                                      init_frame,
                                                      fromCenter=False))
                        cv2.destroyWindow(VideoPlayer.ROI_SELECTION_WINDOW_NAME)
                        self.tracker_broker.init_all_tracker(self._frame, gt_bbox)
                        # TODO if not tracking
                        self.state = States.TRACKING
                        self.video_player.start()

            if self.state == States.TRACKING:
                if self.tracker_broker.num_clients == 0:
                    self.state = States.PLAYING
                if imgui.is_key_pressed(glfw.KEY_V):
                    self.state = States.VIEWING
                    self.video_player.pause()
                    Bus.publish("stop-tracking")
                if imgui.is_key_pressed(glfw.KEY_E):
                    self.state = States.PLAYING
                    Bus.publish("stop-tracking")

                # if self._frame is not None:
                #     self.tracker_broker.send_frame_all_clients(self._frame, self._nf)
                #     all_bbox = self.tracker_broker.get_all_bbox()
                #     self._frame = Drawer.draw_bboxes(self._frame, all_bbox)

            if self.state == States.VIEWING:
                self._key_control_video()
                if imgui.is_key_pressed(glfw.KEY_E):
                    self.state = States.PLAYING

                # if self._frame is not None:
                #     all_bbox = self.tracker_broker.get_all_bbox(self._nf)
                #     self._frame = Drawer.draw_bboxes(self._frame, all_bbox)

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
        if imgui.is_key_down(glfw.KEY_RIGHT):
            self.video_player.seek_forward(5)
        if imgui.is_key_down(glfw.KEY_LEFT):
            self.video_player.seek_backward(5)

    def _new_frame(self, frame: np.ndarray, nf: int):
        self._nf = nf

        print(self.state)
        if self.state == States.PLAYING:
            self._frame = frame

        if self.state == States.TRACKING:
            t1 = time.time()
            self.tracker_broker.send_frame_all_clients(frame, nf)
            all_bbox = self.tracker_broker.get_all_bbox(self._nf)
            self._frame = Drawer.draw_bboxes(frame, all_bbox)
            t2 = time.time()

            Bus.publish("update-real-fps", int(1/(t2-t1)))

        if self.state == States.VIEWING:
            print("VIEW")
            all_bbox = self.tracker_broker.get_all_bbox(self._nf)
            self._frame = Drawer.draw_bboxes(frame, all_bbox)
