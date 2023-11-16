from __future__ import annotations

import imgui
import numpy as np

from .image_window import ImageWindow


class ZoomImageWindow(ImageWindow):
    def __init__(self):
        super().__init__()

        self._is_image_hovering = False

        self._min_scale = 1
        self._max_scale = 16

        self._scale_speed = .1

        self._current_scale = self._min_scale

        self._is_draw_navigation = True

    def __clip_uv(self):
        # UV edges offset calculation
        x_offset = -min(0, self._uv0.x) or min(0, 1 - self._uv1.x)
        y_offset = -min(0, self._uv0.y) or min(0, 1 - self._uv1.y)

        self._uv0 = imgui.Vec2(self._uv0.x + x_offset, self._uv0.y + y_offset)
        self._uv1 = imgui.Vec2(self._uv1.x + x_offset, self._uv1.y + y_offset)

    def __touch_moving(self):
        if not imgui.is_mouse_dragging(0):
            return

        drag_delta = imgui.get_mouse_drag_delta()

        x_offset = -(drag_delta.x / self.size.x / self._current_scale)
        y_offset = -(drag_delta.y / self.size.y / self._current_scale)

        self._uv0 = imgui.Vec2(self._uv0.x + x_offset, self._uv0.y + y_offset)
        self._uv1 = imgui.Vec2(self._uv1.x + x_offset, self._uv1.y + y_offset)

        self.__clip_uv()

        imgui.reset_mouse_drag_delta()

    def __touch_zooming(self):
        mouse_wheel = imgui.get_io().mouse_wheel
        if not mouse_wheel:
            return

        # Calculate mouse position
        anchor_pos_screen = imgui.get_mouse_pos()
        anchor_pos_texture = self.screen2image(self, anchor_pos_screen.x, anchor_pos_screen.y)

        anchor_pos_texture_plane = imgui.Vec2(anchor_pos_texture.x / self._texture_width,
                                              anchor_pos_texture.y / self._texture_height)

        anchor_pos_uv_plane = imgui.Vec2((anchor_pos_texture_plane[0] - self._uv0[0]) / (self._uv1[0] - self._uv0[0]),
                                         (anchor_pos_texture_plane[1] - self._uv0[1]) / (self._uv1[1] - self._uv0[1]))

        # Scale calculation
        self._current_scale = self._current_scale + self._current_scale * self._scale_speed * mouse_wheel
        self._current_scale = np.clip(self._current_scale, self._min_scale, self._max_scale)

        # UV calculation
        uv_scale = 1 / self._current_scale

        self._uv0 = imgui.Vec2(anchor_pos_texture_plane.x - anchor_pos_uv_plane.x * uv_scale,
                               anchor_pos_texture_plane.y - anchor_pos_uv_plane.y * uv_scale)
        self._uv1 = imgui.Vec2(self._uv0.x + uv_scale, self._uv0.y + uv_scale)

        self.__clip_uv()

    def _draw_content(self):
        super()._draw_content()

        self._is_image_hovering = imgui.is_item_hovered()

    def _handle_input(self):
        if not self._is_image_hovering:
            return

        self.__touch_moving()
        self.__touch_zooming()

    def _draw_overlay(self):
        if not self._is_draw_navigation or self._current_scale == self._min_scale:
            return

        draw_list = imgui.get_window_draw_list()

        def draw_rect(p1: imgui.Vec2, p2: imgui.Vec2, color_rgb: tuple[float, float, float]):
            foreground_color = imgui.get_color_u32_rgba(color_rgb[0], color_rgb[1], color_rgb[2], 1.0)
            background_color = imgui.get_color_u32_rgba(color_rgb[0], color_rgb[1], color_rgb[2], 0.3)
            draw_list.add_rect_filled(p1.x, p1.y, p2.x, p2.y, background_color)
            draw_list.add_rect(p1.x, p1.y, p2.x, p2.y, foreground_color, thickness=1)

        pos = imgui.Vec2(self.position.x + self.size.x * .01, self.position.y + self.size.y * .01)
        size = imgui.Vec2(self._width * .2, self._height * .2)

        draw_rect(p1=pos,
                  p2=imgui.Vec2(pos.x + size.x, pos.y + size.y),
                  color_rgb=(.3, .3, .3))
        draw_rect(p1=imgui.Vec2(pos.x + self._uv0.x * size.x, pos.y + self._uv0.y * size.y),
                  p2=imgui.Vec2(pos.x + self._uv1.x * size.x, pos.y + self._uv1.y * size.y),
                  color_rgb=(0, 0, .5))
