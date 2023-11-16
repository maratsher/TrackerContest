import imgui

from TrackerContest.gui.objects.panels import Panel

from TrackerContest.core import Bus

class NetworkControl(Panel):
    def __init__(self, name: str = "Network"):
        super().__init__(name)

        self._host = "127.0.0.1"
        self._port = "8080"

    def _draw_content(self):
        imgui.dummy(5, 5)
        imgui.set_window_font_scale(1.5)
        imgui.text("HOST:")
        imgui.same_line()
        changed, self._host = imgui.input_text("##host", self._host)
        imgui.text("PORT:")
        imgui.same_line()
        changed, self._port = imgui.input_text("##port", self._port)

        if changed:
            Bus.publish("changed-address-server", (self._host, self._port))
