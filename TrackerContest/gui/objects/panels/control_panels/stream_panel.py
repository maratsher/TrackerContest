from typing import Dict, Tuple, AnyStr

import imgui

from TrackerContest.core import Bus
from TrackerContest.gui.objects.panels import Panel


class StreamControl(Panel):
    def __init__(self, name: str = "Stream"):
        super().__init__(name)

        self._in_tracking = True
        self._trackers: Dict = {}

        Bus.subscribe("set-init-fps", self.fps)
        Bus.subscribe("connected-new-tracker", self._connected_new_tracker)
        Bus.subscribe("remove-tracker", self._removed_tracker)
        Bus.subscribe("update-tracker-fps", self._update_fps)
        Bus.subscribe("update-real-fps", self._update_real_fps)

        self._fps = 0
        self._real_fps = 0
        self._brightness = 1

    def fps(self, fps: int):
        self._fps = fps

    def _draw_content(self):
        imgui.set_window_font_scale(1.5)
        imgui.dummy(5, 5)
        imgui.text("Original FPS: ")
        imgui.same_line()
        changed, self._fps = imgui.slider_int("##fps", self._fps, 1, 100)
        if changed:
            Bus.publish("set-fps", self._fps)

        imgui.set_window_font_scale(1.7)
        imgui.dummy(5, 5)
        imgui.text(f"Real FPS: {self._real_fps}")

        imgui.dummy(5, 5)
        imgui.set_window_font_scale(2)
        imgui.text("Connected trackers:")
        imgui.set_window_font_scale(1.5)
        for tracker_name in self._trackers.keys():
            color: Tuple = self._trackers.get(tracker_name).get('color')
            address: AnyStr = self._trackers.get(tracker_name).get('address')
            tracker_fps: int = self._trackers.get(tracker_name).get("fps")
            activated: bool = self._trackers.get(tracker_name).get("activated")
            imgui.text_colored(f"{tracker_name} (fps: {tracker_fps})", *color, self._brightness)
            imgui.same_line()
            changed, self._trackers[tracker_name]["selected"] = imgui.checkbox(f"##{tracker_name}{address}",
                                                                               self._trackers.get(tracker_name).get(
                                                                                   "selected"))

            if changed:
                Bus.publish("changed-draw-mode", tracker_name,
                            self._trackers[tracker_name]["selected"])

    def _connected_new_tracker(self, name: str, color: tuple, address: str):
        self._trackers[name] = {"color": color, "address": address, "selected": True, "activated": True, "fps": 0}

    def _removed_tracker(self, name: str):
        self._trackers.pop(name)

    def _update_fps(self, name: str, fps: int):
        self._trackers[name]["fps"] = fps

    def _update_real_fps(self, fps: int):
        self._real_fps = fps
