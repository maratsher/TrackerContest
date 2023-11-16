import imgui

from TrackerContest.gui.objects.panels import Panel

from TrackerContest.core import Bus

class StreamControl(Panel):
    def __init__(self, name: str = "Stream"):
        super().__init__(name)

        Bus.subscribe("set-init-fps", self.fps)

        self._fps = 0

    def fps(self, fps: int):
        self._fps = fps

    def _draw_content(self):
        imgui.set_window_font_scale(1.5)
        imgui.text("FPS: ")
        imgui.same_line()
        changed, self._fps = imgui.slider_int("##fps", self._fps, 1, 100)
        if changed:
            Bus.publish("set-fps", self._fps)