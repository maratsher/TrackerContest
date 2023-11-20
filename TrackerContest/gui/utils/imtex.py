import enum

import OpenGL.GL as gl

import imgui


class ImTex:
    class TexFormat(enum.Enum):
        RGB = gl.GL_RGB
        RGBA = gl.GL_RGBA
        BGR = gl.GL_BGR
        BGRA = gl.GL_BGRA

    def __init__(self, width: int, height: int,
                 src_format: TexFormat = TexFormat.RGB, dst_format: TexFormat = TexFormat.RGB, data=None):

        self.__tex_size: imgui.Vec2 = imgui.Vec2(width, height)

        self.__tex_id: gl.GLuint64 = gl.glGenTextures(1)

        gl.glBindTexture(gl.GL_TEXTURE_2D, self.__tex_id)
        gl.glPixelStorei(gl.GL_UNPACK_ROW_LENGTH, 0)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, src_format.value, width, height, 0, dst_format.value,
                        gl.GL_UNSIGNED_BYTE, data)

        self.check_errors()

    def release_tex_id(self):
        gl.glDeleteTextures(1, self.__tex_id)

    def upload_data(self, data, tex_format: TexFormat = TexFormat.RGB):
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.__tex_id)
        gl.glTexSubImage2D(gl.GL_TEXTURE_2D, 0, 0, 0, self.__tex_size.x, self.__tex_size.y,
                           tex_format.value, gl.GL_UNSIGNED_BYTE, data)
        self.check_errors()

    def get_tex_id(self) -> gl.GLuint64:
        return self.__tex_id

    def get_size(self) -> imgui.Vec2:
        return self.__tex_size

    @staticmethod
    def check_errors():
        match gl.glGetError():
            case gl.GL_INVALID_ENUM:
                raise ValueError("Invalid enum")
            case gl.GL_INVALID_VALUE:
                raise ValueError("Invalid value")
            case gl.GL_INVALID_OPERATION:
                raise ValueError("Invalid operation")
            case gl.GL_OUT_OF_MEMORY:
                raise MemoryError("Out of memory")
