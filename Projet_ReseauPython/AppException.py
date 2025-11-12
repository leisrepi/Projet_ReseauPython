class TooManyMachinesException(Exception):
    def __init__(self, __message):
        self.__message = __message
        super().__init__(self.__message)

class MaskNotInRangeException(Exception):
    def __init__(self, __message):
        self.__message = __message
        super().__init__(self.__message)

class InvalidMaskException(Exception):
    def __init__(self, __message):
        self.__message = __message
        super().__init__(self.__message)

class UserAlreadyInDBException(Exception):
    def __init__(self):
        self.__message = "L'utilisateur existe déja dans la base de données."
        super().__init__(self.__message)

class SNMaskErrorException(Exception):
    def __init__(self):
        self.__message = "Le masque de sous-réseaux est erroné."
        super().__init__(self.__message)

class NotAuthentifyException(Exception):
    def __init__(self):
        self.__message = "L'authentification a échoué, la session est échue."
        super().__init__(self.__message)