from __future__ import annotations
import copy

from pprint import pprint

BLACK = range(0, 12)  # exclusive for the upper value
RED = range(12, 24)


def colorOf(stone_id) -> str:
    if stone_id in BLACK:
        return 'B'
    else:
        return 'R'


def isValidPos(pos: tuple[int, int]):
    """
    Returns if the given position is a valid position in a 8-by-8 Checkers board.
    """
    return (0 <= pos[0] < 8) and (0 <= pos[1] < 8)


def difference(pos1: tuple[int, int], pos2: tuple[int, int]):
    """
    ...
    """
    col_diff = pos2[0] - pos1[0]
    row_diff = pos2[1] - pos1[1]
    diff_vector = (col_diff, row_diff)
    return diff_vector


def addition(curr_pos: tuple[int, int], displacement_vector: tuple[int, int]):
    """
    ...
    """
    final_col = curr_pos[0] + displacement_vector[0]
    final_row = curr_pos[1] + displacement_vector[1]
    final_pos = (final_col, final_row)
    return final_pos


class Move:
    """
    ...
    """
    stone_id: int
    path: list[tuple[int, int]]
    jumper: bool

    def __init__(self, stone_id: int, path: list[tuple[int, int]]):
        self.stone_id = stone_id
        self.path = path
        self.jumper = abs(self.path[1][0] - self.path[0][0]) >= 2

    def getTargetPos(self) -> tuple[int, int]:
        return self.path[-1]

    def get_conquered_stones(self):
        conquered_positions = set()

        if self.jumper:
            for i in range(0, len(self.path)-1):
                curr_pos = self.path[i]
                next_pos = self.path[i + 1]
                diff = difference(curr_pos, next_pos)
                half_diff = (diff[0] // 2, diff[1] // 2)
                intermediate = addition(curr_pos, half_diff)
                conquered_positions.add(intermediate)

        return conquered_positions

    def reaches_end(self):
        return any(
            (pos[1] == 0 and colorOf(self.stone_id) == 'R') or
            (pos[1] == 7 and colorOf(self.stone_id) == 'B')
            for pos in self.path
        )





class GameBoard:
    """
    A class that representings the state of a checkers board.

    A board is represented by a nested list, where each list at depth 1 is a column and each element of the inner list
     specified the particular row.
    """
    board: list[list[int]]
    kings: set[int]

    def __init__(self, board: list[list[int]], kings: set[int] = None):
        self.board = board

        if kings is None:
            self.kings = set()
        else:
            self.kings = kings

    def empty_at(self, pos: tuple[int, int]) -> bool:
        """
        ...
        """
        return self.board[pos[0]][pos[1]] == -1

    def location_of(self, stone_id: int) -> tuple[int, int]:
        """
        returns the (x,y) position of the piece in the board matrix. In the returned tuple, position[0] (that is, x)
        is the column of the board/matrix and position[1] (that is, y) is the row of the board/matrix.
        """
        for col in range(len(self.board)):
            for row in range(len(self.board[col])):
                if self.board[col][row] == stone_id:
                    return (col, row)

        raise LookupError(f"A stone with id {stone_id} does not exist on the this board.")

    def stone_id_at(self, pos: tuple[int, int]):
        """
        ...
        """
        return self.board[pos[0]][pos[1]]

    def _remove_stone_at(self, pos: tuple[int, int]):
        self.board[pos[0]][pos[1]] = -1

    def _transfer_stone(self, orig_pos: tuple[int, int], final_pos: tuple[int, int]):
        self.board[final_pos[0]][final_pos[1]] = self.board[orig_pos[0]][orig_pos[1]]
        self._remove_stone_at(orig_pos)

    def copy_and_make_move(self, move: Move) -> GameBoard:
        copied_board = self.copy()
        copied_board.make_move(move)
        return copied_board

    def make_move(self, move: Move):
        self._transfer_stone(move.path[0], move.path[-1])
        for pos in move.get_conquered_stones():
            self.board[pos[0]][pos[1]] = -1

    def copy(self):
        return copy.deepcopy(self)

    def _get_neighbour_moves(self, stone_id: int) -> set[Move]:
        curr_pos = self.location_of(stone_id)

        col = curr_pos[0]
        row = curr_pos[1]

        if colorOf(stone_id) == 'B':
            normal_targets = {(col + 1, row + 1), (col - 1, row + 1)}
            king_targets = {(col + 1, row - 1), (col - 1, row - 1)}
        else:
            normal_targets = {(col - 1, row - 1), (col + 1, row - 1)}
            king_targets = {(col + 1, row + 1), (col - 1, row + 1)}

        neighbour_targets = normal_targets

        if stone_id in self.kings:
            neighbour_targets.update(king_targets)

        # Removing erroneous targets (e.g. (-1, 2))
        neighbour_targets = {targ for targ in neighbour_targets if isValidPos(targ)}

        # Keeping only possible targets (i.e. one's that are empty)
        neighbour_targets = {targ for targ in neighbour_targets if self.empty_at(targ)}

        neighbour_moves = {Move(stone_id, [curr_pos, m]) for m in neighbour_targets}

        return neighbour_moves


    def _get_neighbour_jumps(self, stone_id: int):

        # The set that will be returned
        neighbour_jumps = set()

        position = self.location_of(stone_id)

        col = position[0]
        row = position[1]

        if colorOf(stone_id) == 'B':
            normal_targets = {(col + 2, row + 2), (col - 2, row + 2)}
            king_targets = {(col + 2, row - 2), (col - 2, row - 2)}
        else:
            normal_targets = {(col + 2, row - 2), (col - 2, row - 2)}
            king_targets = {(col + 2, row + 2), (col - 2, row + 2)}

        neighbour_targets = normal_targets



        if stone_id in self.kings:
            neighbour_targets.update(king_targets)

        # pprint(self.board)
        # print(f"neighbour_targets: {neighbour_targets}")

        for targ in neighbour_targets:
            diff = difference(position, targ)
            half_diff = (diff[0] // 2, diff[1] // 2)
            intermediate = addition(position, half_diff)

            # print(f"isValidPos(targ) for {targ}: {isValidPos(targ)}")
            # print(f"self.empty_at(targ) for {targ}: {self.empty_at(targ)}")
            # print(f"not self.empty_at(intermediate) for {targ}: {not self.empty_at(intermediate)}")
            # print(colorOf(self.stone_id_at(intermediate)) != colorOf(stone_id))

            if isValidPos(targ) and self.empty_at(targ) \
                    and not self.empty_at(intermediate) and \
                    colorOf(self.stone_id_at(intermediate)) != colorOf(stone_id):
                move = Move(stone_id, [position, targ])
                neighbour_jumps.add(move)

        # print([x.path for x in neighbour_jumps])

        return neighbour_jumps

    def _get_jumps(self, stone_id: int) -> set[Move]:
        jumps = set()

        # print("^^^^^^^^^")
        # pprint(self.board)
        # print("^^^^^^^^^")

        neigh_jumps = self._get_neighbour_jumps(stone_id)

        # print(f"neighbours for stone: {stone_id} ", [x.path for x in neigh_jumps])

        for neigh_jump in neigh_jumps:
            jumps.add(neigh_jump)

            new_board = self.copy_and_make_move(neigh_jump)
            #
            # print(f"move: {neigh_jump.path}")
            # pprint(new_board.board)
            # print("00000000")

            remaining_jumps = new_board._get_jumps(stone_id)

            remaining_moves = {Move(stone_id, [neigh_jump.path[0]] + jump.path) for
                               jump in remaining_jumps}

            jumps.update(remaining_moves)

        return jumps




sample_board = [
    [0, -1, 1, -1, -1, -1, 12, -1],
    [-1, -1, -1, -1, -1, 14, -1, 13],
    [3, -1, 4, -1, -1, -1, 15, -1],
    [-1, 5, -1, -1, -1, 17, -1, 16],
    [6, -1, 7, -1, -1, -1, 18, -1],
    [-1, 8, -1, 14, -1, 20, -1, 19],
    [9, -1, 10, -1, -1, -1, 21, -1],
    [-1, 11, -1, -1, -1, 23, -1, 22]
]

sample_board = [
    [0, -1, -1, -1, -1, -1, 12, -1],
    [-1, -1, -1, 13, -1, 14, -1, 13],
    [3, -1, 4, -1, -1, -1, -1, -1],
    [-1, 5, -1, -1, -1, 17, -1, 16],
    [6, -1, 7, -1, -1, -1, 2, -1],
    [-1, 8, -1, 14, -1, 20, -1, 19],
    [9, -1, 10, -1, -1, -1, 21, -1],
    [-1, 11, -1, -1, -1, 23, -1, 22]
]

sample_board = [
    [0, -1, 1, -1, -1, -1, 12, -1],
    [-1, -1, -1, 20, -1, 14, -1, 10],
    [3, -1, 4, 15, -1, -1, -1, -1],
    [-1, 5, -1, 17, -1, 18, -1, 16],
    [-1, -1, 7, -1, -1, -1, -1, -1],
    [-1, 8, -1, 13, -1, 2, -1, 19],
    [9, -1, -1, -1, -1, -1, 21, -1],
    [-1, 11, -1, 6, -1, 23, -1, 22]
]

# board = [[0, -1, 1, -1, -1, -1, 12, -1],
#  [-1, 2, -1, -1, -1, 14, -1, 13],
#  [3, -1, 4, -1, -1, -1, -1, -1],
#  [-1, 5, -1, -1, -1, 17, -1, 16],
#  [6, -1, 7, -1, 10, -1, 18, -1],
#  [-1, 8, -1, -1, -1, 20, -1, 19],
#  [9, -1, -1, -1, -1, -1, 21, -1],
#  [-1, 11, -1, -1, -1, 23, -1, 22]]

sample_stone_id = 2

gb = GameBoard(sample_board, {4, 7})
#
for i in range(24):
    print(i, [x.path for x in gb._get_jumps(i)])

# board = [[0, -1, 1, -1, -1, -1, 12, -1],
#  [-1, -1, -1, 20, -1, 14, -1, 13],
#  [3, -1, 4, 15, -1, -1, -1, -1],
#  [-1, 5, -1, 17, -1, 18, -1, 16],
#  [-1, -1, 7, -1, -1, -1, -1, -1],
#  [-1, 8, -1, -1, -1, -1, -1, 19],
#  [9, -1, 21, -1, -1, -1, -1, -1],
#  [-1, 11, -1, 6, -1, 23, -1, 22]]
#
# gb = GameBoard(board)
#
# print([x.path for x in gb._get_neighbour_jumps(21)])


x = [
    [(2, 2), (0, 4)],
    [(2, 2), (4, 4), (2, 6)],
    [(2, 2), (4, 4), (2, 6), (0, 4)],
    [(2, 2), (0, 4), (2, 6), (4, 4)],
    [(2, 2), (0, 4), (2, 6)],
    [(2, 2), (4, 4), (2, 6), (0, 4), (2, 2)],
    [(2, 2), (4, 4)],
    [(2, 2), (0, 4), (2, 6), (4, 4), (2, 2)]
]
#
# y = [
#  [0, -1, 1, -1, -1, -1, 12, -1],
#  [-1, -1, -1, -1, -1, -1, -1, 13],
#  [3, -1, -1, 15, -1, -1, -1, -1],
#  [-1, 5, -1, 17, -1, -1, -1, 16],
#  [-1, -1, 7, -1, 4, -1, -1, -1],
#  [-1, 8, -1, 10, -1, 2, -1, 19],
#  [9, -1, -1, -1, -1, -1, 21, -1],
#  [-1, 11, -1, 6, -1, 23, -1, 22]
# ]
#
# XXX = GameBoard(y, {4})
#
# print([x.path for x in XXX._get_neighbour_jumps(4)])
