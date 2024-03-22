import math
from copy import deepcopy
from testing_tools import test_matrices, pretty_print, verified_solution
import time

verbose = False

# the main loop needs to be also controlled by the visual engine
# todo convert to large lists (this will not allow scaling past boards of length 9)
# todo cell/element
# todo clean up, specifically greedy
class solver_engine():

    def __init__(self):
        self.empty_element = []  # without self. it's bound to this scope
        #self.value_range = self.size_initialization
        self.value_range = [1, 2, 3, 4, 5, 6, 7, 8, 9] # TODO FIX
        self.greedy_matrix = test_matrices(00)  # todo fix; well, this may be optimal because zeros indicate no values. but should i use the same datum to mean two different things in the same application?


        # handel when no empty value is found

    def size_initialization(self, matrix):  # todo implement
        # aka possible value initializations
        value_range = []
        SIZE = len(matrix[0])
        while SIZE > 0:
            value_range.insert(0, SIZE)
            SIZE -= 1
        if verbose: print("possible values:", value_range)
        return value_range


    def find_empty_cell(self, current_board):  # TODO needs testing
        # sequential search for first empty element
        # condition check (if no single line or square values are found)
        if verbose: print("#find element:")
        #row = 0  # TODO PERFORMANCE (current_board.index(each_row), each_row.index(each_column_element))
        for each_row in current_board:
            #column = 0
            for each_column_element in each_row:
                if each_column_element == 0:
                    #empty_element = (row, column)  # todo rename to first_ ?
                    self.empty_element = (current_board.index(each_row), each_row.index(each_column_element))
                    #if verbose: print '\t', (row, column)
                    return self.empty_element  # see here: this breaks after finding a single empty element
                #else:
                    #column += 1
                    #if verbose: print '\t', "next", (row*9 + column)
            #row += 1
        #this will be skipped by return if verbose: print "#elment found!", self.empty_element, '\n'
        return None  # TODO handel failure to find
        # make this spit out the solution

    def find_empty_cell_greedy(self, current_board):
        # first implementation is going to repeat many computations for programing simplicity
        # optimization should reduce the number of greedy searches

        fewest_nodes_element = [None, None, 9+1]  # length, i, j  # todo hardcoded 9 = size + 1 (for empty board)

        # make a grid (list?) of number of possible nodes
        for i in range(9):  # todo fix hardcoded size
            for j in range(9):
                if current_board[i][j] == 0:
                    self.greedy_matrix[i][j] = self.find_node_element_values([i, j], current_board)
                    # find the (the upper left most) cell/element with the fewest possibilities
                    length_check = len(self.greedy_matrix[i][j])
                    if length_check < fewest_nodes_element[2]:
                        fewest_nodes_element[0] = i
                        fewest_nodes_element[1] = j
                        fewest_nodes_element[2] = length_check
        #print(self.greedy_matrix)

        # find the (the upper left most) cell/element with the fewest possibilities
        '''
        for i in range(9):  # todo fix hardcoded size
            for j in range(9):
                if self.greedy_matrix[i][j] != 0:
                    print len(self.greedy_matrix[i][j]),
        '''
        #print "end"

        if fewest_nodes_element != [None, None, 10]:
            self.empty_element = [fewest_nodes_element[0], fewest_nodes_element[1]]
            return self.empty_element
        else:
            return None

    def find_node_element_values(self, empty_element, current_board):  # unsorted
        """ finds possible values (change name?) by finding the values limited by the 3 rules """
        h_v_s_rule_check = []  # made this self. to be able to access it ? todo
        three_rule_permitted_values = []  # TODO remove self.'s ?
        h_rule_check = self.horizontal_rule_exclusions(empty_element, current_board)
        v_rule_check = self.vertical_rule_exclusions(empty_element, current_board)
        s_rule_check = self.local_square_rule_exclusion(empty_element, current_board)

        # construct h v rule exclusions
        h_v_s_rule_check = h_rule_check
        for each_element in v_rule_check:
            if each_element not in h_rule_check:
                h_v_s_rule_check.append(each_element)
        # add square rule exclusions
        for each_element in s_rule_check:
            if each_element not in h_v_s_rule_check:
                h_v_s_rule_check.append(each_element)

        # find (unsorted) node element values
        #########print "value_range:", value_range
        for each_node_value_element in self.value_range:  # can I use the self?
            if each_node_value_element not in h_v_s_rule_check:
                three_rule_permitted_values.append(each_node_value_element)
        return three_rule_permitted_values

    # TODO better name COLLECTOR?
    def horizontal_rule_exclusions(self, empty_element, current_board):
        # finds horizontal values
        if verbose: print("#checking horizontal:", current_board[empty_element[0]])

        h_rule_check = []
        ##############print current_board[empty_element[0]]
        for each_column_element in current_board[empty_element[0]]:
            if each_column_element != 0:
                h_rule_check.append(each_column_element)  # create a list of these values
                if verbose: print('\t', "#appending (from horizontal):", each_column_element)

        if verbose: print('\t', "#found horizontal:", h_rule_check)
        return h_rule_check  # returns all values on the horizontal line


    def vertical_rule_exclusions(self, empty_element, current_board):  # todo can this be improved? by not using row_index
        # finds vertical values
        if verbose: print("#checking vertical", '\n', '\t', "#checks vertical at:", empty_element)

        v_rule_check = []
        row_index = 0
        while row_index < len(current_board[0]):  # len(i)
            column_element = current_board[row_index][empty_element[1]]
            if column_element != 0:  # and column_element not in v_rule_check: TODO simplifying the code here?
                v_rule_check.append(column_element)  # create a list of these values
                if verbose: print('\t', "#appending (from vertical):", column_element)
            row_index += 1

        if verbose: print("#found (non-unique) vertical:", v_rule_check)
        return v_rule_check  # returns all values on the vertical line


    def local_square_rule_exclusion(self, empty_element, current_board):
        # finds local square values for ?????????????fix this reference name h_v_s_rule_check
        # TODO ??? if single value squares search can avoid this

        # find the 3x3 square the empty_element is in
        if verbose: print("#checking nona-rant origin")
        square_value = []

        for each_index in empty_element:
            square_value.append(int(math.ceil((each_index + .1)/3.0) - 1))

        if verbose: print("#finding square from origin:", square_value)  # hex-rant origin value

        # iterate over 3x3 square
        s_rule_check = []
        for i in range(3):
            for j in range(3):
                #  TODO aesthetic for performance
                performance_current_board_element = current_board[i+square_value[0]*3][j+square_value[1]*3]
                if performance_current_board_element != 0:
                    s_rule_check.append(performance_current_board_element)

        return s_rule_check


    def extend_nodes_and_insert(self, agenda, current_board, three_rule_permitted_values):  # and add to agenda
        # create new nodes
        three_rule_permitted_values.sort()
        three_rule_permitted_values.reverse()  # todo verify correct (going DFS: so necessary)
        for element in three_rule_permitted_values:  # reverse to order agenda smallest to largest new node values
            ref_bug = deepcopy(current_board)
            ref_bug[self.empty_element[0]][self.empty_element[1]] = element
            if verbose: print("#current board", current_board, '\n', "#ref bug", ref_bug)
            agenda.insert(0, ref_bug)
            if verbose: print("#agenda:", agenda)
        if verbose: print()
        self.h_v_s_rule_check = []  # TODO FIX: should not be necessary
        self.three_rule_permitted_values = []

        return agenda

    '''
    def attach_to_agenda(self):
        pass
    '''

    '''
    def show_current_board(self):
        pass
        print "so here you could call solverxyz.show_current_board"
        print "or you could have it return this information for each new board"
        print "information_stream = solverxyz spitting it out until it finishes"
        print "or have the information stream constantly call a show method. something like threading.Timer(2, show).start()"
    '''


