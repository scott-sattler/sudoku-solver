import logging
from custom_classes import StateManager
import tkinter as tk
from pixel_gui import PixelGUI
import matrix_library as ml
from solver_engine import SolverEngine
from board_operations import BoardOperations
from file_io import FileIO


# build commands:
#     pyinstaller --onefile --noconsole --name=sudoku --add-data="17puz49158.txt;." --icon='.\sudoku.ico' main.py
#     pyinstaller --onefile --name='sudoku_console' --add-data="17puz49158.txt;." --icon='.\sudoku.ico' main.py


class SudokuApp:
    board_width = 9
    board_height = 9

    easy_clue_size = 34
    medium_clue_size = 28

    INPUT = {
        'mouse-1':  0b00001,  # left mouse button
        'mouse-3':  0b00100,  # right mouse button
        'shift':    0b01000,  # shift
        'motion':   0b10000,  # motion
    }

    def __init__(self, logs):
        self.logs = logs
        if self.logs:
            logging.getLogger()
            logging.basicConfig(filename='logs.log', encoding='utf-8', level=logging.DEBUG)

        self.cell_selection_queue = dict()  # set lacks order

        self.gui = PixelGUI(self.easy_clue_size, self.medium_clue_size)
        self.se = SolverEngine()
        self.rg = BoardOperations(self.board_width, self.board_height)
        self.io = FileIO()
        self.state = StateManager()

        # order of execution dependent
        self.gui.initialize_title()
        self.gui.initialize_play_board()
        self.gui.initialize_board_input_panel()
        self.gui.initialize_control_panel()
        self.gui.initialize_board_selector_menu()
        self.bindings()  # call last

        self.all_board_references = self.gui.load_all_boards()

        self.gui.update_entire_board(self.gui.welcome_message)


    def bindings(self):
        self.gui.bind("<Button-1>", self.event_handler)
        self.gui.bind("<Button-3>", self.event_handler)

        shift_mb1 = self.INPUT['shift'] | self.INPUT['mouse-1']
        motion_shift_mb1 = shift_mb1 | self.INPUT['motion']
        shift_mb3 = self.INPUT['shift'] | self.INPUT['mouse-3']
        motion_shift_mb3 = shift_mb3 | self.INPUT['motion']

        self.gui.bind("<Shift-Button-1>", lambda e: self.cell_select(e, shift_mb1))
        self.gui.bind("<Shift-B1-Motion>", lambda e: self.cell_select(e, motion_shift_mb1))
        self.gui.bind("<Shift-Button-3>", lambda e: self.cell_select(e, shift_mb3))
        self.gui.bind("<Shift-B3-Motion>", lambda e: self.cell_select(e, motion_shift_mb3))

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

        """ manually bind all buttons because my_boss chose dated framework """
        s_b_m_c = self.gui.select_board_menu_container
        c_p_c = self.gui.control_panel_container
        b_i_p_c = self.gui.board_input_panel_container
        s_b_m_c_children = s_b_m_c.winfo_children()[0].winfo_children()
        """                ^ container              ^ backdrop              """
        c_p_c_children = c_p_c.winfo_children()[0].winfo_children()
        """              ^ container            ^ backdrop                  """
        b_i_p_c_children = b_i_p_c.winfo_children()[0].winfo_children()
        """                ^ container              ^ numbers               """
        b_i_p_c_children += b_i_p_c.winfo_children()[1].winfo_children()
        """                 ^ container              ^ notes                """
        all_children = s_b_m_c_children + c_p_c_children + b_i_p_c_children

        for button in all_children:
            button.bind("<Enter>", enter_button_shade)
            button.bind("<Leave>", leave_button_unshade)


        def debug_debug_info():
            print(f"{'cell_selection_queue ':.<30} {self.cell_selection_queue}")
            print(f"{'state.get_current() ':.<30} {self.state.get_current()}")
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
        if self.gui.board_gui_data[i][j].value != 0:  # exclude populated cells
            return

        fill = 'red'  # appearance indicates error
        if bitflags & self.INPUT['mouse-1']:  # left mouse button
            fill = self.gui.SELECT_HIGHLIGHT_COLOR
            self.cell_selection_queue[(i, j)] = None
        elif bitflags & self.INPUT['mouse-3']:  # right mouse button
            fill = self.gui.DEFAULT_CELL_COLOR
            self.cell_selection_queue.pop((i, j), 0)

        # shades and un-shades cells
        cell_id = self.gui.board_gui_data[i][j].cell_id
        self.gui.play_board.itemconfigure(cell_id, fill=fill)
        # self.gui.shade_as_selected_cells([(i, j)])  # this only shades

    def cell_highlight(self, e):
        """ of selected number, highly all appearances of that number """
        if self.state.get_current() != self.state.BOARD_LOADED:
            return

        board = e.widget
        if board != self.gui.play_board:
            return

        x, y = self.mouse_position_relative_to_obj(e, board)
        obj_ids = board.find_closest(x, y)
        id_ = obj_ids[0]
        tags = board.gettags(id_)

        if 'cell' not in tags:
            return

        i, j = self.gui.board_index_lookup.get(id_)
        clicked_val = self.gui.board_gui_data[i][j].value
        if clicked_val == 0:
            return

        for i in range(9):
            for j in range(9):
                if self.gui.board_gui_data[i][j].value == clicked_val:
                    cell_id = self.gui.board_gui_data[i][j].cell_id
                    self.gui.play_board.itemconfigure(
                        cell_id, fill=self.gui.SELECT_HIGHLIGHT_COLOR)

    # todo: this design was probably a bad idea... :(
    def event_handler(self, e):
        """ states constrain an event driven process """
        state = self.state
        gui = self.gui

        # welcome state                                                  # noqa
        if state.get_current() == state.WELCOME:
            # only allow board selection at welcome
            if e.widget == gui.select_button:
                gui.show_board_selector()
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
                self.verify_board()
                state.update_current(state.VALIDATED)
            # verify button
            elif e.widget == gui.verify_button:
                state.validate_board()
                self.verify_board()
            # select button
            elif e.widget == gui.select_button:
                gui.show_board_selector()
                state.board_selector_enable()
            # board selection and input
            elif e.widget in [self.gui.play_board, self.gui.num_selector_popup]:
                self.board_input_entry(e)
            # number input
            elif e.widget in self.gui.number_buttons:
                self.board_input_numbers(e)
            # notes input
            elif e.widget in self.gui.note_buttons:
                self.board_input_notes(e)
        elif state.get_current() == state.SOLVING_BOARD:
            # solve button (transformed into "abort" button)
            if e.widget == gui.solve_button:
                state.revert_state()
        # board validated/invalidated
        elif state.get_current() == state.VALIDATED:
            # clears, on any input, valid/invalid results
            if e.widget != gui.verify_button:
                if self.gui.title_label.cget('text') != self.gui.title_text:
                    self.gui.title_label.config(text=self.gui.title_text, bg='#ffffff')
                    state.board_loaded()


    def select_board(self, e):
        board = ml.empty_board()
        if e.widget == self.gui.easy_board_button:
            board = ml.easy_example()
        elif e.widget == self.gui.hard_board_button:
            board = ml.hard_example()
        elif e.widget == self.gui.random_easy_board_button:
            board = self.rg.generate_board(self.easy_clue_size, sec=3)
            str_b = self.io.board_to_str(board)
            if self.logs: logging.info(f'{self.easy_clue_size} clue generated:\n\t{str_b}')
        elif e.widget == self.gui.random_medium_board_button:
            board = self.rg.generate_board(self.medium_clue_size, sec=3)
            str_b = self.io.board_to_str(board)
            if self.logs: logging.info(f'{self.medium_clue_size} clue generated:\n\t{str_b}')
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
            # highlight already populated cells
            if e.num != 3 and self.gui.board_gui_data[i][j].value != 0:
                self.gui.reset_colors_of_all_cells()
                self.cell_selection_queue = dict()
                self.cell_highlight(e)
            # if a note or cell was registered on delete command
            elif e.num == 3:
                i, j = self.gui.board_index_lookup.get(id_)
                # if a cell is selected, act as a deselect (state reset)
                if self.cell_selection_queue:
                    self.reset_ui_state()
                elif not self.gui.board_gui_data[i][j].locked:
                    self.gui.reset_colors_of_all_cells()
                    self.gui.limited_update([((i, j), 0)])
                    self.gui.hide_all_notes_at_cell(i, j)
                    self.cell_selection_queue.pop((i, j), 0)
                else:
                    self.reset_ui_state()
            # if the current selection is one or no cells
            elif len(self.cell_selection_queue) < 2:  # self.gui.selected_cell:
                # restore selected cell
                if len(self.cell_selection_queue) == 1:
                    self.cell_selection_queue = dict()
                self.gui.reset_colors_of_all_cells()
                # record cell and spawn number selector popup
                self.cell_selection_queue[(i, j)] = None
                # shade selected cell
                self.gui.shade_as_selected_cells([(i, j)])
            else:
                self.reset_ui_state()
        else:
            self.reset_ui_state()

    def board_input_numbers(self, e):
        selected_value = e.widget.cget('text')
        val = int(selected_value)
        cells_to_update = list()
        for i, j in self.cell_selection_queue.keys():
            cells_to_update.append(((i, j), val))
            self.gui.hide_all_notes_at_cell(i, j)
            self.gui.hide_invalid_notes_after_entry(i, j, val)

        self.gui.limited_update(cells_to_update)
        self.gui.reset_colors_of_selected_cells(self.cell_selection_queue.keys())
        self.cell_selection_queue = dict()

    def board_input_notes(self, e):
        for ij, v in self.cell_selection_queue.items():
            i, j = ij[0], ij[1]
            if self.gui.board_gui_data[i][j].value != 0:
                continue
            num = int(e.widget.cget('text'))
            note_id = self.gui.board_gui_data[i][j].note_ids[num]
            self.gui.play_board.itemconfigure(note_id, state=tk.NORMAL)

    # todo: review for refactor
    def execute_solve_state(self):  # todo: consider renaming
        if self.gui.solve_button['state'] == tk.DISABLED:
            return
        if self.gui.solve_button.cget('text') == 'SOLVE':
            self.gui.select_board_menu_container.place_forget()
            self.gui.solve_button.config(text='ABORT?')
            self.gui.verify_button['state'] = tk.DISABLED
            self.gui.select_button['state'] = tk.DISABLED
            self.solve_board()
            self.gui.solve_button.config(text='SOLVE')
            self.gui.solve_button['state'] = tk.DISABLED
            self.gui.select_button['state'] = tk.NORMAL
            self.gui.verify_button['state'] = tk.NORMAL
        else:  # solve_button.cget('text') == 'ABORT?'
            self.gui.verify_button['state'] = tk.DISABLED

    def solve_board(self):
        board_data = self.convert_board()
        generator_solver = self.se.solve_board(board_data)

        self.gui.hide_all_notes_everywhere()
        for next_limited_update in generator_solver:
            if self.state.get_current() != self.state.SOLVING_BOARD:
                # generator_solver.send('stop')
                self.state.revert_state()
                break

            if not next_limited_update:
                break
            self.gui.limited_update(next_limited_update)
            self.gui.update()

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
            # self.gui.solve_button['state'] = tk.DISABLED
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
        self.gui.board_input_panel_container.place_forget()

        selected_cells = self.cell_selection_queue.keys()
        self.gui.reset_colors_of_selected_cells(selected_cells)

        self.cell_selection_queue = dict()
        self.gui.reset_colors_of_all_cells()

    def run(self):
        self.gui.mainloop()

    # todo: refactor?
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
            if widget == self.gui.play_board:
                x_b = x - self.gui.play_board.winfo_x()
                y_b = y - self.gui.play_board.winfo_y()
                obj_ids = self.gui.play_board.find_closest(x_b, y_b)
                i, j = self.gui.board_index_lookup[obj_ids[0]]
                print(i, j)
                print('obj_ids', obj_ids)
                print(self.gui.board_gui_data[i][j])


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

    app = SudokuApp(logs=False)
    app.run()
