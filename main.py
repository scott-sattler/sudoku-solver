import logging
from class_cell_data import CellData
import tkinter as tk
from pixel_gui import PixelGUI
import matrix_library
from solver_engine import SolverEngine
from board_operations import BoardOperations
from file_io import FileIO


# print('''
# todo:
#     merge select and delete logic (shift area; old/single selection area)
#     ...
#     solver could use notes as an implicit stack for unexplored children...
#     tho, still going to perform vastly inferior to dancing links...
#     could look cool tho !
#     ...
#     solver was mostly to look cool, but is a bit slow on fixed 17 boards
#     consider precomputing valid moves (would preserve coolness of current solution)
#     ...
#     ! address 40 clue min edge case
#     consider adding valid transformations (for previously selected boards?)
#     ...
#     implement previously randomly selected record (currently in logs)
#     some sort of save system... scores, etc. ?
#     ...
#     optimize random generation; probably require redesign using dancing links
#     ...
#     asyncio/multiprocessing/multithreading for board generation?
#     spawn multiple threads for multiple boards? worse min, better worst case
#     ...
#     consider picking random cells and filling them
#     ...
#     review and resolve existing todos
#     matrix creator via input? eg 123456789<enter>2345...
#     ...
#     optimization fun (temporal constraints tho :( ):
#         to (more) optimally reduce density:
#         transform matrix into undirected graph
#         give each node
#             decrement method
#                 decrement count of adjacent nodes (including diagonal?)
#             references to diagonal neighbors (dijkstra's update analogue)
#         heapify single pass array of nodes (binary heap implementation)
#         using this priority queue, pop, decrement (need update?), validate
#
# todo (old):
#     taskbar icon not displaying
#     consider subclasses
#     http://stackoverflow.com/questions/17056211/python-tkinter-option-menu
#
# build commands:
#     pyinstaller --onefile --noconsole --name=sudoku --add-data="17puz49158.txt;." --icon='.\sudoku.ico' main.py
#     pyinstaller --onefile --name='sudoku_console' --add-data="17puz49158.txt;." --icon='.\sudoku.ico' main.py
#
# ''')

