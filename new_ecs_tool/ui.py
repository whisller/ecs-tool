from new_ecs_tool.base_layout import make_layout


class Ui:
    def __init__(self, layout, data_loader):
        self.layout = layout
        self.data_loader = data_loader

    def refresh(self):
        return self.layout(make_layout()).refresh(self.data_loader.load())
