class CellData:
    def __init__(self, value=None, text_id=None, cell_id=None, note_ids=None, locked=False):
        self.value = value  # actual value to display (as text)
        self.text_id = text_id
        self.cell_id = cell_id
        self.locked = locked  # locked when loading a board
        self.note_ids = note_ids
        # self.parent = None
        # self.color = '#ffffff'

    # def set_color(self, color=None) -> None:
    #     if color is None:
    #         color = self.color
    #     else:
    #         self.color = color
    #     self.parent.itemconfigure(fill=color)

    def __repr__(self):
        return str((self.value, self.text_id, self.cell_id))