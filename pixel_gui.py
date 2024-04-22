import tkinter as tk
import tempfile
from class_cell_data import CellData


ICON = (b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x08\x00h\x05\x00\x00'
        b'\x16\x00\x00\x00(\x00\x00\x00\x10\x00\x00\x00 \x00\x00\x00\x01\x00'
        b'\x08\x00\x00\x00\x00\x00@\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        b'\x00\x01\x00\x00\x00\x01') + b'\x00' * 1282 + b'\xff' * 64

_, ICON_PATH = tempfile.mkstemp()
with open(ICON_PATH, 'wb') as icon_file:
    icon_file.write(ICON)


class PixelGUI(tk.Tk):
    BOARD_CELLS = 9
    CELL_SIZE = 50
    DEFAULT_COLOR = '#ffffff'
    BUTTON_COLOR = DEFAULT_COLOR
    BUTTON_HOVER_COLOR = '#dfdfdf'
    DEFAULT_CELL_COLOR = DEFAULT_COLOR
    SELECT_HIGHLIGHT_COLOR = '#d3d3d3'
    LOCKED_CELL_FILL_COLOR = '#eeeeee'
    NOTE_COLOR = '#808080'

    def __init__(self, easy_clue_size, medium_clue_size, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.container = tk.Frame(self)
        self.container.config(background=self.DEFAULT_COLOR)
        self.container.pack(side="top", fill="both", expand=True)

        self.title('')
        self.iconbitmap(default=ICON_PATH)
        # self.iconbitmap(default='sudoku.ico')
        self.resizable(width=False, height=False)
        self.config(background="#ffffff")  # white

        self.board_font = "fixedsys"  # 12, 18, 24, 34... sizes... 40 is different font... 45 resumes?
        self.font_size = int(12 / 25.000 * self.CELL_SIZE)  # 24 @ CELL_SIZE 50

        self.title_text = 'SUDOKU SOLVER'  # todo: rename
        # self.title_text = 'SUDOKU PLAYER'  # todo: rename

        self.title_container = None
        self.title_label = None

        self.play_board_container = None
        self.play_board = None

        self.control_panel_container = None
        self.solve_button = None
        self.select_button = None
        self.verify_button = None

        self.num_selector_popup = None  # todo: deprecated

        self.board_input_panel_container = None
        self.number_panel_container = None
        self.notes_panel_container = None
        self.number_buttons = None
        self.note_buttons = None

        self.cell_colors = False

        self.easy_clue_size = easy_clue_size
        self.medium_clue_size = medium_clue_size

        self.select_board_menu_container = None
        self.empty_board_button = None
        self.easy_board_button = None
        self.hard_board_button = None
        self.random_easy_board_button = None
        self.random_medium_board_button = None
        self.random_pick_17_board_button = None

        self.validation_message = None

        self.board_index_lookup = dict()  # lookup from tk id
        self.num_selector_lookup = dict()  # lookup from tk id

        """ primary data structure """
        self.board_gui_data = [[CellData() for _ in range(9)] for __ in range(9)]

        self.offset = 5  # cosmetic offset
        self.dynamic_size = self.BOARD_CELLS * self.CELL_SIZE
        self.play_board_width = self.dynamic_size + self.offset * 2
        self.play_board_height = self.dynamic_size + self.offset * 2

        self.fill_count = 0  # allows cycling; current only in debug keybind
        '''            red        green      blue       yellow     grey       cyan       magenta    orange     purple  '''  # noqa
        self.fill = ['#FF3333', '#33FF33', '#3333FF', '#FFFF33', '#777777', '#33FFFF', '#FF33FF', '#FF9933', '#8833FF']  # noqa

        self.welcome_message = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            ['S', 'E', 'L', 'E', 'C', 'T', 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            ['Y', 'O', 'U', 'R', 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            ['B', 'O', 'A', 'R', 'D', 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            ['T', 'O', 0, 'B', 'E', 'G', 'I', 'N', 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]

    def load_all_boards(self):
        all_boards = [
            self.empty_board_button,
            self.easy_board_button,
            self.hard_board_button,
            self.random_easy_board_button,
            self.random_medium_board_button,
            self.random_pick_17_board_button,
        ]
        return all_boards

    def initialize_title(self):
        self.title_container = tk.Canvas(self.container)
        self.title_container.config(borderwidth=0, highlightthickness=0)
        self.title_container.pack()

        self.title_label = tk.Label(self.title_container)
        self.title_label.config(
            text=self.title_text,
            font=(self.board_font, self.font_size * 2),
            bg=self.DEFAULT_COLOR,
            padx=20)
        self.title_label.pack()

    def initialize_play_board(self):
        """
        - create board
        - create board lines
        - initialize (populate) board_gui_data matrix
            create square cell, text box, and notes for each cell
        """
        self.play_board_container = tk.Frame(self.container)
        self.play_board_container.config(bg=self.DEFAULT_COLOR)
        self.play_board_container.pack(after=self.title_container)

        self.play_board = tk.Canvas(self.play_board_container)
        self.play_board.config(borderwidth=0, highlightthickness=0)
        self.play_board.config(
            height=self.play_board_height,
            width=self.play_board_width,
            bg=self.DEFAULT_COLOR)
        self.play_board.pack(pady=(10, 10))

        board_size = len(self.board_gui_data)

        font_size = self.font_size
        cell_size = self.CELL_SIZE
        offset = self.offset
        cbw = self.play_board.winfo_reqwidth()
        cbh = self.play_board.winfo_reqheight()

        # create lines
        for x_shift in range(board_size - 1):
            if (x_shift + 1) % 3 != 0:  # minor lines
                x_0 = (x_shift + 1) * cell_size + offset
                x_1 = (x_shift + 1) * cell_size + offset
                y_0 = 0 + offset
                y_1 = cbh - offset
                width = 1
            else:  # major lines
                x_0 = (x_shift + 1) * cell_size + offset
                x_1 = (x_shift + 1) * cell_size + offset
                y_0 = 0
                y_1 = cbh
                width = 3
            self.play_board.create_line(x_0, y_0, x_1, y_1, width=width)

        for y_shift in range(board_size - 1):
            if (y_shift + 1) % 3 != 0:  # minor lines
                x_0 = 0 + offset
                x_1 = cbh - offset
                y_0 = (y_shift + 1) * cell_size + offset
                y_1 = (y_shift + 1) * cell_size + offset
                width = 1
            else:  # major lines
                x_0 = 0
                x_1 = cbh
                y_0 = (y_shift + 1) * cell_size + offset
                y_1 = (y_shift + 1) * cell_size + offset
                width = 3
            self.play_board.create_line(x_0, y_0, x_1, y_1, width=width)

        # initialize board_gui_data matrix
        # creates canvas and text box for each cell
        for i in range(len(self.board_gui_data)):
            for j in range(len(self.board_gui_data[0])):
                cell_id = self.play_board.create_rectangle(
                    j * 50 + self.offset,
                    i * 50 + self.offset,
                    (j + 1) * 50 + self.offset,
                    (i + 1) * 50 + self.offset,
                    width=0,
                    fill=self.DEFAULT_CELL_COLOR,
                    tags="cell",
                )

                txt_id = self.play_board.create_text(
                    cell_size / 2 + (j * cell_size) + 4,
                    cell_size / 2 + (i * cell_size) + 4,
                    font=(self.board_font, font_size),
                    text='',
                    tags="cell",
                )

                note_ids = ['one-indexed']
                mid_i = cell_size / 2 + (j * cell_size) + offset
                mid_j = cell_size / 2 + (i * cell_size) + offset
                for p in range(3):
                    for q in range(3):
                        note_id = self.play_board.create_text(
                            mid_i - 14 + (q * 14),  # 14 * 3 = 42 => 8px/2 border
                            mid_j - 14 + (p * 14),  # forced int precision
                            font=(self.board_font, 8),
                            text=f'{(3 * p) + q + 1}',
                            fill=self.NOTE_COLOR,  # '#808080'
                            tags='note',
                        )
                        note_ids.append(note_id)

                self.play_board.lower(cell_id)
                self.board_gui_data[i][j].cell_id = cell_id
                self.board_gui_data[i][j].text_id = txt_id
                self.board_gui_data[i][j].note_ids = note_ids
                for id_ in note_ids:
                    self.play_board.itemconfig(id_, state=tk.HIDDEN)
                    self.board_index_lookup[id_] = (i, j)

                self.board_index_lookup[txt_id] = (i, j)
                self.board_index_lookup[cell_id] = (i, j)

    # todo: deprecated
    def initialize_num_selector_popup(self):
        cell_size = self.CELL_SIZE
        width = cell_size * 3
        height = cell_size * 3
        border_width = 3
        rect_b_width = 2

        self.num_selector_popup = tk.Canvas(self.play_board)
        self.num_selector_popup.config(
            width=width,
            height=height,
            bg=self.DEFAULT_COLOR,
            borderwidth=border_width,
            highlightthickness=0)
        self.num_selector_popup.place(relx=0, rely=0)
        self.num_selector_popup["state"] = tk.DISABLED
        self.num_selector_popup.place_forget()

        for i in range(3):
            for j in range(3):
                num = (i * 3) + (j + 1)
                color = self.fill[num - 1] if self.cell_colors else self.DEFAULT_CELL_COLOR

                cell_id = self.num_selector_popup.create_rectangle(
                    j * (width / 3) + border_width + rect_b_width,
                    i * (width / 3) + border_width + rect_b_width,
                    j * (width / 3) + cell_size + border_width / 3,
                    i * (width / 3) + cell_size + border_width / 3,
                    width=rect_b_width, fill=color,
                    tags=('num', 'backdrop'),
                )
                self.num_selector_lookup[cell_id] = num

                text_id = self.num_selector_popup.create_text(
                    j * (width / 3) + (border_width + rect_b_width + cell_size) / 2,
                    i * (width / 3) + (border_width + rect_b_width + cell_size) / 2,
                    font=(self.board_font, self.font_size),
                    text=num,
                    tags='num',
                )
                self.num_selector_lookup[text_id] = num

    def initialize_control_panel(self):
        """ these buttons differ from board select menu buttons """
        def formatted_button(master, text, f_scale):
            # font_size = int(self.font_size * f_scale)
            font_size = int(24)  # 'fixedsys' fixed at 24 until 34
            button_color = self.BUTTON_COLOR
            button = tk.Label(master)
            button.config(text=text, anchor=tk.CENTER)
            button.config(font=(self.board_font, font_size))
            button.config(bg=button_color, borderwidth=0)
            button.config(width=8)
            return button

        # note: Canvas has useful options and functionality versus Frame
        self.control_panel_container = tk.Frame(self.container)
        self.control_panel_container.config(highlightthickness=0)
        self.control_panel_container.config(
            width=self.play_board.winfo_reqwidth() + 40,
            # width=self.title_container.winfo_reqwidth(),
            height=self.CELL_SIZE,
            bg=self.DEFAULT_COLOR)
        self.control_panel_container.pack(fill=tk.BOTH, side=tk.BOTTOM, pady=(5, 5))

        # solve, verify, and select buttons
        c_p_c = self.control_panel_container  # buttons parent
        foo = tk.Frame(c_p_c, bg=self.DEFAULT_COLOR)
        foo.place(relx=.5, rely=.5, anchor=tk.CENTER)

        f_scale = 1  # 'fixedsys' fixed at 24 until 34

        self.solve_button = formatted_button(foo, 'SOLVE', f_scale)
        self.solve_button.grid(row=0, column=0, rowspan=2)
        self.solve_button['state'] = tk.DISABLED

        self.verify_button = formatted_button(foo, 'VERIFY', f_scale)
        self.verify_button.grid(row=0, column=1, rowspan=2)
        self.verify_button['state'] = tk.DISABLED

        self.select_button = formatted_button(foo, 'SELECT', f_scale)
        self.select_button.grid(row=0, column=2, rowspan=2)

    def initialize_board_selector_menu(self):
        """ to add borders, these buttons differ from control board buttons """
        def formatted_button(master, text, f_scale):
            """  """
            """ labels necessary due to tk limitations """
            """ functionally most similar to buttons """
            font_size = int(self.font_size * f_scale)
            button_color = self.BUTTON_COLOR
            button = tk.Label(master)
            button.config(text=text, anchor=tk.CENTER)
            button.config(font=(self.board_font, font_size))
            button.config(bg=button_color, relief='sunken', borderwidth=0)
            button.config(highlightbackground='black', highlightthickness=2)
            button.config(height=1, width=7)  # width in chars
            button.config(pady=8)
            return button

        # difficulty selector backdrop
        self.select_board_menu_container = (tk.Canvas(self.play_board))
        self.select_board_menu_container.config(
            highlightthickness=2,
            highlightbackground='black')
        # place cannot be used here; settings are forgotten

        # exclusively for button alignment  # todo: local?
        select_board_menu_backdrop = tk.Frame(self.select_board_menu_container)
        select_board_menu_backdrop.place(relx=.5, rely=.5, anchor=tk.CENTER)

        size = .8  # button font relative size
        sbmb = select_board_menu_backdrop

        self.empty_board_button = formatted_button(sbmb, "Empty", size)
        self.empty_board_button.grid(row=0, column=0, padx=2, pady=3)

        self.easy_board_button = formatted_button(sbmb, "Easy", size)
        self.easy_board_button.grid(row=0, column=1, padx=2, pady=3)

        self.hard_board_button = formatted_button(sbmb, "Hard", size)
        self.hard_board_button.grid(row=0, column=2, padx=2, pady=3)

        # self.random_board_button = formatted_button(sbmb, "Random", size)
        # self.random_board_button.grid(row=2, column=0)

        txt_1 = f"Gen. Rand. {self.easy_clue_size} Clue"
        self.random_easy_board_button = formatted_button(sbmb, txt_1, size)
        self.random_easy_board_button.config(width=max(len(txt_1) + 1, 14), padx=6)
        self.random_easy_board_button.grid(row=1, column=0, columnspan=3, padx=2, pady=0)

        txt_2 = f"Gen. Rand. {self.medium_clue_size} Clue"
        self.random_medium_board_button = formatted_button(sbmb, txt_2, size)
        self.random_medium_board_button.config(width=max(len(txt_2) + 1, 14), padx=6)
        self.random_medium_board_button.grid(row=2, column=0, columnspan=3, padx=2, pady=3)

        txt_3 = "Pick Rand. 17 Clue"
        self.random_pick_17_board_button = formatted_button(sbmb, txt_3, size)
        self.random_pick_17_board_button.config(width=max(len(txt_3) + 1, 14), padx=6)
        self.random_pick_17_board_button.grid(row=3, column=0, columnspan=3, padx=2, pady=0)

    def initialize_number_panel(self):
        """ these buttons MAY? differ from board select menu buttons """  # todo
        def formatted_button(master, text, f_scale):
            font_size = int(self.font_size * f_scale)
            button_color = self.BUTTON_COLOR
            button = tk.Label(master)
            button.config(text=text, anchor=tk.CENTER)
            button.config(bg=button_color, borderwidth=2, relief='solid')
            button.config(width=2, padx=0)
            button.config(font=(self.board_font, font_size))
            return button

        self.number_panel_container = tk.Canvas(self.board_input_panel_container)
        self.number_panel_container.pack()
        npc = self.number_panel_container
        npc.config(bg=self.DEFAULT_COLOR, highlightthickness=0)
        npc.grid_rowconfigure(0, weight=1)
        npc.grid_rowconfigure(2, weight=1)
        npc.grid_columnconfigure(0, weight=1)
        npc.grid_columnconfigure(10, weight=1)

        self.number_buttons = ['one-indexed']
        for i in range(1, 10):
            temp_button = formatted_button(npc, f'{i}', 1)
            temp_button.grid(row=1, column=i, rowspan=1, columnspan=1, sticky='')
            self.number_buttons.append(temp_button)

    def initialize_notes_panel(self):
        """ these buttons MAY? differ from board select menu buttons """  # todo
        def formatted_button(master, text, f_scale):
            font_size = int(self.font_size * f_scale)
            button_color = self.BUTTON_COLOR
            note_color = self.NOTE_COLOR
            button = tk.Label(master)
            button.config(text=text, anchor=tk.CENTER)
            button.config(bg=button_color, borderwidth=2, relief='solid')
            button.config(width=2, padx=0)
            button.config(font=(self.board_font, font_size))
            button.config(fg=note_color)
            return button

        self.notes_panel_container = tk.Canvas(self.board_input_panel_container)
        self.notes_panel_container.pack()
        npc = self.notes_panel_container
        npc.config(bg=self.DEFAULT_COLOR, highlightthickness=0)
        npc.grid_rowconfigure(0, weight=1)
        npc.grid_rowconfigure(2, weight=1)
        npc.grid_columnconfigure(0, weight=1)
        npc.grid_columnconfigure(10, weight=1)

        self.note_buttons = ['one-indexed']
        for i in range(1, 10):
            temp_button = formatted_button(npc, f'{i}', .8)
            temp_button.grid(row=1, column=i, rowspan=1, columnspan=1, sticky='')
            temp_button.grid(pady=0)
            self.note_buttons.append(temp_button)

    def initialize_board_input_panel(self):
        self.board_input_panel_container = tk.Canvas(self.container)
        self.board_input_panel_container.config(highlightthickness=0)
        self.board_input_panel_container.config(
            # width=self.play_board.winfo_reqwidth(),
            # height=self.CELL_SIZE,
            bg=self.DEFAULT_COLOR,
        )
        self.board_input_panel_container.pack()

        self.initialize_number_panel()
        self.initialize_notes_panel()

    def show_board_selector(self):
        p_rows = 4  # todo
        self.select_board_menu_container.place(
            relx=.5, rely=.5, width=400, height=60 * p_rows, anchor=tk.CENTER)

    def hide_board_selector(self):
        self.select_board_menu_container.place_forget()

    def lock_and_shade_cells(self, board_to_shade):
        """ locks and colors cells dark """
        for i in range(len(self.board_gui_data)):
            for j in range(len(self.board_gui_data[0])):
                cell_id = self.board_gui_data[i][j].cell_id
                text_id = self.board_gui_data[i][j].text_id
                number = board_to_shade[i][j]
                fill = self.LOCKED_CELL_FILL_COLOR
                if number == 0:  # reset old value
                    fill = ''
                    number = ''
                    self.board_gui_data[i][j].locked = False
                else:
                    self.board_gui_data[i][j].locked = True

                self.play_board.itemconfigure(cell_id, fill=fill)
                self.play_board.itemconfigure(text_id, text=number)
                self.play_board.lower(cell_id)

    def limited_update(self, changed_cells) -> None:
        """ changed_cells parameter of type [(i, j, value)]
            note: does NOT hide notes
        """
        if not changed_cells:
            return
        for ij, val in changed_cells:
            i, j = ij[0], ij[1]
            self.board_gui_data[i][j].value = val
            text_id = self.board_gui_data[i][j].text_id
            if val == 0:
                # reset zeroed cells
                cell_id = self.board_gui_data[i][j].cell_id
                self.play_board.itemconfigure(cell_id, fill=self.DEFAULT_CELL_COLOR)
                val = ''  # prevents display of zeros
            self.play_board.itemconfig(text_id, text=val)

    def update_entire_board(self, new_board) -> None:
        for i in range(len(new_board)):
            for j in range(len(new_board[0])):  # assumes rectangular
                self.board_gui_data[i][j].value = new_board[i][j]

                text_id = self.board_gui_data[i][j].text_id
                number = self.board_gui_data[i][j].value
                if number == 0:
                    number = ''

                self.play_board.itemconfig(text_id, text=number)
                self.hide_all_notes_at_cell(i, j)

    def shade_as_selected_cells(self, selected_cells):
        highlight = self.SELECT_HIGHLIGHT_COLOR
        for i, j in selected_cells:
            cell_id = self.board_gui_data[i][j].cell_id
            self.play_board.itemconfigure(cell_id, fill=highlight)

    def reset_colors_of_selected_cells(self, selected_cells):
        restore_color = self.DEFAULT_CELL_COLOR
        for i, j in selected_cells:
            cell_id = self.board_gui_data[i][j].cell_id
            self.play_board.itemconfigure(cell_id, fill=restore_color)

    def reset_colors_of_all_cells(self):
        for i in range(9):
            for j in range(9):
                fill = self.DEFAULT_CELL_COLOR
                if self.board_gui_data[i][j].locked:
                    fill = self.LOCKED_CELL_FILL_COLOR
                cell_id = self.board_gui_data[i][j].cell_id
                self.play_board.itemconfigure(
                    cell_id, fill=fill)

    def hide_invalid_notes_after_entry(self, i, j, val=None):
        """ given the cell (i, j), remove all invalid notes (sqr and hv) """
        # get top left corner of 3x3 square
        i_0 = i - (i % 3)
        j_0 = j - (j % 3)
        board_val = val
        if val is None:
            board_val = self.board_gui_data[i][j].value

        for k in range(3):
            for l in range(3):
                note_id = self.board_gui_data[i_0 + k][j_0 + l].note_ids[board_val]
                self.play_board.itemconfigure(note_id, state=tk.HIDDEN)

        for e in range(9):
            note_id = self.board_gui_data[e][j].note_ids[board_val]
            self.play_board.itemconfigure(note_id, state=tk.HIDDEN)
            note_id = self.board_gui_data[i][e].note_ids[board_val]
            self.play_board.itemconfigure(note_id, state=tk.HIDDEN)

    def hide_all_notes_at_cell(self, i, j):
        """ hides all notes taken at cell (i, j) """
        for k in range(1, 10):
            n_id = self.board_gui_data[i][j].note_ids[k]
            self.play_board.itemconfigure(n_id, state=tk.HIDDEN)

    def hide_all_notes_everywhere(self):
        """ hides all notes taken in all cells """
        for i in range(9):
            for j in range(9):
                for k in range(1,10):
                    n_id = self.board_gui_data[i][j].note_ids[k]
                    self.play_board.itemconfigure(n_id, state=tk.HIDDEN)

    # todo: broken from refactor
    def toggle_color(self):
        """ easter-egg that allows colorized components """
        self.cell_colors = not self.cell_colors

        # recolor number selector popup
        count = 0
        for id_, val in self.num_selector_lookup.items():
            tags = self.num_selector_popup.itemcget(id_, "tags")
            if 'backdrop' not in tags:
                continue
            fill = '#ffffff'
            if self.cell_colors:
                fill = self.fill[count]
                count += 1
            self.num_selector_popup.itemconfigure(id_, fill=fill)

    ###########################################################################
    # deprecated and debugging tools below

    # todo: deprecated
    def spawn_num_selector(self, i, j):
        board_width = self.play_board.winfo_width()
        board_height = self.play_board.winfo_height()
        cell_id = self.board_gui_data[i][j].cell_id
        x1y1x2y2 = self.play_board.coords(cell_id)
        x = x1y1x2y2[2] - self.CELL_SIZE / 2
        y = x1y1x2y2[3] - self.CELL_SIZE / 2
        x_rel = x / board_width
        y_rel = y / board_height

        # anchor = tk.NW
        anchor = ''
        if .33 < y_rel < .66 and .33 < x_rel < .66:
            anchor = 'nw'

        if y_rel > .66:
            anchor = 's'
        elif y_rel < .33:
            anchor = 'n'

        if x_rel > .66:
            anchor += 'e'
        elif x_rel < .33:
            anchor += 'w'

        self.num_selector_popup.place(relx=x_rel, rely=y_rel, anchor=anchor)

    # todo: deprecated
    def show_board_input_panel(self):
        self.board_input_panel_container.place(
            # relx=.5, rely=.94, width=490, height=60, anchor=tk.CENTER)
            relx=.5, rely=1, width=490, height=85, anchor=tk.S)

    # todo: deprecated
    def show_notes_panel(self):  # todo: deprecated
        self.notes_panel_container.place(
            relx=.5, rely=.94, width=490, height=60, anchor=tk.CENTER)
