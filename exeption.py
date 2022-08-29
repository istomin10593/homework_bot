
class HTTPStatusError(Exception):
    def __init__(self, response):
        message = (
            f'Not available ENDPOINT:{response.url}.'
            f'Status code: {response.status_code}'
        )
        super().__init__(message)
