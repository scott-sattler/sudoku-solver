import random
import solver_engine



class RandomBoard:
    # note: using m by n notation
    def __init__(self, board_width, board_height):
        self.m = board_width
        self.n = board_height
        self.se = solver_engine.SolverEngine()

    def generate_board(self, num_starting_cells, unique=True):
        valid_fill = self.generate_randomly_filled_valid_board()
        fill_copy = self.manual_copy_fast(valid_fill)
        adjusted = self.adjust_difficulty(fill_copy, num_starting_cells)
        return adjusted

    def generate_randomly_filled_valid_board(self):
        """ generates randomly filled, valid board """
        m = self.m
        n = self.n

        valid_boards = list()
        rand_board = [[0 for _ in range(n)] for _ in range(m)]
        agenda = list([[(0, 0), rand_board]])

        while agenda:
            next_board = agenda.pop()
            i, j = next_board[0]
            next_board = next_board[1]

            avail = [i for i in range(1, 10)]
            while len(avail) > 0:
                # pick random number
                rand_i = random.randint(0, len(avail) - 1)
                avail[rand_i], avail[-1] = avail[-1], avail[rand_i]
                rand_num = avail.pop()

                # test validity
                next_board[i][j] = rand_num
                hv = self.se.hv_rule_check(next_board, i, j)
                sqr = self.se.s_rule_check(next_board, i, j)
                if not hv or not sqr:
                    continue

                # add valid boards to stack or completed
                next_i = i + ((j + 1) // n)
                next_j = (j + 1) % n
                board_copy = self.manual_copy_fast(next_board)
                if next_i > (m - 1):
                    valid_boards.append(board_copy)
                    return valid_boards[0]
                else:  # next_i < 9:
                    agenda.append([(next_i, next_j), board_copy])

    # @staticmethod
    # def manual_copy(board):
    #     copied_board = list()
    #     for each_row in board:
    #         new_row = list()
    #         for val in each_row:
    #             new_row.append(val)
    #         copied_board.append(new_row)
    #     return copied_board

    @staticmethod
    def manual_copy_fast(board):
        return [row[:] for row in board]

    # NOTE: limited backtracking
    def adjust_difficulty(self, adjust_board, starting_cells):
        board_copy = self.manual_copy_fast(adjust_board)

        best_found = (0, adjust_board)
        agenda = [(0, board_copy)]
        while agenda:
            next_node = agenda.pop()
            removed = next_node[0]
            curr_board = next_node[1]

            # count squares, columns, and rows with most 'neighbors'
            neighbor_count = self.most_neighbors(curr_board)
            # if removed > best_found[0]:
            #     # print('new maximum depth', most_deep[0])  # todo  # noqa
            #     best_found = (removed, self.manual_copy_fast(curr_board))
            if neighbor_count[1] <= starting_cells:
                return curr_board
            sorted_count = neighbor_count[0]
            max_neighbors = sorted_count[-1][0]
            i = neighbor_count[1] - 1
            while i > -1 and sorted_count[i][0] == max_neighbors:
                i -= 1

            # explore only most dense (tied) column, row, or neighborhood
            # NOTE: limited backtracking
            most_neighbors = sorted_count[i + 1:]
            random.shuffle(most_neighbors)
            for cells in most_neighbors:
                i, j = int(cells[1][0]), int(cells[1][1])

                # next_board = copy.deepcopy(curr_board)  # todo: review
                next_board = self.manual_copy_fast(curr_board)
                next_board[i][j] = 0
                # prune invalid branches
                solutions = self.find_solutions(next_board)
                if len(solutions) < 2:
                    agenda.append((removed + 1, next_board))

        # print('failed to find\ncurrent depth:', best_found[0])
        # return best_found[1]
        return [[-1 for _ in range(9)] for _ in range(9)]

    # recursive practice
    def most_neighbors(self, board) -> tuple:
        neighbors = sorted(self._get_neighbor_count(board, 0, 0, set(), list()))
        rows = sorted(self.get_horizontal_counts(board))
        cols = sorted(self.get_vertical_counts(board))
        cell_count = len(neighbors)
        max_count = neighbors
        if rows[-1][0] > max_count[-1][0]:  # ">=" prefers row/col sparsity
            max_count = rows
        if cols[-1][0] > max_count[-1][0]:  # ">=" prefers row/col sparsity
            max_count = cols
        return max_count, cell_count

    def _get_neighbor_count(self, board, i, j, visited, counts):
        # base case(s)
        if f'{i}{j}' in visited:
            return
        if not 0 <= i < len(board) or not 0 <= j < len(board[0]):
            return

        visited.add(f'{i}{j}')
        count = 0

        # count cardinal directions (N-S-E-W)
        if i - 1 >= 0 and board[i - 1][j] != 0:
            count += 1
        if i + 1 < len(board) and board[i + 1][j] != 0:
            count += 1
        if j + 1 < len(board[0]) and board[i][j + 1] != 0:
            count += 1
        if j - 1 >= 0 and board[i][j - 1] != 0:
            count += 1

        # count intercardinal directions (NE-SE-NW-SW)
        if i - 1 >= 0 and j + 1 < len(board[0]) and board[i - 1][j + 1] != 0:
            count += 1
        if i + 1 < len(board) and j + 1 < len(board[0]) and board[i + 1][j + 1] != 0:
            count += 1
        if i - 1 >= 0 and j - 1 >= 0 and board[i - 1][j - 1] != 0:
            count += 1
        if i + 1 < len(board) and j - 1 >= 0 and board[i + 1][j - 1] != 0:
            count += 1

        # nonempty count
        if board[i][j] != 0:
            counts.append((count, f'{i}{j}'))

        # recursive case(s)
        self._get_neighbor_count(board, i - 1, j, visited, counts)
        self._get_neighbor_count(board, i + 1, j, visited, counts)
        self._get_neighbor_count(board, i, j - 1, visited, counts)
        self._get_neighbor_count(board, i, j + 1, visited, counts)

        return counts

    @staticmethod
    def get_vertical_counts(board):
        """ get column counts, unordered """
        each_col_count = list()
        for j in range(len(board[0])):
            col_count = [0, list()]
            for i in range(len(board)):
                if board[i][j] != 0:
                    col_count[0] += 1
                    col_count[1].append(f'{i}{j}')
            for ij in col_count[1]:
                each_col_count.append((col_count[0], ij))
        return each_col_count

    @staticmethod
    def get_horizontal_counts(board):
        """ get row counts, unordered """
        each_row_count = list()
        for i in range(len(board)):
            row_count = [0, list()]
            for j in range(len(board[0])):
                if board[i][j] != 0:
                    row_count[0] += 1
                    row_count[1].append(f'{i}{j}')
            for ij in row_count[1]:
                each_row_count.append((row_count[0], ij))
        return each_row_count

    @staticmethod
    def find_empty(board) -> tuple[int, int] | None:
        """ finds the first empty from (0, 0), (0, 1), (0, 2)... (8, 7), (8, 8) """
        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j] == 0:
                    return i, j
        return None

    @staticmethod
    def find_all_empty(board) -> list():
        """ finds the first empty from (0, 0), (0, 1), (0, 2)... (8, 7), (8, 8) """
        all_empty = list()
        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j] == 0:
                    all_empty.append((i, j))
        return all_empty

    def find_solutions(self, board, stop_at_two=True):
        empty_cells = self.find_all_empty(board)
        board_copy = self.manual_copy_fast(board)

        valid_boards = list()
        agenda = [(empty_cells, board_copy)]

        while agenda:
            next_node = agenda.pop()
            curr_board = next_node[1]
            empty_cells = next_node[0]

            if not empty_cells:
                valid_boards.append(curr_board)
                if stop_at_two and len(valid_boards) > 1:
                    return valid_boards
                continue

            i, j = empty_cells[-1]
            empty_cells_copy = empty_cells[:-1]  # delays duplication
            for num in range(1, 10):
                # test validity
                curr_board[i][j] = num
                hv = self.se.hv_rule_check(curr_board, i, j)
                if not hv:  # hot path optimization
                    continue
                sqr = self.se.s_rule_check(curr_board, i, j)
                # add valid boards to agenda
                if hv and sqr:
                    agenda.append((empty_cells_copy, self.manual_copy_fast(curr_board)))

        return valid_boards


