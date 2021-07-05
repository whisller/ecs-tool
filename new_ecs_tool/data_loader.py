from dataclasses import dataclass

from .context import ContextObject


@dataclass
class Data:
    click_params: dict
    fetcher: dict


class DataLoader:
    def __init__(self, context: ContextObject, click_params, data_fetcher):
        self.context = context
        self.click_params = click_params
        self.data_fetcher = data_fetcher
        self.data = self.load()

    def load(self):
        return Data(
            self.click_params, self.data_fetcher(self.context, self.click_params)
        )
