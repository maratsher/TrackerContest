from typing import Optional

import imgui

from TrackerContest.gui.objects import GUIObject


class Panel(GUIObject):
    def __init__(self, name: str):
        super().__init__()
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def _begin_child(self):
        imgui.begin_child(self._id, imgui.get_content_region_available_width(), 0, False)

    def _draw_content(self):
        pass

    def _end_child(self):
        imgui.end_child()

    def draw(self):
        self._begin_child()

        self._draw_content()

        self._end_child()
