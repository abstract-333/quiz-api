from starlette.requests import Request
from starlette.responses import Response


class ResponseRequestDependency:
    def __init__(self, request: Request, response: Response):
        self.request = request
        self.response = response