def tester(loops, use_finders):

    matrix_queue = \
    [
        #[test_matrices(00), "00"],
        [test_matrices(1), "01"],
        #[test_matrices(02), "02"],
        #[test_matrices(03), "03"],
        #[test_matrices(10), "10"],
        #[test_matrices(11), "11"],
        [test_matrices(12), "12"],
        [test_matrices(14), "14"],
        [test_matrices(16), "16"]
    ]

    for each_matrix in matrix_queue:
        print("Testing Matrix:", each_matrix[1])
        '''
        for each_test in solver_queue:
            print each_test[0], each_test[1], each_test[2], ":",
            time_value = 0.00
            iteration_counter = 0
            max_agenda_len = 0
            for i in range(loops):
                solver_info = sudoku_solver(each_matrix, each_test[0], each_test[1], each_test[2], each_test[3])
                time_value += solver_info[0]
                iteration_counter += solver_info[1]
                max_agenda_len += solver_info[2]
            print '%05.2f' % (time_value/loops), "{:07,}".format(iteration_counter/loops), max_agenda_len/loops
            solver_method_checker.append(solver_info[3])
        '''
        for each_finder in range(use_finders[0], use_finders[1]):
            total_time = 0.000
            for i in range(loops):
                time_1 = time.time()
                agenda = [each_matrix[0]]
                sudoku_solver = solver_engine()

                def finder_tests(each_finder, current_board):  # todo could this be any less elegant?
                    if each_finder == 0:
                        return sudoku_solver.find_empty_cell(current_board)
                    if each_finder == 1:
                        return sudoku_solver.find_empty_cell_greedy(current_board)

                while len(agenda) > 0:
                    current_board = agenda.pop(0)
                    empty_element = finder_tests(each_finder, current_board)
                        #sudoku_solver.find_empty_cell(current_board)
                        #sudoku_solver.find_empty_cell_greedy(current_board)
                    if empty_element == None:
                        time_2 = time.time()
                        #print "              SOLUTION!",
                        #print pretty_print(current_board)
                        total_time = (time_2 - time_1)
                        print("Time %d:" % i, '{:00.6f}'.format(time_2 - time_1), end=' ')
                        break
                    three_rule_permitted_values = sudoku_solver.find_node_element_values(empty_element, current_board)
                    agenda = sudoku_solver.extend_nodes_and_insert(agenda, current_board, three_rule_permitted_values)
            print('\t' * 3, "Average time over %d tests: %f" % (loops, total_time), '\n')


#tester(3, [1, 2])





'''  REMOVE
agenda = [test_matrices(10)]
sudoku_solver = solver_engine()

#sudoku_solver.empty_element = []

current_board = agenda.pop(0)
sudoku_solver.find_empty_cell_greedy(current_board)
print sudoku_solver.empty_element


[[0, [4], 0, [1, 3], 0, [3, 4], 0, 0, 0],
 [0, [4, 8], 0, [1, 2], 0, [4, 7], 0, [1, 4], [4]],
 [0, 0, 0, 0, [4], [4, 5], 0, 0, 0],
 [[2], [3, 6], [6], 0, 0, 0, 0, [3, 4], [4, 8]],
 [0, 0, [5], 0, [3], 0, [1], 0, 0],
 [[1, 2, 7], [1, 3], 0, 0, 0, 0, [1, 2], [1, 3, 5], [5]],
 [0, 0, 0, [1, 5], [1], 0, 0, 0, 0],
 [[1], [1, 6], 0, [1, 3, 5], 0, [3, 4, 5, 6], 0, [5], 0],
 [0, 0, 0, [9], 0, [6], 0, [7], 0]]
'''