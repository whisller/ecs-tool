from rich.layout import Layout


def make_layout():
    layout = Layout(name="root")
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=7),
    )

    return layout


class Ui:
    def __init__(self, layout, data_loader):
        self.layout = layout
        self.data_loader = data_loader

    def refresh(self):
        return self.layout(make_layout()).load(self.data_loader.load())
