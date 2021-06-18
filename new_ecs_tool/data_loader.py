class DataLoader:
    def __init__(self, click_params, data_fetcher, *args):
        self.click_params = click_params
        self.data_fetcher = data_fetcher
        self.args = args
        self.data = self.load()

    def load(self):
        return {
            "click_params": self.click_params,
            "fetcher": self.data_fetcher(click_params=self.click_params, *self.args)
        }
