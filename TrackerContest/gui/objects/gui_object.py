import itertools


class GUIObject:
    __id_iter = itertools.count()

    def __init__(self):
        self._id = str(next(self.__id_iter))
