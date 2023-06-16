from sqlalchemy import Result


class ResultIntoList:
    def __init__(self, result_proxy: Result):
        self.result_proxy = result_proxy

    def parse(self):
        result = []
        for row in self.result_proxy:
            yield row._asdict()
        # return result
