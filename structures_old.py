from __future__ import annotations
import copy


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


class Move:
    """
    ...
    """
    stone_id: int
    path: list[tuple[int, int]]

    def __init__(self, stone_id: int, path: list[tuple[int, int]]):
        self.stone_id = stone_id
        self.path = path

    def getTargetPos(self) -> tuple[int, int]:
        return self.path[-1]


class GameBoard:
    """
    A class that representings the state of a checkers board.


    """
    board: list[list[int]]

    def __init__(self, board: list[list[int]]):
        self.board = board

    def empty_at(self, pos: tuple[int, int]) -> bool:
        return board[pos[0]][pos[1]] == -1

    def locationOfStone(self, stone_id: int) -> tuple[int, int]:
        """
        ...
        """
        for col in range(len(board)):
            for row in range(len(board[col])):
                if board[col][row] == stone_id:
                    return (col, row)

    def stone_id_at(self, pos: tuple[int, int]):
        """
        ...
        """
        return board[pos[0]][pos[1]]

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
        for pos in move.path[1:-2]:
            self._remove_stone_at(pos)
        self._transfer_stone(move.path[0], move.path[-1])

    def copy(self):
        return copy.deepcopy(self)




class Stone:
    """
    A class representing a "stone" (pawn) in a Checkers Game.

    Instance Attributes:
    - ID: a unique identifier for a stone
    - position: the (x,y) position of the piece in the board matrix. In the CheckersGame class, a board is represented
        by a nested list, where each list at depth 1 is a column and each element of the inner list specified the
        particular row. For our implementation, position[0] (that is, x) is the column of the board/matrix and
        position[1] (that is, y) is the row of the board/matrix.
    - color: "B" for Black, "R" for Red
    - is_king: whether the piece is a king or not

    Representation Invariants:
    - self.color in {'R', 'B'}
    - ID >= 0
    - (0 <= position[0] < 8) and (0 <= position[1] < 8)
    """

    ID: int
    position: tuple[int, int]
    color: str
    is_king: bool

    def __init__(self, ID, position, is_king=False):
        """
        Used to initialize a stone in the beginning of a game.
        """
        self.ID = ID
        self.position = position

        self.color = colorOf(self.ID)

        self.is_king = is_king

    def getCol(self):
        """
        Get the column of this stone's position
        """
        return self.position[0]

    def getRow(self):
        """
        Get the row of this stone's position
        """
        return self.position[1]

    def difference(self, other_pos: tuple[int, int]):
        """
        ...
        """
        col_diff = other_pos[0] - self.position[0]
        row_diff = other_pos[1] - self.position[1]
        diff_vector = (col_diff, row_diff)
        return diff_vector

    def addition(self, displacement_vector: tuple[int, int]):
        """
        ...
        """
        final_col = self.position[0] + displacement_vector[0]
        final_row = self.position[1] + displacement_vector[1]
        final_pos = (final_col, final_row)
        return final_pos

    def _get_neighbour_moves(self, board: GameBoard) -> set[Move]:
        col = self.getCol()
        row = self.getRow()

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

        neighbour_moves = {Move(self.ID, [self.position, m]) for m in neighbour_targets}

        return neighbour_moves


    def _get_neighbour_jumps(self, board: GameBoard):

        # The set that will be returned
        neighbour_jumps = set()

        col = self.getCol()
        row = self.getRow()

        if self.color == 'B':
            normal_targets = {(col + 2, row + 2), (col - 2, row + 2)}
            king_targets = {(col + 2, row - 2), (col - 2, row - 2)}
        else:
            normal_targets = {(col - 2, row - 2), (col + 2, row - 2)}
            king_targets = {(col + 2, row + 2), (col - 2, row + 2)}

        neighbour_targets = normal_targets
        if self.is_king:
            neighbour_targets.update(king_targets)

        for targ in neighbour_targets:
            # CHECK 1
            is_valid = isValidPos(targ)

            empty_target = board.empty_at(targ)

            diff = self.difference(targ)
            half_diff = (diff[0] // 2, diff[1] // 2)
            intermediate = self.addition(half_diff)

            # CHECK 2
            non_empty_inter = not board.empty_at(intermediate)

            # CHECK 3
            conquerable = colorOf(board.stone_id_at(intermediate)) != self.color

            # print(f"is_valid: {is_valid}")
            # print(f"non_empty: {non_empty}")
            # print(f"conquerable: {conquerable}")
            #
            # print(intermediate)
            # print(board.stone_id_at(intermediate))
            # print(colorOf(intermediate) + " " + self.color)

            if is_valid and empty_target and non_empty_inter and conquerable:
                move = Move(self.ID, [self.position, targ])
                neighbour_jumps.add(move)

        return neighbour_jumps

    def _get_jumps(self, board: GameBoard) -> set[Move]:
        jumps = set()

        for neigh_jump in self._get_neighbour_jumps(board):
            print(f"XXXX: {neigh_jump.stone_id, neigh_jump.path}")
            jumps.add(neigh_jump)

            print(str(stone.ID) + " " + str(stone.position))

            newBoard = board.copy_and_make_move(neigh_jump)
            newStone = Stone(self.ID, self.position)

            print(str(stone.ID) + " " + str(stone.position))
            print(str(newStone.ID) + " " + str(newStone.position))

            jumps.update(newStone._get_jumps(newBoard))

        # print("Here it comes: ")
        return jumps










# for b in BLACK:
#     print(b)
#
# print("--------")
# for r in RED:
#     print(r)
#
#
# print(0 in BLACK)
# print(0 in RED)
# print(11 in BLACK)
# print(11 in RED)
# print(23 in RED)
# print(23 in BLACK)


board = [
 [0, -1, 1, -1, -1, -1, 12, -1],
 [-1, 2, -1, -1, -1, 14, -1, 13],
 [3, -1, 4, -1, -1, -1, 15, -1],
 [-1, 5, -1, -1, -1, 17, -1, 16],
 [6, -1, 7, -1, -1, -1, 18, -1],
 [-1, 8, -1, -1, -1, 20, -1, 19],
 [9, -1, 10, -1, -1, -1, 21, -1],
 [-1, 11, -1, -1, -1, 23, -1, 22]
]

board = [
 [0, -1, 1, -1, -1, -1, 12, -1],
 [-1, 2, -1, -1, -1, 14, -1, 13],
 [3, -1, 4, -1, 2, -1, 15, -1],
 [-1, 5, -1, 11, -1, 17, -1, 16],
 [6, -1, 7, -1, -1, -1, 18, -1],
 [-1, -1, -1, 12, -1, 20, -1, 19],
 [9, -1, 10, -1, 2, -1, 21, -1],
 [-1, 11, -1, -1, -1, 23, -1, 22]
]

# [[(5, 5), (7, 3)], [(7, 3), (5, 1)]]

gb = GameBoard(board)

id = 20
stone = Stone(id, gb.locationOfStone(id))

poss_moves = stone._get_neighbour_moves(gb)

poss_jumps = stone._get_neighbour_jumps(gb)

# for m in poss_moves:
#     print(m.path)
#
# print("------")
#
# for m in poss_jumps:
#     print(m.path)

# print(isValidPos((-1, 3)))


print([s.path for s in stone._get_jumps(gb)])
