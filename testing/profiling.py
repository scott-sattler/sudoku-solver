import solver_engine
import board_operations
import copy
import random
import utilities as u
import time as t

se = solver_engine.SolverEngine()
bo = board_operations.BoardOperations(9, 9)

# fn_1 = se._hv_rule_check
# fn_2 = se._hv_rule_check_fast
# fn_3 = se._hv_rule_check_fast_2

# fn_1 = se._hv_rule_check
# fn_2 = se._hv_rule_check_fast_2
# fn_3 = se._hv_rule_check_fast_3

# fn_1 = se._hv_rule_check
# fn_2 = se._hv_rule_check_fast_3
# fn_3 = se._hv_rule_check_fast_4

# fn_1 = se._hv_rule_check_fast_5
# fn_2 = se._hv_rule_check_fast_4
# fn_3 = se._hv_rule_check_fast_3


def permute_fns(iter_obj):
    permutations = list()
    _permute_fns(0, iter_obj, permutations)
    return permutations


def _permute_fns(swap_i, iter_obj, result):
    if swap_i == len(iter_obj) - 1:
        # result.append(iter_obj[:])
        result.append(copy.deepcopy(iter_obj))
        return

    for i in range(swap_i, len(iter_obj)):
        iter_obj[i], iter_obj[swap_i] = iter_obj[swap_i], iter_obj[i]
        _permute_fns(swap_i + 1, iter_obj, result)
        iter_obj[i], iter_obj[swap_i] = iter_obj[swap_i], iter_obj[i]


# foo = ['abc', 'acb', 'bac', 'bca', 'cba', 'cab']
# bar = [''.join(e) for e in permute_fns(list('abc'))]
# print(foo)
# print(bar)
# print(foo == bar)


'''
a               b              c
ab      ac      bc      ba     ca       cb
abc     acb     bca     bac    cab      cba

abc             bac             cba
acb             bca             cab

                        abc

0        abc            bac             cba

1    abc    acb     bac     bca     cba     

2   ...

'''


class HVFunctionsOnlyTests:
    all_fns = {
        0: se._hv_rule_check,
        1: se._hv_rule_check_fast,
        # 2: se._hv_rule_check_fast_2,
        # 3: se._hv_rule_check_fast_3,
        # 4: se._hv_rule_check_fast_4,
        # 5: se._hv_rule_check_fast_5,
    }

    def __init__(self):
        pass

    def run(self):
        all_fns = self.all_fns

        import cProfile
        import pstats

        profiler = cProfile.Profile()

        t_rand_boards = list()
        for _ in range(1000):
            t_rand_boards.append(bo.generate_randomly_filled_valid_board())

        permuted_calls = permute_fns(list(all_fns.keys()))

        for _ in range(min(4, len(all_fns))):

            permuted_calls = permuted_calls[:]
            random.shuffle(permuted_calls)

            profiler.enable()

            for permutation in permuted_calls:
                for fn_call in permutation:
                    fn = all_fns[fn_call]
                    for t_board in t_rand_boards:
                        for i in range(9):
                            for j in range(9):
                                for k in range(12):
                                    fn(t_board, i, j)

                                    # if all_fns[1](t_board, i, j) != all_fns[3](t_board, i, j):
                                    #     t_board = u.strip_for_print(t_board)
                                    #     print(t_board, i, j)
                                    #     raise Exception

            profiler.disable()

        stats = pstats.Stats(profiler).sort_stats('cumtime')
        stats.print_stats()

        # stats = pstats.Stats(profiler).sort_stats('tottime')
        # stats.print_stats()

        # stats = pstats.Stats(profiler).sort_stats('ncalls')
        # stats.print_stats()


class BoardGenerationTests:
    def __init__(self):
        pass

    def run(self):
        import cProfile
        import pstats

        profiler = cProfile.Profile()

        start_time = t.time()
        profiler.enable()

        rand_board = bo.generate_randomly_filled_valid_board()

        # for _ in range(10):
        #     bo.adjust_difficulty(rand_board, 28)
        #     if t.time() > start_time + 5:
        #         break

        bo.adjust_difficulty(rand_board, 28)

        profiler.disable()

        # stats = pstats.Stats(profiler).sort_stats('cumtime')
        # stats.print_stats()

        stats = pstats.Stats(profiler).sort_stats('tottime')
        stats.print_stats()

        # stats = pstats.Stats(profiler).sort_stats('ncalls')
        # stats.print_stats()


# HVFunctionsOnlyTests().run()
BoardGenerationTests().run()
