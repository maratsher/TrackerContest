from typing import Dict, List, Tuple, AnyStr
import imgui
import numpy as np

from TrackerContest.gui.objects.panels import Panel

from TrackerContest.core import Bus


class TrackersPanel(Panel):
    def __init__(self, name: str = "Trackers"):
        super().__init__(name)

        self._in_tracking = False
        self._trackers: Dict = {}
        Bus.subscribe("connected-new-tracker", self._connected_new_tracker)

    def _draw_content(self):
        imgui.set_window_font_scale(2)
        imgui.text("Подключенные трекеры:")
        imgui.set_window_font_scale(1.5)
        for tracker_name in self._trackers.keys():
            color: Tuple = self._trackers.get(tracker_name).get('color')
            address: AnyStr = self._trackers.get(tracker_name).get('address')
            imgui.text_colored(f"{tracker_name} ({address})", *color, 0.5)
            if imgui.is_item_clicked() and not self._in_tracking:
                print(f'PRESSEF {address}')
            imgui.same_line()
            changed, self._trackers[tracker_name]["selected"] = imgui.checkbox(f"##{tracker_name}{address}",
                                                                                       self._trackers.get(tracker_name).get("selected"))

            if changed:
                Bus.publish("changed-draw-mode", tracker_name,
                                                 self._trackers[tracker_name]["selected"])

    def _connected_new_tracker(self, name: str, color: tuple, address: str):
        self._trackers[name] = {"color": color, "address": address, "selected": True, "activated": True}
