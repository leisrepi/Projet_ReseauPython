class TooManyMachinesException(Exception):
    def __init__(self, __message):
        self.__message = __message
        super().__init__(self.__message)

class InvalidMaskException(Exception):
    def __init__(self, __message):
        self.__message = __message
        super().__init__(self.__message)

class UserAlreadyInDBException(Exception):
    def __init__(self, __message):
        self.__message = __message
        super().__init__(self.__message)

class SNMaskErrorException(Exception):
    def __init__(self, __message):
        self.__message = __message
        super().__init__(self.__message)

class NotAuthentifyException(Exception):
    def __init__(self, __message):
        self.__message = __message
        super().__init__(self.__message)