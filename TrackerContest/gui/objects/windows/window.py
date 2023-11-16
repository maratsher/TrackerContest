from __future__ import annotations

import imgui

from TrackerContest.gui.objects import GUIObject


class Window(GUIObject):
    def __init__(self, x=0, y=0, window_width=300, window_height=200, flag=imgui.ALWAYS):
        super().__init__()
        self._x = x
        self._y = y

        self._flag = flag

        self._width = window_width
        self._height = window_height

    @property
    def position(self):
        return imgui.Vec2(self._x, self._y)

    @property
    def size(self):
        return imgui.Vec2(self._width, self._height)

    @staticmethod
    def screen2window(window: Window, screen_x: float, screen_y: float):
        return imgui.Vec2(screen_x - window._x, screen_y - window._y)

    @staticmethod
    def window2screen(window: Window, window_x: float, window_y: float):
        return imgui.Vec2(window_x + window._x, window_y + window._y)

    def _draw_content(self):
        pass

    def _draw_overlay(self):
        pass

    def _setting_window(self):
        imgui.set_next_window_size(self.size.x, self.size.y, self._flag)
        imgui.set_next_window_position(self.position.x, self.position.y, self._flag)

    def _begin_window(self):
        imgui.begin(self._id)

    def _end_window(self):
        imgui.end()

    def _init_window(self):
        pass

    def _handle_input(self):
        pass

    def draw(self):
        self._init_window()

        self._setting_window()

        self._begin_window()

        self._draw_content()

        self._draw_overlay()

        self._handle_input()

        self._end_window()


if __name__ == "__main__":
    pass
