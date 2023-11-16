from __future__ import annotations

import imgui

from TrackerContest.gui.objects.windows import Window

from TrackerContest.gui.utils import ImTex


class ImageWindow(Window):
    def __init__(self):
        super().__init__()

        self._uv0: imgui.Vec2 = imgui.Vec2(0, 0)
        self._uv1: imgui.Vec2 = imgui.Vec2(1, 1)

        self._image_texture = ImTex(1, 1)

    @property
    def _texture_width(self):
        return self._image_texture.get_size().x

    @property
    def _texture_height(self):
        return self._image_texture.get_size().y

    @staticmethod
    def _uv_size(window: ImageWindow) -> imgui.Vec2:
        uv_width = window._texture_width * (window._uv1[0] - window._uv0[0])
        uv_height = window._texture_height * (window._uv1[1] - window._uv0[1])
        return imgui.Vec2(uv_width, uv_height)

    @staticmethod
    def _uv_offset(window: ImageWindow) -> imgui.Vec2:
        uv_offset_x = window._uv0[0] * window._texture_width
        uv_offset_y = window._uv0[1] * window._texture_height
        return imgui.Vec2(uv_offset_x, uv_offset_y)

    @staticmethod
    def image2window(window: ImageWindow, image_x: float, image_y: float):
        uv_size = ImageWindow._uv_size(window)
        uv_offset = ImageWindow._uv_offset(window)
        window_x = (image_x - uv_offset.x) / uv_size.x * window._width
        window_y = (image_y - uv_offset.y) / uv_size.y * window._height
        return imgui.Vec2(window_x, window_y)

    @staticmethod
    def window2image(window: ImageWindow, window_x: float, window_y: float):
        uv_size = ImageWindow._uv_size(window)
        uv_offset = ImageWindow._uv_offset(window)
        image_x = window_x / window._width * uv_size.x + uv_offset.x
        image_y = window_y / window._height * uv_size.y + uv_offset.y
        return imgui.Vec2(image_x, image_y)

    @staticmethod
    def screen2image(window: ImageWindow, screen_x: float, screen_y: float):
        window_position = Window.screen2window(window, screen_x, screen_y)
        return ImageWindow.window2image(window, window_position.x, window_position.y)

    @staticmethod
    def image2screen(window: ImageWindow, image_x: float, image_y: float):
        window_position = ImageWindow.image2window(window, image_x, image_y)
        return Window.window2screen(window, window_position.x, window_position.y)

    def upload_image(self, image):
        self._init_texture(image)

    def _init_texture(self, image):
        if image.shape[1] != self._texture_width or image.shape[0] != self._texture_height:
            self._image_texture.release_tex_id()
            self._image_texture = ImTex(image.shape[1], image.shape[0])

        self._image_texture.upload_data(image.data)

    def _init_window(self):
        # display_size = imgui.get_io().display_size
        #
        # aspect_ratio_x = display_size[0] / self._texture_width
        # aspect_ratio_y = display_size[1] / self._texture_height
        #
        # self._width = self._texture_width * min(aspect_ratio_x, aspect_ratio_y)
        # self._height = self._texture_height * min(aspect_ratio_x, aspect_ratio_y)
        #
        # self._x = display_size[0] / 2 - self._width / 2
        # self._y = display_size[1] / 2 - self._height / 2

        display_size = imgui.get_io().display_size
        aspect_ratio_y = display_size[1] / self._texture_height

        self._height = self._texture_height * aspect_ratio_y
        self._width = 2 / 3 * display_size[0]
        self._x = 0
        self._y = display_size[1] / 2 - self._height / 2



    def _begin_window(self):
        imgui.set_next_window_position(self.position.x, self.position.y, imgui.ALWAYS)
        imgui.set_next_window_size(self.size.x, self.size.y)

        imgui.push_style_var(imgui.STYLE_WINDOW_PADDING, (0, 0))
        imgui.push_style_var(imgui.STYLE_WINDOW_BORDERSIZE, 0)
        imgui.begin(self._id, False, imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_SCROLLBAR |
                    imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_SCROLL_WITH_MOUSE | imgui.WINDOW_NO_BRING_TO_FRONT_ON_FOCUS)

    def _end_window(self):
        imgui.end()
        imgui.pop_style_var(2)

    def _draw_content(self):
        aspect_ratio_x = self.size.x / self._texture_width
        aspect_ratio_y = self.size.y / self._texture_height

        image_width = self._texture_width * min(aspect_ratio_x, aspect_ratio_y)
        image_height = self._texture_height * min(aspect_ratio_x, aspect_ratio_y)

        image_pos_x = self.size.x / 2 - image_width / 2
        image_pos_y = self.size.y / 2 - image_height / 2

        imgui.set_cursor_pos((image_pos_x, image_pos_y))

        imgui.image(self._image_texture.get_tex_id(), image_width, image_height,
                    (self._uv0.x, self._uv0.y), (self._uv1.x, self._uv1.y))
