from typing import List

import imgui

from TrackerContest.gui.objects.windows import Window
from TrackerContest.gui.objects.panels import Panel
from TrackerContest.gui.objects.panels.control_panels import StreamControl, FilesControl, NetworkControl, TrackersPanel


class ControlWindow(Window):
    def __init__(self, x, y):
        super().__init__(x, y)
        self._id = "Control Panel"

        self._panels: List[Panel] = [FilesControl(), StreamControl(), NetworkControl(), TrackersPanel()]
        self._current_panel = self._panels[0]

    def _draw_buttons(self):
        imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (1, 0))

        button_width = imgui.get_content_region_available_width() / len(self._panels)

        for panel in self._panels:
            if imgui.button(panel.name, button_width):
                self._current_panel = panel

            if panel is not self._panels[-1]:
                imgui.same_line()

        imgui.pop_style_var()

    def _draw_panels(self):
        self._current_panel.draw()

    def _setting_window(self):
        imgui.set_next_window_size(self.position.x, imgui.get_io().display_size.y)
        imgui.set_next_window_position(imgui.get_io().display_size.x - self.position.x, self.position.y)

    def _begin_window(self):
        imgui.begin(self._id, False, flags=imgui.WINDOW_NO_COLLAPSE | imgui.WINDOW_NO_RESIZE)

    def _draw_content(self):
        self._draw_buttons()

        imgui.dummy(0, 2)

        self._draw_panels()
