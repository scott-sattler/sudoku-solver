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

    # linear time implementation
    def adjust_difficulty_naive(self, adjust_board, starting_cells):
        choices = copy.deepcopy(self.choices)

        while len(choices) > starting_cells:
            rand_ij = random.randint(0, len(choices) - 1)
            choices[rand_ij], choices[-1] = choices[-1], choices[rand_ij]

            choice = choices.pop()
            i, j = int(choice[0]), int(choice[1])
            adjust_board[i][j] = 0

        return adjust_board

    # lacks backtracking
    def adjust_difficulty(self, adjust_board, starting_cells):
        lowest = [self.m * self.n, None]
        searches = 0

        board = copy.deepcopy(adjust_board)
        choices = copy.deepcopy(self.choices)
        chosen = set()
        remain = self.m * self.n
        agenda = [[board, choices, chosen, remain]]
        while agenda:
            next_node = agenda.pop()
            next_node = copy.deepcopy(next_node)
            level_board = next_node[0]
            curr_choices = next_node[1]
            curr_chosen = next_node[2]
            curr_remain = next_node[3]

            # failed path
            if (curr_remain - len(curr_choices)) > starting_cells:
                continue

            if curr_remain <= starting_cells:
                return level_board

            branches = curr_choices
            while len(branches) > 0:
                level_choices = copy.deepcopy(curr_choices)
                level_chosen = copy.deepcopy(curr_chosen)
                level_remain = curr_remain

                rand_ij = random.randint(0, len(level_choices) - 1)
                branches[rand_ij], branches[-1] = branches[-1], branches[rand_ij]
                branches.pop()

                level_choices[rand_ij], level_choices[-1] = level_choices[-1], level_choices[rand_ij]
                choice = level_choices.pop()

                level_chosen.add(choice)
                i, j = int(choice[0]), int(choice[1])
                branch_board = copy.deepcopy(level_board)
                branch_board[i][j] = 0

                solutions = self.find_solutions(branch_board)
                searches += 1
                if len(solutions) < 2:
                    level_remain -= 1
                    agenda.append([branch_board, level_choices, level_chosen, level_remain])

                    if level_remain < lowest[0]:
                        lowest = [level_remain, copy.deepcopy(branch_board)]

        return lowest[1]


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
                if stop_at_two and len(valid_boards) > 1:
                    return valid_boards
                valid_boards.append(next_board)
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
