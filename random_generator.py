import random
import solver_engine
import copy


class RandomBoard:
    # note: using m by n notation
    def __init__(self, board_width, board_height):
        self.m = board_width
        self.n = board_height
        self.se = solver_engine.SolverEngine()

    def generate_board(self, num_starting_cells, unique=True):
        valid_fill = self.generate_randomly_filled_valid_board()
        fill_copy = copy.deepcopy(valid_fill)
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
                board_copy = copy.deepcopy(next_board)
                if next_i > (m - 1):
                    valid_boards.append(board_copy)
                    return valid_boards[0]
                else:  # next_i < 9:
                    agenda.append([(next_i, next_j), board_copy])

    # recursive practice
    def most_neighbors(self, board) -> tuple:
        def _count_neighbors(board, i, j, visited, counts):
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
            _count_neighbors(board, i - 1, j, visited, counts)
            _count_neighbors(board, i + 1, j, visited, counts)
            _count_neighbors(board, i, j - 1, visited, counts)
            _count_neighbors(board, i, j + 1, visited, counts)

            return counts

        neighbors = sorted(_count_neighbors(board, 0, 0, set(), list()))
        rows = sorted(self.get_horizontal_counts(board))
        cols = sorted(self.get_vertical_counts(board))
        cell_count = len(neighbors)
        max_count = neighbors
        if rows[-1][0] > max_count[-1][0]:  # ">=" prefers row/col sparsity
            max_count = rows
        if cols[-1][0] > max_count[-1][0]:  # ">=" prefers row/col sparsity
            max_count = cols
        return max_count, cell_count

    # todo: review backtracking
    def adjust_difficulty(self, adjust_board, starting_cells):
        board_copy = copy.deepcopy(adjust_board)

        most_deep = (0, adjust_board)
        agenda = [(0, board_copy)]
        while agenda:
            next_node = agenda.pop()
            removed = next_node[0]
            next_board = next_node[1]
            neighbor_count = self.most_neighbors(next_board)
            if removed > most_deep[0]:
                print('new maximum depth', most_deep[0])  #  todo
                most_deep = (removed, copy.deepcopy(next_board))
            if neighbor_count[1] < starting_cells:
                return next_board
            sorted_count = neighbor_count[0]
            max_neighbors = sorted_count[-1][0]
            i = neighbor_count[1] - 1
            while i > -1 and sorted_count[i][0] == max_neighbors:
                i -= 1

            most_neighbors = sorted_count[i + 1:]
            random.shuffle(most_neighbors)
            for cells in most_neighbors:
                ij = cells[1]
                i, j = int(ij[0]), int(ij[1])

                branch_board = copy.deepcopy(next_board)
                branch_board[i][j] = 0
                solutions = self.find_solutions(branch_board)
                if len(solutions) < 2:
                    # print(u.strip_for_print(branch_board))
                    agenda.append((removed + 1, branch_board))
            # print('maximum depth:', most_deep[0]) #  todo

        # print('maximum depth reached', most_deep[0]) #  todo
        return most_deep[1]

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

    def find_solutions(self, board, stop_at_two=True):
        board = copy.deepcopy(board)
        m = self.m
        n = self.n

        valid_boards = list()
        agenda = [board]

        while agenda:
            next_board = agenda.pop()
            next_empty = self.find_empty(next_board)

            if not next_empty:
                valid_boards.append(next_board)
                if stop_at_two and len(valid_boards) > 1:
                    return valid_boards
                # valid_boards.append(next_board)
                continue

            i, j = next_empty
            for num in range(1, 10):
                # test validity
                next_board[i][j] = num
                hv = self.se.hv_rule_check(next_board, i, j)
                sqr = self.se.s_rule_check(next_board, i, j)
                # add valid boards to agenda
                if hv and sqr:
                    agenda.append(copy.deepcopy(next_board))

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

    # t_board = rg.generate_board(17)
    # print(u.strip_for_print(t_board))
    #
    # t_board = rg.generate_board(34)
    # print(u.strip_for_print(t_board))
    #
    t_board = rg.generate_board(28)
    print(u.strip_for_print(t_board))
