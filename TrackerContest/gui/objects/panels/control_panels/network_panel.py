import imgui

from TrackerContest.gui.objects.panels import Panel

from TrackerContest.core import Bus

class NetworkControl(Panel):
    def __init__(self, name: str = "Network"):
        super().__init__(name)

        self._socket_path = "/tmp/server_socket"

    def _draw_content(self):
        pass
        # imgui.dummy(5, 5)
        # imgui.set_window_font_scale(1.5)
        # imgui.text("IPC SOCKET:")
        # imgui.same_line()
        # changed, self._socket_path = imgui.input_text("##host", self._socket_path)
        #
        # if changed:
        #     Bus.publish("changed-address-server", self._socket_path)
        #
        # if imgui.button("Restart"):
        #     Bus.publish("restart-server")
