from requests.exceptions import RequestException


class ErrorResponseException(RequestException):
    def __init__(self, message, content=None, status_code=None):
        super(ErrorResponseException, self).__init__(message)
        self.message = message
        self.content = content
        self.status_code = status_code


class LoginErrorException(ErrorResponseException):
    """
    Used when there's a known login error like invalid credentials etc.
    The message will say what the validation error is.
    """
    pass


class UnexpectedResponseException(ErrorResponseException):
    """
    Used when there's an unexpected response.
    The message will have the status_code and the content will be the response
    body.
    """


class CDMSNotFoundException(ErrorResponseException):
    pass


class CDMSUnauthorizedException(ErrorResponseException):
    pass
