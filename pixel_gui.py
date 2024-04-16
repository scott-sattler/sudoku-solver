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
    BOARD_SIZE = 9
    CELL_SIZE = 50

    def __init__(self, easy_clue_size, medium_clue_size, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.container = tk.Frame(self)
        self.container.config(background="#ffffff")
        self.container.pack(side="top", fill="both", expand=True)

        self.title('')
        self.iconbitmap(default=ICON_PATH)
        # self.iconbitmap(default='sudoku.ico')
        self.resizable(width=False, height=False)
        self.config(background="#ffffff")  # white

        self.offset = 40  # todo
        self.dynamic_size = self.BOARD_SIZE * self.CELL_SIZE

        self.board_font = "fixedsys"
        self.font_size = int(12 / 25.000 * self.CELL_SIZE)
        self.abort = False  # todo: reconsider

        self.title_text = 'SUDOKU SOLVER'
        self.title_container = None
        self.title_label = None

        self.play_board = None

        self.control_panel_container = None
        self.solve_button = None
        self.select_button = None
        self.verify_button = None

        self.notes_panel_container = None
        self.note_buttons = dict()


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

        self.num_selector_popup = None

        # todo: refactor
        self.board_state = None  # default/initialization state
        self.board_state_change = False
        self.board_loaded = False
        self.selected_cell = None
        self.has_lock = None
        # self.is_solvable = False
        # self.can_take_lock = list()

        self.validation_message = None

        self.board_index_lookup = dict()
        self.num_selector_lookup = dict()

        """ primary data structure """
        self.board_gui_data = [[CellData() for _ in range(9)] for __ in range(9)]

        self.play_board_width = 225.000 / 9 / 25 * self.dynamic_size + self.offset / 5 + 2
        self.play_board_height = 225.000 / 9 / 25 * self.dynamic_size + self.offset / 5 + 2

        self.title_container = tk.Canvas(self.container)

        self.play_board = tk.Canvas(self.container)
        self.play_board.config(
            height=self.play_board_height,
            width=self.play_board_width,
            bg='#ffffff', borderwidth=0, highlightthickness=0,
        )
        self.play_board.pack()


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


    def initialize_title(self):
        font_size = self.font_size

        self.title_container = tk.Canvas(self.container)
        self.title_container.config(borderwidth=0, highlightthickness=0)
        self.title_container.pack(before=self.play_board)  # todo: order of execution dependence

        self.title_label = tk.Label(
            self.title_container,
            text=self.title_text,
            font=(self.board_font, font_size * 2),
            bg="#fff",
            padx=20,
        )
        self.title_label.pack()

    def initialize_play_board(self):
        """
        - create board lines
        - initialize (populate) board_gui_data matrix
            create canvas and text box for each cell
        """
        board_size = len(self.board_gui_data)

        font_size = self.font_size
        cell_size = self.CELL_SIZE
        offset = self.offset
        cbw = self.play_board.winfo_reqwidth()
        cbh = self.play_board.winfo_reqheight()

        # create lines (the +4 is the grid offset from the cells - style)
        for x_shift in range(board_size - 1):
            if (x_shift + 1) % 3 != 0:
                x_0 = (x_shift + 1) * cell_size + offset / 8
                x_1 = (x_shift + 1) * cell_size + offset / 8
                y_0 = 0 + offset / 8
                y_1 = cbh - offset / 8
                width = 1
            else:
                x_0 = (x_shift + 1) * cell_size + offset / 10
                x_1 = (x_shift + 1) * cell_size + offset / 10
                y_0 = 0
                y_1 = cbh
                width = 3
            self.play_board.create_line(x_0, y_0, x_1, y_1, width=width)

        for y_shift in range(board_size - 1):
            if (y_shift + 1) % 3 != 0:
                x_0 = 0 + offset / 8
                x_1 = cbh - offset / 8
                y_0 = (y_shift + 1) * cell_size + offset / 8
                y_1 = (y_shift + 1) * cell_size + offset / 8
                width = 1
            else:
                x_0 = 0
                x_1 = cbh
                y_0 = (y_shift + 1) * cell_size + offset / 8
                y_1 = (y_shift + 1) * cell_size + offset / 8
                width = 3
            self.play_board.create_line(x_0, y_0, x_1, y_1, width=width)

        # initialize board_gui_data matrix
        # creates canvas and text box for each cell
        for i in range(len(self.board_gui_data)):
            for j in range(len(self.board_gui_data[0])):  # assumes rectangular
                canvas_id = self.play_board.create_rectangle(
                    j * 50 + self.offset / 8,
                    i * 50 + self.offset / 8,
                    (j + 1) * 50 + self.offset / 8,
                    (i + 1) * 50 + self.offset / 8,
                    width=0, fill="#ffffff",
                    tags="cell",
                )

                txt_id = self.play_board.create_text(
                    cell_size / 2 + (j * cell_size) + 4,
                    cell_size / 2 + (i * cell_size) + 4,
                    font=(self.board_font, font_size),
                    text='',  # str(i) + str(j)
                    tags="cell",
                )

                self.play_board.lower(canvas_id)
                self.board_gui_data[i][j].canvas_id = canvas_id
                self.board_gui_data[i][j].text_id = txt_id

                self.board_index_lookup[txt_id] = (i, j)
                self.board_index_lookup[canvas_id] = (i, j)

    def initialize_num_selector_popup(self):
        cell_size = self.CELL_SIZE
        width = cell_size * 3
        height = cell_size * 3
        border_width = 3
        rect_b_width = 2

        self.num_selector_popup = tk.Canvas(self.play_board)
        self.num_selector_popup.config(
            width=width, height=height,
            bg='#ffffff', borderwidth=border_width, highlightthickness=0)
        self.num_selector_popup.place(relx=0, rely=0)
        self.num_selector_popup["state"] = tk.DISABLED
        self.num_selector_popup.place_forget()

        for i in range(3):
            for j in range(3):
                num = (i * 3) + (j + 1)
                color = self.fill[num - 1] if self.cell_colors else '#ffffff'

                canvas_id = self.num_selector_popup.create_rectangle(
                    j * (width / 3) + border_width + rect_b_width,
                    i * (width / 3) + border_width + rect_b_width,
                    j * (width / 3) + cell_size + border_width / 3,
                    i * (width / 3) + cell_size + border_width / 3,
                    width=rect_b_width, fill=color,  # fill='cyan',
                    tags=('num', 'backdrop'),
                )
                self.num_selector_lookup[canvas_id] = num

                text_id = self.num_selector_popup.create_text(
                    j * (width / 3) + (border_width + rect_b_width + cell_size) / 2,
                    i * (width / 3) + (border_width + rect_b_width + cell_size) / 2,
                    font=(self.board_font, self.font_size),
                    text=num,
                    tags='num',
                )
                self.num_selector_lookup[text_id] = num

    def initialize_control_board(self):
        """ these buttons differ from board select menu buttons """
        def formatted_button(master, text, f_scale):
            font_size = int(self.font_size * f_scale)
            button = tk.Label(master)
            button.config(text=text, anchor=tk.CENTER)
            button.config(bg='#ffffff', borderwidth=0)
            button.config(width=8)
            button.config(font=(self.board_font, font_size))
            return button

        # note: Canvas has useful options and functionality versus Frame
        self.control_panel_container = tk.Canvas(self.container)
        self.control_panel_container.config(
            width=self.play_board.winfo_reqwidth(),
            height=self.CELL_SIZE, bg='#ffffff', highlightthickness=0,)
        self.control_panel_container.pack(fill=tk.BOTH, side=tk.BOTTOM, ipady=10)

        # solve, verify, and select buttons
        c_p_c = self.control_panel_container  # buttons parent
        foo = tk.Frame(c_p_c, bg='#ffffff')
        foo.place(relx=.5, rely=.5, anchor=tk.CENTER)

        self.solve_button = formatted_button(foo, 'SOLVE', 1.2)
        self.solve_button.grid(row=0, column=0, rowspan=2)
        self.solve_button['state'] = tk.DISABLED

        self.verify_button = formatted_button(foo, 'VERIFY', 1.2)
        self.verify_button.grid(row=0, column=1, rowspan=2)
        self.verify_button['state'] = tk.DISABLED

        self.select_button = formatted_button(foo, 'SELECT', 1.2)
        self.select_button.grid(row=0, column=2, rowspan=2)

    def initialize_board_selector_menu(self):
        """ to add borders, these buttons differ from control board buttons """
        def formatted_button(master, text, f_scale):
            """  """
            """ labels necessary due to tk limitations """
            """ functionally most similar to buttons """
            font_size = int(self.font_size * f_scale)
            button = tk.Label(master)
            button.config(text=text, anchor=tk.CENTER)
            button.config(bg='#ffffff', relief='sunken', borderwidth=0)
            button.config(highlightbackground='black', highlightthickness=2)
            button.config(font=(self.board_font, font_size))
            button.config(height=1, width=7)  # width in chars
            button.config(pady=8)
            return button

        # difficulty selector backdrop
        self.select_board_menu_container = (tk.Canvas(self.play_board))
        self.select_board_menu_container.config(
            highlightthickness=2, highlightbackground='black')
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


    def initialize_notes_panel(self):
        """ these buttons MAY? differ from board select menu buttons """  # todo
        def formatted_button(master, text, f_scale):
            font_size = int(self.font_size * f_scale)
            button = tk.Label(master)
            button.config(text=text, anchor=tk.CENTER)
            button.config(bg='#ffffff', borderwidth=2, relief='solid')
            button.config(width=2, padx=0)
            button.config(font=(self.board_font, font_size))
            return button

        self.notes_panel_container = tk.Canvas(self.container)
        npc = self.notes_panel_container
        npc.config(
            bg='#f0ff0f', highlightthickness=2, highlightbackground='black',
        )
        npc.grid_rowconfigure(0, weight=1)
        npc.grid_rowconfigure(2, weight=1)
        npc.grid_columnconfigure(0, weight=1)
        npc.grid_columnconfigure(10, weight=1)

        for i in range(1, 10):
            temp_button = formatted_button(npc, f'{i}', 1)
            temp_button.grid(row=1, column=i, rowspan=1, columnspan=1, sticky='')
            self.note_buttons[i] = temp_button

        self.notes_panel_container.place(relx=.5, rely=.94, width=490, height=60, anchor=tk.CENTER)  # todo: move

    def lock_and_shade_cells(self, board_to_shade):
        """ locks and colors cells dark """
        for i in range(len(self.board_gui_data)):
            for j in range(len(self.board_gui_data[0])):
                canvas_id = self.board_gui_data[i][j].canvas_id
                text_id = self.board_gui_data[i][j].text_id
                number = board_to_shade[i][j]
                fill = '#D4D4D4'  # is 'grey83'; previous was 'gray77'
                if number == 0:  # reset old value
                    fill = ''
                    number = ''
                    self.board_gui_data[i][j].locked = False
                else:
                    self.board_gui_data[i][j].locked = True

                self.play_board.itemconfigure(canvas_id, fill=fill)
                self.play_board.itemconfigure(text_id, text=number)
                self.play_board.lower(canvas_id)

    def limited_update(self, changed_cells) -> None:
        """ changed_cells parameter of type [(i, j, value)] """
        if not changed_cells:
            return
        for i, j, val in changed_cells:
            self.board_gui_data[i][j].value = val
            text_id = self.board_gui_data[i][j].text_id
            if val == 0:  # prevents display of zeros
                val = ''
            self.play_board.itemconfig(text_id, text=val)
        self.board_state_change = True

    def update_entire_board(self, new_board, state_change=True) -> None:
        for i in range(len(new_board)):
            for j in range(len(new_board[0])):  # assumes rectangular
                self.board_gui_data[i][j].value = new_board[i][j]

                text_id = self.board_gui_data[i][j].text_id
                number = self.board_gui_data[i][j].value
                if number == 0:
                    number = ''

                self.play_board.itemconfig(text_id, text=number)
        if state_change:
            self.board_state_change = True

    def spawn_num_selector(self, e):
        board_width = self.play_board.winfo_width()
        board_height = self.play_board.winfo_height()
        x = e.x_root - self.play_board.winfo_rootx()
        y = e.y_root - self.play_board.winfo_rooty()
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

    def toggle_color(self):
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
