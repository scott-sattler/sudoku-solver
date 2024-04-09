class CellData:
    def __init__(self, value=None, text_id=None, canvas_id=None, locked=False):
        self.value = value  # actual value to display (as text)
        self.text_id = text_id
        self.canvas_id = canvas_id
        self.locked = locked  # locked when loading a board
        # self.parent = None
        # self.color = '#ffffff'

    # def set_color(self, color=None) -> None:
    #     if color is None:
    #         color = self.color
    #     else:
    #         self.color = color
    #     self.parent.itemconfigure(fill=color)

    def __repr__(self):
        return str((self.value, self.text_id, self.canvas_id))