class StateManager:
    CURRENT = 'current'
    PREVIOUS = 'previous'
    WELCOME = 'welcome'
    BOARD_SELECTION = 'board_selection'
    BOARD_LOADED = 'board_loaded'
    # BOARD_INPUT = 'baord_input'
    NUMBER_SELECTOR = 'number_selector'
    SOLVING_BOARD = 'solving_board'
    ABORTED = 'aborted'
    VALIDATED = 'validated'

    all_states = [
        CURRENT,
        PREVIOUS,
        WELCOME,
        BOARD_SELECTION,
        BOARD_LOADED,
        # BOARD_INPUT,
        NUMBER_SELECTOR,
        SOLVING_BOARD,
        ABORTED,
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

    def revert_state(self):
        prev = self.state_manager[self.PREVIOUS]
        curr = self.state_manager[self.CURRENT]
        self.state_manager[self.PREVIOUS] = curr
        self.state_manager[self.CURRENT] = prev

    def board_selector_enable(self):
        self.update_previous()
        self.update_current(self.BOARD_SELECTION)
        self.state_manager[self.BOARD_SELECTION] = True

    def board_selector_disable(self):
        if self.get_current() == self.BOARD_SELECTION:
            self.revert_state()
            self.state_manager[self.BOARD_SELECTION] = False

    def board_loaded(self):
        self.update_previous()
        self.update_current(self.BOARD_LOADED)
        self.state_manager[self.BOARD_LOADED] = True

    # def board_input(self):
    #     self.update_previous()
    #     self.update_current(self.BOARD_INPUT)
    #     self.state_manager[self.BOARD_INPUT] = True

    def solving_board_begin(self):
        self.update_previous()
        self.update_current(self.SOLVING_BOARD)
        self.state_manager[self.SOLVING_BOARD] = True

    def solving_board_complete(self):
        if self.get_current() == self.SOLVING_BOARD:
            self.revert_state()
            # self.state_manager[self.BOARD_LOADED] = False  todo ?

    def aborted_solve(self):
        self.state_manager[self.PREVIOUS] = self.BOARD_LOADED
        self.update_current(self.ABORTED)
        # self.state_manager[self.BOARD_LOADED] = False  todo ?

    def validate_board(self):
        if self.get_current() != self.VALIDATED:
            self.update_previous()
            self.update_current(self.VALIDATED)


    # todo: not really using values... mostly just curr/prev strings... ? good?







class SudokuApp:
    board_width = 9
    board_height = 9

    easy_clue_size = 34
    medium_clue_size = 28

    # PRIMARY_BUTTON = "<Button-1>"  # todo: unimplemented

    INPUT = {
        'mouse-1':  0b00001,  # left mouse button
        'mouse-3':  0b00100,  # right mouse button
        'shift':    0b01000,  # shift
        'motion':   0b10000,  # motion
    }

    # # logger = logging.getLogger(__name__)
    # logging.basicConfig(filename='main_log.log', encoding='utf-8', level=logging.DEBUG)
    # logging.getLogger()

    def __init__(self):
        logging.getLogger()
        logging.basicConfig(filename='logs.log', encoding='utf-8', level=logging.DEBUG)

        self.cell_selection_queue = dict()  # set lacks order

        self.gui = PixelGUI(self.easy_clue_size, self.medium_clue_size)
        self.se = SolverEngine()
        self.rg = BoardOperations(self.board_width, self.board_height)
        self.io = FileIO()

        # order dependent
        self.gui.initialize_title()
        self.gui.initialize_play_board()
        self.gui.initialize_control_board()
        self.gui.initialize_board_selector_menu()
        self.gui.initialize_num_selector_popup()
        self.gui.initialize_notes_panel()
        self.bindings()  # call last
        self.gui.update_entire_board(self.gui.welcome_message, state_change=False)

        self.state = StateManager()
        self.all_board_references = self.gui.load_all_boards()

        self.state_solving = False  # todo: remove


    def bindings(self):
        # todo: review todo below; have changed functionality since
        # todo: hold and drag Tkinter bug; have to code workaround or ignore
        # self.gui.bind("<Button-1>", self.event_handler)
        # self.gui.bind("<Button-3>", self.event_handler)
        self.gui.bind("<Button-1>", self.event_handler_new)
        self.gui.bind("<Button-3>", self.event_handler_new)

        shift_mb1 = self.INPUT['shift'] | self.INPUT['mouse-1']
        motion_shift_mb1 = shift_mb1 | self.INPUT['motion']
        shift_mb3 = self.INPUT['shift'] | self.INPUT['mouse-3']
        motion_shift_mb3 = shift_mb3 | self.INPUT['motion']

        self.gui.bind("<Shift-Button-1>", lambda e: self.cell_select(e, shift_mb1))
        self.gui.bind("<Shift-B1-Motion>", lambda e: self.cell_select(e, motion_shift_mb1))
        self.gui.bind("<Shift-Button-3>", lambda e: self.cell_select(e, shift_mb3))
        self.gui.bind("<Shift-B3-Motion>", lambda e: self.cell_select(e, motion_shift_mb3))

        self.gui.bind("<Shift-KeyRelease>", self.shift_release)
        # self.gui.bind("<ButtonRelease-1>", self.event_handler)
        # self.gui.bind("<Button-2>", self.event_handler)

        # self.gui.bind("<ButtonRelease-3>", self.event_handler)
        self.gui.bind("<c>", lambda e: self.gui.toggle_color())

        # todo: consolidate into shader fn
        def enter_button_shade(e):
            # does not work with colorized cells (debug/fun tools)
            if e.widget['bg'] == self.gui.BUTTON_COLOR:
                e.widget['bg'] = self.gui.BUTTON_HOVER_COLOR

        # noinspection SpellCheckingInspection
        def leave_button_unshade(e):
            # does not work with colorized cells (debug/fun tools)
            if e.widget['bg'] == self.gui.BUTTON_HOVER_COLOR:
                e.widget['bg'] = self.gui.BUTTON_COLOR

        def enter_notes_hide(e):
            self.gui.num_selector_popup.place_forget()

        # todo:
        def leave_notes_show(e):
            # if not self.cell_selection_queue:
            #     return
            # i, j = list(self.cell_selection_queue.keys())[-1]  # todo: redesign
            # self.gui.spawn_num_selector(i, j)
            return

        """ manually bind all buttons because my_boss chose dated framework """
        s_b_m_c = self.gui.select_board_menu_container
        c_p_c = self.gui.control_panel_container
        s_b_m_c_children = s_b_m_c.winfo_children()[0].winfo_children()
        """                ^ container              ^ backdrop              """
        c_p_c_children = c_p_c.winfo_children()[0].winfo_children()
        """              ^ container            ^ backdrop                  """
        all_children = s_b_m_c_children + c_p_c_children
        for button in all_children:
            button.bind("<Enter>", enter_button_shade)
            button.bind("<Leave>", leave_button_unshade)

        self.gui.notes_panel_container.bind("<Enter>", enter_notes_hide)
        self.gui.notes_panel_container.bind("<Leave>", leave_notes_show)

        # todo: debuggin' ma life away
        import utilities as u
        def debug_debug_info():
            # print(f"{'has_lock ':.<30} {self.gui.has_lock}")  # todo: deprecated
            print(f"{'cell_selection_queue ':.<30} {self.cell_selection_queue}")  # todo: deprecated; use self.sell_selection_queue
            print(f"{'state.get_current() ':.<30} {self.state.get_current()}")  # todo: deprecated;
            print(f"{'state.get_current() ':.<30} {self.state.state_manager}")
            print()

        def invert_color(element):  # noqa
            if element is None: return  # noqa
            rgb = element.cget('bg')
            if rgb == 'SystemButtonFace': rgb = '#f0f0f0'  # noqa
            if rgb == 'white':  rgb = '#FFFFFF'  # noqa
            rgb = rgb[1:] if rgb[0] == '#' else rgb
            shade = 128
            rgb_hex = (rgb[:2], rgb[2:4], rgb[4:])
            to_ints = tuple(map(lambda x: int(x, 16), rgb_hex))
            offset = tuple(map(lambda x: (x + shade) % 256, to_ints))
            cycled = '#' + ''.join(map(lambda x: hex(x)[2:], offset))
            element.config(bg=cycled)

        key_map = {
            # note: unable to use shift binds
            '<Alt-h>': lambda e: print('text containing help commands'),
            '<Alt-d>': lambda e: debug_debug_info(),
            '<Alt-l>': lambda e: invert_color(self.gui.has_lock),
            '<Alt-c>': lambda e: self.debugging_tools_change_obj_color(e, False),
            '<Alt-b>': lambda e: print(
                u.strip_for_print([[cell.value for cell in row] for row in self.gui.board_gui_data])),  # noqa
        }
        for k, v in key_map.items():
            self.gui.bind(k, v)

    @staticmethod
    def mouse_position_relative_to_obj(e, obj):
        # absolute obj position (NE?) relative to entire screen
        pb_abs_x = obj.winfo_rootx()
        pb_abs_y = obj.winfo_rooty()

        # absolute mouse position relative to entire screen
        # (note: modified by Windows desktop/UI scaling factor)
        abs_x = e.x_root
        abs_y = e.y_root

        rel_x = abs_x - pb_abs_x
        rel_y = abs_y - pb_abs_y

        return rel_x, rel_y

    def mouse_in_play_area(self, e, cosmetic_offset=5) -> tuple | bool:
        board = self.gui.play_board

        grid_line_recess = cosmetic_offset  # pixels
        rel_x, rel_y = self.mouse_position_relative_to_obj(e, board)

        board_width = board.winfo_reqwidth()
        board_height = board.winfo_height()

        lower_x = 0 + grid_line_recess
        lower_y = 0 + grid_line_recess
        upper_x = board_width - grid_line_recess
        upper_y = board_height - grid_line_recess

        if upper_x > rel_x > lower_x and upper_y > rel_y > lower_y:
            return rel_x, rel_y
        return False

    def cell_select(self, e, bitflags):
        """
        explicit modifier evidently necessary
        Tk seems to not work correctly, possibly due to undocumented change
        github.com/python/cpython/blob/main/Lib/tkinter/__init__.py#L1707
        """
        if self.state.get_current() != self.state.BOARD_LOADED:
            return

        board = self.gui.play_board
        if not self.mouse_in_play_area(e):
            return

        rel_x, rel_y = self.mouse_in_play_area(e)

        # # ignore inputs that start off board
        # if e.widget != board:
        #     return

        obj_ids = board.find_closest(rel_x, rel_y)
        id_ = obj_ids[0]
        tags = board.gettags(id_)

        if not ('cell' in tags or 'note' in tags):
            return

        i, j = self.gui.board_index_lookup.get(id_)
        if self.gui.board_gui_data[i][j].locked:  # exclude locked cells
            return

        fill = 'red'  # todo: appearance indicates error
        if bitflags & self.INPUT['mouse-1']:  # left mouse button
            fill = self.gui.SELECT_HIGHLIGHT_COLOR
            self.cell_selection_queue[(i, j)] = None
        elif bitflags & self.INPUT['mouse-3']:  # right mouse button
            fill = self.gui.DEFAULT_CELL_COLOR
            self.cell_selection_queue.pop((i, j), 0)

        cell_id = self.gui.board_gui_data[i][j].cell_id
        self.gui.play_board.itemconfigure(cell_id, fill=fill)

    def shift_release(self, e):
        if not self.cell_selection_queue:
            return

        self.gui.spawn_notes_panel()

    # todo: consider refactor into separate fns
    def event_handler(self, e):
        """  """
        """ employs an application state pattern """
        """ motivation: organizational and clarity """
        empty_board = self.gui.empty_board_button
        easy_board = self.gui.easy_board_button
        hard_board = self.gui.hard_board_button
        gen_larger_clue = self.gui.random_easy_board_button
        gen_smaller_clue = self.gui.random_medium_board_button
        random_17 = self.gui.random_pick_17_board_button
        boards = [empty_board, easy_board, hard_board, gen_larger_clue, gen_smaller_clue, random_17]

        def convert_board():
            """ convert to array of int arrays """
            return [[cell.value for cell in row] for row in self.gui.board_gui_data]

        def board_input(event):  # todo: this should only be called when board input (see below)
            if not self.gui.board_loaded:
                return
            if self.state_solving:
                return

            board = event.widget  # play board OR num selector
            x = event.x_root - board.winfo_rootx()  # todo: is this e.x?
            y = event.y_root - board.winfo_rooty()  # todo: is this e.y?
            cb = self.gui.play_board
            offset = self.gui.offset / (self.gui.BOARD_SIZE - 1)  # canvas lines/cells offset

            obj_ids = board.find_closest(x, y)
            id_ = obj_ids[0]
            tags = board.gettags(id_)

            if self.mouse_in_play_area(e):  # todo: this shouldn't be necessary (see above)
                i, j = self.gui.board_index_lookup.get(id_)
            else:
                return

            # if a note was registered (vs cell) on delete command
            if e.num == 3:
                self.gui.limited_update([((i, j), 0)])
                self.cell_selection_queue.pop((i, j))
            # if board cell (or cell note) was selected
            elif 'cell' in tags or 'note' in tags:
                if self.gui.board_gui_data[i][j].locked:
                    # ignore locked (loaded board) cells
                    reset_ui_state()
                # elif e.num == 3:  # and not self.gui.selected_cell:  # todo: move to fn?
                #     # delete cell entry on right click
                #     self.gui.limited_update([((i, j), 0)])
                elif not self.cell_selection_queue:  # self.gui.selected_cell:
                    # record cell and spawn number selector popup
                    # self.gui.selected_cell = (i, j)  # todo: deprecated
                    self.cell_selection_queue[(i, j)] = None
                    self.gui.spawn_num_selector(i, j)
                    self.gui.spawn_notes_panel()
                    self.gui.has_lock = self.gui.play_board
                    # shade selected cell
                    highlight = self.gui.SELECT_HIGHLIGHT_COLOR
                    cell_id = self.gui.board_gui_data[i][j].cell_id
                    self.gui.play_board.itemconfigure(cell_id, fill=highlight)  # todo: move to gui  as fn?
                else:
                    reset_ui_state()
            # if the num selector was selected
            elif 'num' in tags:
                print('num path')
                val = self.gui.num_selector_lookup.get(id_)
                cells_to_update = list()
                for ij, v in self.cell_selection_queue.items():
                    i, j = ij[0], ij[1]
                    pb_obj_id = self.gui.board_gui_data[i][j].cell_id
                    cb.itemconfigure(pb_obj_id, fill='#ffffff')  # todo:
                    cells_to_update.append((ij, val))
                self.gui.limited_update(cells_to_update)
                self.gui.hide_notes_at_cell(i, j)
            else:
                reset_ui_state()

        # todo: refactor further ?; kept from old design
        # todo: refactor matrix import into main
        def board_selector(event):
            from testing.test_cases import TestMatrices

            board = TestMatrices().matrix_00()
            if event.widget == self.gui.easy_board_button:
                board = TestMatrices().matrix_01()
            elif event.widget == self.gui.hard_board_button:
                board = TestMatrices().matrix_11()  # hard
            elif event.widget == self.gui.random_easy_board_button:
                board = self.rg.generate_board(self.easy_clue_size, sec=3)
                str_b = self.io.board_to_str(board)
                logging.info(f'{self.medium_clue_size} clue generated:\n\t{str_b}')
            elif event.widget == self.gui.random_medium_board_button:
                board = self.rg.generate_board(self.medium_clue_size, sec=3)
                str_b = self.io.board_to_str(board)
                logging.info(f'{self.medium_clue_size} clue generated:\n\t{str_b}')
            elif event.widget == self.gui.random_pick_17_board_button:
                # board = matrix_library.steering_wheel_classic
                board = self.io.read_and_load_board_from_17_hints_data_file()

            self.gui.update_entire_board(board)
            self.gui.lock_and_shade_cells(board)

        def solve_board():
            board_data = convert_board()
            generator_solver = self.se.solve_board(board_data)

            for next_limited_update in generator_solver:
                if self.abort:
                    # generator_solver.send('stop')
                    self.abort = False
                    break

                if not next_limited_update:
                    break
                self.gui.limited_update(next_limited_update)
                self.gui.update()

        # todo: keep validation result until board state changes
        # todo: probably refactor (eg board_state_change confusing)
        def click_solve():
            if self.gui.solve_button['state'] == tk.DISABLED:
                return
            if self.gui.solve_button.cget('text') == 'SOLVE':
                self.gui.select_board_menu_container.place_forget()
                self.gui.solve_button.config(text='ABORT?')
                self.gui.verify_button['state'] = tk.DISABLED
                self.gui.select_button['state'] = tk.DISABLED
                self.state_solving = True
                solve_board()
                self.gui.solve_button.config(text='SOLVE')
                self.gui.solve_button['state'] = tk.DISABLED
                self.state_solving = False
                self.gui.select_button['state'] = tk.NORMAL
                self.gui.verify_button['state'] = tk.NORMAL
                self.gui.board_loaded = False
                verify()
                self.gui.board_state_change = False
            else:  # solve_button.cget('text') == 'ABORT?'
                self.abort = True
                self.gui.verify_button['state'] = tk.DISABLED

        # to do: separate gui verify state
        def verify():
            se = SolverEngine()

            if se.validate_board(convert_board()):
                self.gui.title_label.config(
                    text='VALIDATED!',
                    width=len(self.gui.title_text))
                # self.gui.verify_button['state'] = tk.DISABLED
                self.gui.title_label.config(bg='#53ec53')
                self.gui.solve_button['state'] = tk.DISABLED
            else:
                self.gui.title_label.config(
                    text='invalid :(',
                    width=len(self.gui.title_text))
                self.gui.title_label.config(bg='#ec5353')
            self.gui.verify_button['state'] = tk.DISABLED

        def reset_ui_state():
            self.gui.select_board_menu_container.place_forget()
            self.gui.notes_panel_container.place_forget()
            self.gui.num_selector_popup.place_forget()

            restore_color = self.gui.DEFAULT_CELL_COLOR
            for ij, v in self.cell_selection_queue.items():
                cell_id = self.gui.board_gui_data[ij[0]][ij[1]].cell_id
                self.gui.play_board.itemconfigure(cell_id, fill=restore_color)

            self.cell_selection_queue = dict()
            self.gui.has_lock = None

        # if e.num == 2:
        #     self.debugging_tools_change_obj_color(e)
        #     return

        # todo: control flow outer
        if e.widget in self.gui.note_buttons:
            for ij, v in self.cell_selection_queue.items():
                i, j = ij[0], ij[1]
                num = int(e.widget.cget('text'))
                note_id = self.gui.board_gui_data[i][j].note_ids[num]
                self.gui.play_board.itemconfigure(note_id, state=tk.NORMAL)

        # clears, on any input, valid/invalid results
        if self.gui.title_label.cget('text') != self.gui.title_text:
            self.gui.title_label.config(text=self.gui.title_text, bg='#ffffff')

        if e.widget in [self.gui.play_board, self.gui.num_selector_popup]:
            # todo: handling same types of things in different places
            # todo: handling same types of things in different places

            """ handles board user entry """
            # ~ self.gui.select_board_menu_container.winfo_viewable():
            if self.gui.has_lock in [None, self.gui.play_board]:
                board_input(e)
            else:
                reset_ui_state()  # todo: review

        elif e.widget == self.gui.select_button:
            """ spawns difficulty menu after clicking 'select' """
            if self.gui.select_button['state'] == tk.DISABLED:
                return

            # does not have lock
            if self.gui.has_lock != self.gui.select_board_menu_container:
                # other has lock
                if self.gui.has_lock is not None:
                    reset_ui_state()
                """ place() doesn't work without arguments ??? """
                """ even if place(*args) is called at creation """
                p_rows = 4
                self.gui.select_board_menu_container.place(
                    relx=.5, rely=.5, width=400, height=60 * p_rows, anchor=tk.CENTER)
                self.gui.has_lock = self.gui.select_board_menu_container
            # ~ self.gui.select_board_menu_container.winfo_viewable():
            elif self.gui.select_board_menu_container == self.gui.has_lock:
                reset_ui_state()
        elif e.widget in boards:
            board_selector(e)
            self.gui.solve_button['state'] = tk.NORMAL
            self.gui.verify_button['state'] = tk.NORMAL
            self.gui.board_loaded = True
            reset_ui_state()

        elif e.widget == self.gui.solve_button:
            if self.gui.has_lock:
                return
            click_solve()
        elif e.widget == self.gui.verify_button:
            if not self.gui.board_loaded:
                return
            if self.gui.has_lock or self.state_solving:
                return
            if self.gui.verify_button['state'] == tk.NORMAL:
                verify()

        # todo: this was created as a sentinel for the title, but is misused in the click_solve() code...
        if self.gui.board_state_change:
            """ restores title to original state on any user input """
            self.gui.title_label.config(text=self.gui.title_text, bg='#ffffff')
            self.gui.board_state_change = False

            self.gui.verify_button['state'] = tk.NORMAL

        self.gui.update()

    def event_handler_new(self, e):
        """ states constrain an event driven process """
        state = self.state
        gui = self.gui

        # todo: move to fn?
        # clears, on any input, valid/invalid results
        if self.gui.title_label.cget('text') != self.gui.title_text:
            self.gui.title_label.config(text=self.gui.title_text, bg='#ffffff')

        # welcome state                                                  # noqa
        if state.get_current() == state.WELCOME:
            # only allow board selection at welcome
            if e.widget == gui.select_button:
                gui.spawn_board_selector()
                state.board_selector_enable()
        # board selection state
        elif state.get_current() == state.BOARD_SELECTION:
            # allow board selector menu to be toggled
            if e.widget == gui.select_button:
                gui.hide_board_selector()
                state.board_selector_disable()
            # execute board selection
            elif e.widget in self.all_board_references:
                selected_board = self.select_board(e)
                gui.update_entire_board(selected_board)
                gui.lock_and_shade_cells(selected_board)
                state.board_loaded()
                self.reset_ui_state()
        # board loaded state
        elif state.get_current() == state.BOARD_LOADED:
            # solve button
            if e.widget == gui.solve_button:
                state.solving_board_begin()
                self.execute_solve_state()
                state.solving_board_complete()
            # verify button
            elif e.widget == gui.verify_button:
                state.validate_board()
                self.verify_board()
            # select button
            elif e.widget == gui.select_button:
                gui.spawn_board_selector()
                state.board_selector_enable()
            # board selection and input
            elif e.widget in [self.gui.play_board, self.gui.num_selector_popup]:
                self.board_input_entry(e)
            # notes input
            elif e.widget in self.gui.note_buttons:
                self.board_input_notes(e)
        # solving board state
        elif state.get_current() == state.SOLVING_BOARD:
            # solve button (transformed into "abort" button)
            if e.widget == gui.solve_button:
                state.aborted_solve()
        # aborted state
        elif state.get_current() == state.ABORTED:
            # select button
            if e.widget == gui.select_button:
                gui.spawn_board_selector()
                state.board_selector_enable()
        # board validated/invalidated
        elif state.get_current() == state.VALIDATED:  # todo: time between validation and validated?
            # select button
            if e.widget == gui.select_button:
                gui.spawn_board_selector()
                state.board_selector_enable()
            # solve button
            elif e.widget == gui.solve_button:
                state.solving_board_begin()
                self.execute_solve_state()
                state.solving_board_complete()
            # verify button
            elif e.widget == gui.verify_button:
                state.validate_board()
                self.verify_board()




    def select_board(self, e):
        import matrix_library as ml

        board = ml.empty_board()
        if e.widget == self.gui.easy_board_button:
            board = ml.easy_example()
        elif e.widget == self.gui.hard_board_button:
            board = ml.hard_example()
        elif e.widget == self.gui.random_easy_board_button:
            board = self.rg.generate_board(self.easy_clue_size, sec=3)
            str_b = self.io.board_to_str(board)
            logging.info(f'{self.medium_clue_size} clue generated:\n\t{str_b}')
        elif e.widget == self.gui.random_medium_board_button:
            board = self.rg.generate_board(self.medium_clue_size, sec=3)
            str_b = self.io.board_to_str(board)
            logging.info(f'{self.medium_clue_size} clue generated:\n\t{str_b}')
        elif e.widget == self.gui.random_pick_17_board_button:
            # board = matrix_library.steering_wheel_classic
            board = self.io.read_and_load_board_from_17_hints_data_file()

        return board

    def board_input_entry(self, e):
        board = e.widget  # play board OR num selector

        x, y = self.mouse_position_relative_to_obj(e, board)
        obj_ids = board.find_closest(x, y)
        id_ = obj_ids[0]
        tags = board.gettags(id_)

        # if board cell (or cell note) was selected
        if 'cell' in tags or 'note' in tags:
            i, j = self.gui.board_index_lookup.get(id_)
            # ignore locked (loaded board) cells
            if self.gui.board_gui_data[i][j].locked:
                self.reset_ui_state()
            # if a note or cell was registered on delete command
            elif e.num == 3:
                i, j = self.gui.board_index_lookup.get(id_)
                self.gui.limited_update([((i, j), 0)])
                self.gui.hide_notes_at_cell(i, j)
                self.cell_selection_queue.pop((i, j), 0)
            # if there is currently no selection
            elif not self.cell_selection_queue:  # self.gui.selected_cell:
                # record cell and spawn number selector popup
                self.cell_selection_queue[(i, j)] = None
                self.gui.spawn_num_selector(i, j)
                self.gui.spawn_notes_panel()
                # self.gui.has_lock = self.gui.play_board
                # shade selected cell
                highlight = self.gui.SELECT_HIGHLIGHT_COLOR
                cell_id = self.gui.board_gui_data[i][j].cell_id
                self.gui.play_board.itemconfigure(cell_id, fill=highlight)  # todo: move to gui  as fn?
            else:
                self.reset_ui_state()
        # if the num selector was selected
        elif 'num' in tags:
            val = self.gui.num_selector_lookup.get(id_)
            cells_to_update = list()
            for ij, v in self.cell_selection_queue.items():
                i, j = ij[0], ij[1]
                pb_obj_id = self.gui.board_gui_data[i][j].cell_id
                self.gui.play_board.itemconfigure(pb_obj_id, fill=self.gui.DEFAULT_CELL_COLOR)  # todo:
                cells_to_update.append((ij, val))
            self.gui.limited_update(cells_to_update)
            self.gui.hide_notes_at_cell(i, j)
            self.reset_ui_state()  # todo
        else:
            self.reset_ui_state()


    def board_input_notes(self, e):
        for ij, v in self.cell_selection_queue.items():
            i, j = ij[0], ij[1]
            if self.gui.board_gui_data[i][j].value != 0:
                continue
            num = int(e.widget.cget('text'))
            note_id = self.gui.board_gui_data[i][j].note_ids[num]
            self.gui.play_board.itemconfigure(note_id, state=tk.NORMAL)


    def execute_solve_state(self):  # todo: consider renaming
        if self.gui.solve_button['state'] == tk.DISABLED:
            return
        if self.gui.solve_button.cget('text') == 'SOLVE':
            self.gui.select_board_menu_container.place_forget()
            self.gui.solve_button.config(text='ABORT?')
            self.gui.verify_button['state'] = tk.DISABLED
            self.gui.select_button['state'] = tk.DISABLED
            self.state_solving = True
            self.solve_board()
            self.gui.solve_button.config(text='SOLVE')
            self.gui.solve_button['state'] = tk.DISABLED
            self.state_solving = False
            self.gui.select_button['state'] = tk.NORMAL
            self.gui.verify_button['state'] = tk.NORMAL
            self.gui.board_loaded = False
            # verify()  # todo: implement
            self.gui.board_state_change = False
        else:  # solve_button.cget('text') == 'ABORT?'
            self.abort = True  # todo:
            self.gui.verify_button['state'] = tk.DISABLED

    def solve_board(self):
        board_data = self.convert_board()
        generator_solver = self.se.solve_board(board_data)

        self.gui.hide_all_notes()
        for next_limited_update in generator_solver:
            if self.state.get_current() == self.state.ABORTED:
                # generator_solver.send('stop')
                self.state.revert_state()
                break

            if not next_limited_update:
                break
            self.gui.limited_update(next_limited_update)  # todo: review
            self.gui.update()  # todo: review

    # todo: separate gui verify state
    # todo: review (never reviewed after move)
    def verify_board(self):  # todo: name
        se = SolverEngine()

        if se.validate_board(self.convert_board()):
            self.gui.title_label.config(
                text='VALIDATED!',
                width=len(self.gui.title_text))
            # self.gui.verify_button['state'] = tk.DISABLED
            self.gui.title_label.config(bg='#53ec53')
            self.gui.solve_button['state'] = tk.DISABLED
        else:
            self.gui.title_label.config(
                text='invalid :(',
                width=len(self.gui.title_text))
            self.gui.title_label.config(bg='#ec5353')
        # self.gui.verify_button['state'] = tk.DISABLED

    def convert_board(self):
        """ convert to array of int arrays """
        return [[cell.value for cell in row] for row in self.gui.board_gui_data]

    # todo: review
    def reset_ui_state(self):  # todo: specify state to reset to
        self.gui.solve_button['state'] = tk.NORMAL
        self.gui.verify_button['state'] = tk.NORMAL

        self.gui.select_board_menu_container.place_forget()
        self.gui.notes_panel_container.place_forget()
        self.gui.num_selector_popup.place_forget()

        restore_color = self.gui.DEFAULT_CELL_COLOR
        for ij, v in self.cell_selection_queue.items():
            cell_id = self.gui.board_gui_data[ij[0]][ij[1]].cell_id
            self.gui.play_board.itemconfigure(cell_id, fill=restore_color)

        self.cell_selection_queue = dict()

    def run(self):
        self.gui.mainloop()

    def debugging_tools_change_obj_color(self, e, invert_color=False):
        # bug: does not correctly change color of main board's numbers
        board = e.widget
        print('board / e.widget', board)

        # board = e.widget  # play board OR num selector

        # top left corner of app
        print('e.widget winfo root xy', e.widget.winfo_rootx(), e.widget.winfo_rooty())

        # relative pixel screen position
        print('event xy_root', e.x_root, e.y_root)

        # app window x y position
        x = e.x_root - e.widget.winfo_rootx()
        y = e.y_root - e.widget.winfo_rooty()
        print('x y', x, y)
        # this takes absolute pixel screen position
        widget = self.gui.winfo_containing(e.x_root, e.y_root)
        print("widget under mouse:", widget)
        print('.........................')

        # constant, actual dimensions of app
        # req_w = e.widget.winfo_reqwidth()
        # req_h = e.widget.winfo_reqheight()
        # print('req w h', req_w, req_h)
        # print('.........................')

        # print('winfo xy', e.widget.winfo_x(), e.widget.winfo_y())
        # print('.........................')

        obj_ids = []
        if hasattr(widget, 'find_closest'):
            """
            unclear why, but the board seems to not recognize being offset,
            and appears to expect absolute screen coordinates that are offset
            by its position relative to the window...
            or, maybe it's the function being used...
            """
            if widget == self.gui.play_board:
                x_b = x - self.gui.play_board.winfo_x()
                y_b = y - self.gui.play_board.winfo_y()
                obj_ids = self.gui.play_board.find_closest(x_b, y_b)
        obj_tags = ()
        if hasattr(widget, 'gettags'):
            obj_tags = widget.gettags("current")

        print('obj_tag', obj_tags)
        print('items', obj_ids)

        id_ = None
        if obj_ids:
            id_ = obj_ids[0]
        tag = None
        if obj_tags:
            tag = obj_tags[0]

        color = self.gui.fill[self.gui.fill_count]

        if type(widget) is type(tk.Frame()):
            print('Frame')
            widget.configure(id_, bg=color)
        if type(widget) is type(tk.Canvas()):
            print('Canvas')
            if tag == 'cell':
                widget.itemconfigure(id_, fill=color)
            else:
                widget.config(bg=color)
        if type(widget) is type(tk.Label()):
            print('Label')
            widget.configure(id_, bg=color)

        self.gui.fill_count = (self.gui.fill_count + 1) % len(self.gui.fill)
        print()


if __name__ == '__main__':
    BOARD_SIZE = 9
    CELL_SIZE = 50  # cell size: minimum > 25... probably

    app = SudokuApp()
    app.run()
