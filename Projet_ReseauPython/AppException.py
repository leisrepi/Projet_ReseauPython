class TooManyMachinesException(Exception):
    def __init__(self, __message):
        self.__message = __message
        super().__init__(self.__message)

class InvalidMaskException(Exception):
    def __init__(self, __message):
        self.__message = __message
        super().__init__(self.__message)