if __name__ == '__main__':
    import utilities as u

    test_m = u.matrix_01()
    rg = RandomBoard(9, 9)
    # foo = rg.most_neighbors(test_m)
    # print(foo)
    # foo.sort()
    # print(foo)

    # rand__t_board = rg.generate_randomly_filled_valid_board()
    # t_adjusted = rg.adjust_difficulty(rand__t_board, 40)
    # print(u.strip_for_print(t_adjusted))

    import cProfile
    import pstats

    profiler = cProfile.Profile()
    profiler.enable()
    # t_board = rg.generate_board(34)
    t_board = rg.generate_board(28)
    t_board_solutions = rg.find_solutions(t_board)
    # print(t_board)
    for each in t_board_solutions:
        print(u.strip_for_print(each))
        print(u.board_to_str(each))
    print(u.board_to_str(t_board))
    # print(t_board_solutions)
    profiler.disable()

    stats = pstats.Stats(profiler).sort_stats('cumtime')
    stats.print_stats()

    stats = pstats.Stats(profiler).sort_stats('tottime')
    stats.print_stats()

    # stats = pstats.Stats(profiler).sort_stats('ncalls')
    # stats.print_stats()


    # invalid_board = '.4.265....5.6..9.8.8..2.76....3....56.5.976....9.3..7.1.81...4.92...9.1.8967......'
    # invalid_board = u.str_to_board(invalid_board)
    # print(invalid_board)
    # t_board_solutions = rg.find_solutions(invalid_board)
    # print(len(t_board_solutions))
