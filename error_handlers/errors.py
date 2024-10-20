class CustomError(Exception):
    pass


class DatabaseConnectionError(CustomError):
    def __init__(self, message="Error with connection to db"):
        self.message = message
        super().__init__(self.message)


class Error404(CustomError):
    def __init__(self, message="Error with status code 404"):
        self.message = message
        super().__init__(self.message)


class Error409(CustomError):
    def __init__(self, message="Error with status code 409"):
        self.message = message
        super().__init__(self.message)


class ZeroEmailError(CustomError):
    def __int__(self, message="You cant create account without email"):
        self.message = message
        super().__init__(self.message)


class ZeroPassError(CustomError):
    def __int__(self, message="You cant create account without password"):
        self.message = message
        super().__init__(self.message)


class CompanyNameError(CustomError):
    def __init__(self, message="You cant create company without name"):
        self.message = message
        super().__init__(self.message)


class FilterError(CustomError):
    id: int

    def __init__(self, tg_id, message="We cant find company relevant for you"):
        self.id = tg_id
        self.message = message
        super().__init__(self.message)


class ContentError(CustomError):
    def __init__(self, message="GPT response is incorrect"):
        self.message = message
        super().__init__(self.message)


class ParseError(CustomError):
    def __init__(self, message="Error with processing GPT answer"):
        self.message = message
        super().__init__(self.message)
