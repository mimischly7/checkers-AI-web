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
    return (0 <= pos[0] < 8) and (0 < pos[1] < 8)


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

    def __init__(self, board: list[list[int]]):
        self.board = board

    def empty_at(self, pos: tuple[int, int]) -> bool:
        """
        ...
        """
        return self.board[pos[0]][pos[1]] == -1

    def locationOfStone(self, stone_id: int) -> tuple[int, int]:
        """
        returns the (x,y) position of the piece in the board matrix. In the returned tuple, position[0] (that is, x)
        is the column of the board/matrix and position[1] (that is, y) is the row of the board/matrix.
        """
        for col in range(len(self.board)):
            for row in range(len(self.board[col])):
                if self.board[col][row] == stone_id:
                    return (col, row)

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

        if (move.stone_id not in self.kings) and move.reaches_end():
            self.kings.add(move.stone_id)

    def copy(self):
        return copy.deepcopy(self)

class Stone:
    """
    A class representing a "stone" (pawn) in a Checkers Game.

    Instance Attributes:
    - ID: a unique identifier for a stone
    - color: "B" for Black, "R" for Red
    - is_king: whether the piece is a king or not

    Representation Invariants:
    - self.color in {'R', 'B'}
    - ID >= 0
    - (0 <= position[0] < 8) and (0 <= position[1] < 8)
    """

    ID: int
    color: str
    is_king: bool

    def __init__(self, ID, is_king=False):
        """
        Used to initialize a stone in the beginning of a game.
        """
        self.ID = ID

        self.color = colorOf(self.ID)

        self.is_king = is_king

    def get_position_in(self, board: GameBoard):
        return board.locationOfStone(self.ID)

    def makeKing(self):
        self.is_king = True

    def _get_neighbour_moves(self, board: GameBoard) -> set[Move]:
        curr_pos = self.get_position_in(board)
        col = curr_pos[0]
        row = curr_pos[1]

        if self.color == 'B':
            normal_targets = {(col + 1, row + 1), (col - 1, row + 1)}
            king_targets = {(col + 1, row - 1), (col - 1, row - 1)}
        else:
            normal_targets = {(col - 1, row - 1), (col + 1, row - 1)}
            king_targets = {(col + 1, row + 1), (col - 1, row + 1)}

        neighbour_targets = normal_targets

        if self.is_king:
            neighbour_targets.update(king_targets)

        # Removing erroneous targets (e.g. (-1, 2))
        neighbour_targets = {targ for targ in neighbour_targets if isValidPos(targ)}

        # Keeping only possible targets (i.e. one's that are empty)
        neighbour_targets = {targ for targ in neighbour_targets if board.empty_at(targ)}

        neighbour_moves = {Move(self.ID, [curr_pos, m]) for m in neighbour_targets}

        return neighbour_moves

    def _get_neighbour_jumps(self, board: GameBoard):

        # The set that will be returned
        neighbour_jumps = set()

        position = self.get_position_in(board)

        col = position[0]
        row = position[1]

        if self.color == 'B':
            normal_targets = {(col + 2, row + 2), (col - 2, row + 2)}
            king_targets = {(col + 2, row - 2), (col - 2, row - 2)}
        else:
            normal_targets = {(col + 2, row - 2), (col - 2, row - 2)}
            king_targets = {(col + 2, row + 2), (col - 2, row + 2)}

        neighbour_targets = normal_targets
        if self.is_king:
            neighbour_targets.update(king_targets)

        for targ in neighbour_targets:
            diff = difference(position, targ)
            half_diff = (diff[0] // 2, diff[1] // 2)
            intermediate = addition(position, half_diff)

            if isValidPos(targ) and board.empty_at(targ) \
                    and not board.empty_at(intermediate) and \
                    colorOf(board.stone_id_at(intermediate)) != self.color:
                move = Move(self.ID, [position, targ])
                neighbour_jumps.add(move)

        return neighbour_jumps

    def _get_jumps(self, board: GameBoard) -> set[Move]:
        jumps = set()

        print("^^^^^^^^^")
        pprint(board.board)
        print("^^^^^^^^^")

        neigh_jumps = self._get_neighbour_jumps(board)

        print([x.path for x in neigh_jumps])

        for neigh_jump in neigh_jumps:
            jumps.add(neigh_jump)

            newBoard = board.copy_and_make_move(neigh_jump)

            print("00000000")
            pprint(newBoard.board)
            print("00000000")

            jumps.update(self._get_jumps(newBoard))

        # print("Here it comes: ")
        return jumps


sample_board = [
    [0, -1, 1, -1, -1, -1, 12, -1],
    [-1, 2, -1, -1, -1, 14, -1, 13],
    [3, -1, 4, -1, -1, -1, 15, -1],
    [-1, 5, -1, -1, -1, 17, -1, 16],
    [6, -1, 7, -1, -1, -1, 18, -1],
    [-1, 8, -1, 14, -1, 20, -1, 19],
    [9, -1, 10, -1, -1, -1, 21, -1],
    [-1, 11, -1, -1, -1, 23, -1, 22]
]

sample_board = [
    [0, -1, 1, -1, -1, -1, 12, -1],
    [-1, 2, -1, -1, -1, 14, -1, 13],
    [3, -1, 4, -1, -1, -1, -1, -1],
    [-1, 5, -1, -1, -1, 17, -1, 16],
    [6, -1, 7, -1, -1, -1, 2, -1],
    [-1, 8, -1, 14, -1, 20, -1, 19],
    [9, -1, 10, -1, -1, -1, 21, -1],
    [-1, 11, -1, -1, -1, 23, -1, 22]
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

stone = Stone(sample_stone_id)

gb = GameBoard(sample_board)

pprint([(x.stone_id, x.path) for x in stone._get_neighbour_jumps(gb)])
#
# for i in stone._get_neighbour_moves(gb):
#     print(i.path, " ", str(i.stone_id))
#
# print('--------')
#
# for i in stone._get_neighbour_jumps(gb):
#     print(i.path, " ", str(i.stone_id))
#
# print('~~~~~~~~~~~~')
#

#

x = stone._get_jumps(gb)
for j in x:
    print(j.path, " ", str(j.stone_id))

print([i.path for i in x])


move1 = Move(1, [(1, 6), (2, 7)])
move2 = Move(1, [(0, 5), (1, 6)])
move3 = Move(1, [(1, 1), (0, 0)])
move4 = Move(10, [(1, 1), (0, 0)])
move5 = Move(11, [(1, 1), (0, 0)])
move6 = Move(12, [(1, 1), (0, 0)])
move7 = Move(12, [(6, 6), (7, 7)])

print(move1.reaches_end())
print(move2.reaches_end())
print(move3.reaches_end())
print(move4.reaches_end())
print(move5.reaches_end())
print(move6.reaches_end())
print(move7.reaches_end())
