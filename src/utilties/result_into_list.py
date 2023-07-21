import dataclasses

from sqlalchemy import Result


class ResultIntoList:
    def __init__(self, result_proxy: Result):
        self.result_proxy: Result = result_proxy

    def parse(self):
        # Return sqlalchemy result

        for row in self.result_proxy:
            yield row._asdict()
