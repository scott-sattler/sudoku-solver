class CellData:
    """
        note_values:
        OFF: 0.
        ON: i at i.
    """
    def __init__(self, value=None, text_id=None, cell_id=None, note_ids=None, note_values=None, locked=False):
        self.value = value  # actual value to display (as text)
        self.text_id = text_id
        self.cell_id = cell_id
        self.locked = locked  # locked when loading a board
        self.note_ids = note_ids
        self.note_values = note_values  # one-indexed

    def init_notes(self):
        self.note_values = [i for i in range(10)]

    def note_enable(self, val):
        if self.note_values is None:
            self.init_notes()
        self.note_values[val] = val

    def note_disable(self, val):
        if self.note_values is not None:
            self.note_values[val] = 0

    def __repr__(self):
        info = (f"value: {self.value}\n"
                f"text_id : {self.text_id}\n"
                f"cell_id : {self.cell_id}\n"
                f"locked : {self.locked}\n"
                f"note_ids : {self.note_ids}\n"
                f"note_values : {self.note_values}\n")
        return info


class StateManager:
    CURRENT = 'current'
    PREVIOUS = 'previous'
    # INPUT_RESET = 'input_reset'
    WELCOME = 'welcome'
    BOARD_SELECTION = 'board_selection'
    BOARD_LOADED = 'board_loaded'
    # BOARD_INPUT = 'baord_input'
    DOUBLE_CLICK_HIGHLIGHT = 'double_click_highlight'
    NUMBER_SELECTOR = 'number_selector'
    SOLVING_BOARD = 'solving_board'
    # ABORTED = 'aborted'
    VALIDATED = 'validated'

    all_states = [
        CURRENT,
        PREVIOUS,
        # INPUT_RESET,
        WELCOME,
        BOARD_SELECTION,
        BOARD_LOADED,
        # BOARD_INPUT,
        DOUBLE_CLICK_HIGHLIGHT,
        NUMBER_SELECTOR,
        SOLVING_BOARD,
        # ABORTED,
        VALIDATED,
    ]

    def __init__(self):
        self.state_manager: dict[str, bool | None | str] = dict()
        self.welcome_state()

    def welcome_state(self):
        for each_state in self.all_states:
            self.state_manager[each_state] = False
        self.state_manager[self.CURRENT] = self.WELCOME
        self.state_manager[self.PREVIOUS] = None
        self.state_manager[self.WELCOME] = True

    def get_current(self):
        return self.state_manager[self.CURRENT]

    def get_previous(self):
        return self.state_manager[self.PREVIOUS]

    def update_previous(self):
        self.state_manager[self.PREVIOUS] = self.state_manager[self.CURRENT]
        previous_state = self.state_manager[self.PREVIOUS]
        self.state_manager[previous_state] = False

    def update_current(self, to_state):
        self.state_manager[self.CURRENT] = to_state
        self.state_manager[to_state] = True

    def revert_state(self):
        prev = self.state_manager[self.PREVIOUS]
        curr = self.state_manager[self.CURRENT]
        self.state_manager[prev] = True
        self.state_manager[curr] = False
        self.state_manager[self.PREVIOUS] = curr
        self.state_manager[self.CURRENT] = prev

    def board_selector_enable(self):
        self.update_previous()
        self.update_current(self.BOARD_SELECTION)

    def board_selector_disable(self):
        if self.get_current() == self.BOARD_SELECTION:
            self.revert_state()

    def board_loaded(self):
        self.update_previous()
        self.update_current(self.BOARD_LOADED)

    def double_click_highlight(self):
        self.update_previous()
        self.update_current(self.DOUBLE_CLICK_HIGHLIGHT)

    def double_click_restore(self):
        self.revert_state()

    # def board_input(self):
    #     self.update_previous()
    #     self.update_current(self.BOARD_INPUT)
    #     self.state_manager[self.BOARD_INPUT] = True

    def solving_board_begin(self):
        self.update_previous()
        self.update_current(self.SOLVING_BOARD)

    def solving_board_complete(self):
        if self.get_current() == self.SOLVING_BOARD:
            self.revert_state()

    def validate_board(self):
        if self.get_current() != self.VALIDATED:
            self.update_previous()
            self.update_current(self.VALIDATED)

    # todo: mostly just curr/prev strings...
