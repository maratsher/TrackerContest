import glfw
import imgui

from TrackerContest.gui import ImGuiApp
from TrackerContest.gui.objects.windows.image_windows import ZoomImageWindow
from TrackerContest.gui.objects.windows.control_windows import ControlWindow

from TrackerContest.core.video import VideoPlayer
from TrackerContest.core.network import TrackerBroker
from TrackerContest.core.utils import Drawer
from TrackerContest.core import Bus


class OmenApp(ImGuiApp):
    def __init__(self, window_width, window_height, fullscreen):
        super().__init__(window_width, window_height, fullscreen)

        self._image_window = ZoomImageWindow()
        self._camera_window = ControlWindow(x=420, y=0)

        self.video_player = VideoPlayer()
        Bus.subscribe("init-video", self.video_player.init_video)

        self.tracker_broker = TrackerBroker()
        Bus.subscribe("changed-address-server", self.tracker_broker.server_address)

    def _terminate(self):
        super()._terminate()
        self.video_player.stop()

    def _update(self):
        super()._update()

    def draw_content(self):
        if imgui.is_key_pressed(glfw.KEY_SPACE):
            if self.video_player.on_pause:
                self.video_player.start()
            else:
                self.video_player.pause()
        elif imgui.is_key_pressed(glfw.KEY_R):
            self.video_player.restart()
        elif imgui.is_key_pressed(glfw.KEY_RIGHT):
            self.video_player.seek_forward(2)
        elif imgui.is_key_pressed(glfw.KEY_LEFT):
            self.video_player.seek_backward(2)

        frame = self.video_player.get_frame()
        if frame is not None:
            self.tracker_broker.send_frame_all_clients(frame)
            all_bbox = self.tracker_broker.get_all_bbox()
            frame = Drawer.draw_bboxes(frame, all_bbox)
            self._image_window.upload_image(frame)
        self._image_window.draw()
        self._camera_window.draw()


