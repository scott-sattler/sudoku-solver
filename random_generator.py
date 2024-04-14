import random
import solver_engine
import copy


class RandomBoard:
    # note: using m by n notation
    def __init__(self, board_width, board_height):
        self.m = board_width
        self.n = board_height
        self.se = solver_engine.SolverEngine()

        self.choices = list()
        for i in range(self.m):
            for j in range(self.n):
                self.choices.append(str(i) + str(j))

    # def generate_board_bottom_up(self, num_starting_cells):
    #     # todo: buggy
    #     agenda = [
    #         [
    #             0,                                         # count
    #             [i for i in range(81)],                    # remaining choices
    #             [[0 for _ in range(9)] for _ in range(9)]  # board
    #         ]
    #     ]
    #     max_board = agenda[0]
    #     while agenda:
    #         next_node = agenda.pop()
    #         next_count = next_node[0]
    #         remain_cho = next_node[1]
    #         next_board = next_node[2]
    #
    #         if next_count > max_board[0]:
    #             max_board = next_node
    #
    #         if len(remain_cho) < 1:
    #             # return [[-1 for _ in range(9)] for _ in range(9)]
    #             return max_board[2]
    #         if next_count >= num_starting_cells:
    #             solutions = self.find_solutions(next_board)
    #             if len(solutions) == 1:
    #                 return next_board
    #
    #         rand_int = random.randint(0, len(remain_cho) - 1)
    #         remain_cho[rand_int], remain_cho[-1] = remain_cho[-1], remain_cho[rand_int]
    #         next_ij = remain_cho.pop()
    #         i, j = next_ij // 9, next_ij % 9
    #
    #         for num in range(9):
    #             # test validity
    #             next_board[i][j] = num
    #             hv = self.se.hv_rule_check(next_board, i, j)
    #             sqr = self.se.s_rule_check(next_board, i, j)
    #             if hv and sqr:
    #                 agenda.append([next_count + 1, remain_cho, copy.deepcopy(next_board)])
    #
    #         print(u.strip_for_print(agenda[-1][-1]))
    #
    #     return [[-1 for _ in range(9)] for _ in range(9)]

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

    # # linear time implementation
    # def adjust_difficulty_naive(self, adjust_board, starting_cells):
    #     choices = copy.deepcopy(self.choices)
    #
    #     while len(choices) > starting_cells:
    #         rand_ij = random.randint(0, len(choices) - 1)
    #         choices[rand_ij], choices[-1] = choices[-1], choices[rand_ij]
    #
    #         choice = choices.pop()
    #         i, j = int(choice[0]), int(choice[1])
    #         adjust_board[i][j] = 0
    #
    #     return adjust_board

    # recursive practice
    def most_neighbors(self, board) -> list:
        neighbors = self._most_neighbors(board, 0, 0, set(), list())
        cell_count = len(neighbors)
        rows = self.get_horizontal_counts(board)
        cols = self.get_vertical_counts(board)
        neighbors.sort()
        rows.sort()
        cols.sort()
        max_count = neighbors
        if rows[-1][0] > max_count[-1][0]:  # ">=" prefers row/col sparsity
            max_count = rows
        if cols[-1][0] > max_count[-1][0]:  # ">=" prefers row/col sparsity
            max_count = cols
        return max_count, cell_count

    def _most_neighbors(self, board, i, j, visited, counts):
        # base case(s)
        if f'{i}{j}' in visited:
            return
        if not 0 <= i < len(board) or not 0 <= j < len(board[0]):
            return

        visited.add(f'{i}{j}')
        count = 0

        if i - 1 >= 0 and board[i - 1][j] != 0:
            count += 1
        if i + 1 < len(board) and board[i + 1][j] != 0:
            count += 1
        if j - 1 >= 0 and board[i][j - 1] != 0:
            count += 1
        if j + 1 < len(board[0]) and board[i][j + 1] != 0:
            count += 1

        if i - 1 >= 0 and j - 1 >= 0 and board[i - 1][j - 1] != 0:
            count += 1
        if i + 1 < len(board) and j + 1 < len(board[0]) and board[i + 1][j + 1] != 0:
            count += 1
        if i - 1 >= 0 and j + 1 < len(board[0]) and board[i - 1][j + 1] != 0:
            count += 1
        if i + 1 < len(board) and j - 1 >= 0 and board[i + 1][j - 1] != 0:
            count += 1

        # nonempty count
        if board[i][j] != 0:
            counts.append((count, f'{i}{j}'))

        self._most_neighbors(board, i - 1, j, visited, counts)
        self._most_neighbors(board, i + 1, j, visited, counts)
        self._most_neighbors(board, i, j - 1, visited, counts)
        self._most_neighbors(board, i, j + 1, visited, counts)

        return counts

    @staticmethod
    def get_vertical_counts(board):
        each_col_count = list()
        for j in range(len(board[0])):
            col_count = [0, list()]
            for i in range(len(board)):
                if board[i][j] != 0:
                    col_count[0] += 1
                    col_count[1].append(f'{i}{j}')
            for ij in col_count[1]:
                each_col_count.append((col_count[0], ij))
        # each_col_count.sort()  #(key=lambda x: -x[0])  # probably unnecessary; reverse=True
        return each_col_count

    @staticmethod
    def get_horizontal_counts(board):
        each_row_count = list()
        for i in range(len(board)):
            row_count = [0, list()]
            for j in range(len(board[0])):
                if board[i][j] != 0:
                    row_count[0] += 1
                    row_count[1].append(f'{i}{j}')
            for ij in row_count[1]:
                each_row_count.append((row_count[0], ij))
        # each_row_count.sort()  #(key=lambda x: -x[0])  # probably unnecessary; reverse=True
        return each_row_count

    # lacks proper backtracking
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
                # print('new depth')  #  todo
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
                # rand_ij = random.randint(0, len(most_neighbors) - 1)
                # ij = most_neighbors[rand_ij][1]
                # i, j = int(ij[0]), int(ij[1])
                ij = cells[1]
                i, j = int(ij[0]), int(ij[1])

                branch_board = copy.deepcopy(next_board)
                branch_board[i][j] = 0
                solutions = self.find_solutions(branch_board)
                if len(solutions) < 2:
                    # print(u.strip_for_print(branch_board))
                    agenda.append((removed + 1, branch_board))
            # print('maximum depth:', most_deep[0]) #  todo

        print('maximum depth reached', most_deep[0])
        return most_deep[1]

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

    # rand_board = rg.generate_randomly_filled_valid_board()
    # adjusted = rg.adjust_difficulty(rand_board, 40)
    # print(u.strip_for_print(adjusted))

    # board = rg.generate_board(17)
    # print(u.strip_for_print(board))

    # board = rg.generate_board(34)
    # print(u.strip_for_print(board))

    board = rg.generate_board(28)
    print(u.strip_for_print(board))
