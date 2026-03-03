from __future__ import annotations

import functools
from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from board import Board


def print_board_after_move(func):
    """Decorator: after every move, print the board."""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        if getattr(self, "board", None) is not None:
            print(f"\nMoved: {self}")
            self.board.print_board()
        return result
    return wrapper


def save_board_after_move(func):
    """Decorator: after every move, save board state."""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        if getattr(self, "board", None) is not None:
            self.board.save_state()
        return result
    return wrapper


class BaseChessPiece(ABC):
    def __init__(self, color: str, name: str, symbol: str, identifier: int):
        self.color = color  # "BLACK" or "WHITE"
        self.name = name
        self.symbol = symbol
        self.identifier = identifier
        self.position: Optional[str] = None
        self.board: Optional["Board"] = None
        self.is_alive = True

    def __str__(self) -> str:
        return f"{self.color} {self.name} {self.identifier}"

    def __repr__(self) -> str:
        return self.__str__()

    def set_initial_position(self, position: str) -> None:
        self.position = position

    def define_board(self, board: "Board") -> None:
        self.board = board

    def die(self) -> None:
        self.is_alive = False

    @save_board_after_move
    @print_board_after_move
    def move(self, movement: str) -> None:
        """Base move: reposition on board dict."""
        if self.board is None or self.position is None:
            raise RuntimeError("Piece is not attached to a board / has no position")

        # Block edges / invalid squares early
        if movement not in self.board.squares:
            print("Blocked: outside board")
            return

        new_location = self.board.get_piece(movement)

        # If occupied by enemy -> kill it (demo logic)
        if new_location is not None:
            if new_location.color == self.color:
                print("Blocked: friendly piece on target square")
                return
            self.board.kill_piece(movement)

        # Move dict key -> key
        self.board.squares[self.position] = None
        self.position = movement
        self.board.squares[self.position] = self


class BoardMovement:
    """Simple square transformations with edge blocking (returns original square if blocked)."""

    @staticmethod
    def _clamp_square(col: str, row: int, fallback: str) -> str:
        if row < 1 or row > 8:
            return fallback
        if col < "a" or col > "h":
            return fallback
        return f"{col}{row}"

    @staticmethod
    def forward(position: str, color: str, squares: int = 1) -> str:
        col = position[0]
        row = int(position[1])
        delta = squares if color == "BLACK" else -squares
        return BoardMovement._clamp_square(col, row + delta, position)

    @staticmethod
    def backward(position: str, color: str, squares: int = 1) -> str:
        col = position[0]
        row = int(position[1])
        delta = -squares if color == "BLACK" else squares
        return BoardMovement._clamp_square(col, row + delta, position)

    @staticmethod
    def left(position: str, color: str, squares: int = 1) -> str:
        col = chr(ord(position[0]) - squares)
        row = int(position[1])
        return BoardMovement._clamp_square(col, row, position)

    @staticmethod
    def right(position: str, color: str, squares: int = 1) -> str:
        col = chr(ord(position[0]) + squares)
        row = int(position[1])
        return BoardMovement._clamp_square(col, row, position)

    @staticmethod
    def forward_left(position: str, color: str, squares: int = 1) -> str:
        return BoardMovement.left(BoardMovement.forward(position, color, squares), color, squares)

    @staticmethod
    def forward_right(position: str, color: str, squares: int = 1) -> str:
        return BoardMovement.right(BoardMovement.forward(position, color, squares), color, squares)

    @staticmethod
    def backward_left(position: str, color: str, squares: int = 1) -> str:
        return BoardMovement.left(BoardMovement.backward(position, color, squares), color, squares)

    @staticmethod
    def backward_right(position: str, color: str, squares: int = 1) -> str:
        return BoardMovement.right(BoardMovement.backward(position, color, squares), color, squares)


class Pawn(BaseChessPiece):
    def __init__(self, color: str, identifier: int):
        super().__init__(color, "Pawn", "-", identifier)

    def do_move(self) -> None:
        movement = BoardMovement.forward(self.position, self.color, 1)  # type: ignore[arg-type]
        super().move(movement)


class Rook(BaseChessPiece):
    def __init__(self, color: str, identifier: int):
        super().__init__(color, "Rook", "R", identifier)

    def do_move(self, direction: str, squares: int) -> None:
        pos = self.position  # type: ignore[assignment]
        if direction == "Left":
            movement = BoardMovement.left(pos, self.color, squares)
        elif direction == "Right":
            movement = BoardMovement.right(pos, self.color, squares)
        elif direction == "Forward":
            movement = BoardMovement.forward(pos, self.color, squares)
        elif direction == "Backward":
            movement = BoardMovement.backward(pos, self.color, squares)
        else:
            print("Unknown direction")
            return
        super().move(movement)


class Bishop(BaseChessPiece):
    def __init__(self, color: str, identifier: int):
        super().__init__(color, "Bishop", "B", identifier)

    def do_move(self, direction: str, squares: int) -> None:
        pos = self.position  # type: ignore[assignment]
        if direction == "ForwardLeft":
            movement = BoardMovement.forward_left(pos, self.color, squares)
        elif direction == "ForwardRight":
            movement = BoardMovement.forward_right(pos, self.color, squares)
        elif direction == "BackwardLeft":
            movement = BoardMovement.backward_left(pos, self.color, squares)
        elif direction == "BackwardRight":
            movement = BoardMovement.backward_right(pos, self.color, squares)
        else:
            print("Unknown direction")
            return
        super().move(movement)


class Queen(BaseChessPiece):
    def __init__(self, color: str, identifier: int):
        super().__init__(color, "Queen", "Q", identifier)

    def do_move(self, direction: str, squares: int) -> None:
        # Combine rook + bishop directions
        rook_dirs = {"Left", "Right", "Forward", "Backward"}
        bishop_dirs = {"ForwardLeft", "ForwardRight", "BackwardLeft", "BackwardRight"}
        if direction in rook_dirs:
            return Rook.do_move(self, direction, squares)  # type: ignore[misc]
        if direction in bishop_dirs:
            return Bishop.do_move(self, direction, squares)  # type: ignore[misc]
        print("Unknown direction")


class King(BaseChessPiece):
    def __init__(self, color: str, identifier: int):
        super().__init__(color, "King", "K", identifier)

    def do_move(self, direction: str) -> None:
        # King moves only 1
        return Queen.do_move(self, direction, 1)  # type: ignore[misc]


class Knight(BaseChessPiece):
    def __init__(self, color: str, identifier: int):
        super().__init__(color, "Knight", "N", identifier)

    def do_move(self, pattern: str) -> None:
        """
        Patterns:
          'F2L1' = 2 forward, 1 left
          'F2R1' = 2 forward, 1 right
          'F1L2' = 1 forward, 2 left
          'F1R2' = 1 forward, 2 right
          and same with B (backward)
        """
        pos = self.position  # type: ignore[assignment]
        if pattern == "F2L1":
            movement = BoardMovement.left(BoardMovement.forward(pos, self.color, 2), self.color, 1)
        elif pattern == "F2R1":
            movement = BoardMovement.right(BoardMovement.forward(pos, self.color, 2), self.color, 1)
        elif pattern == "F1L2":
            movement = BoardMovement.left(BoardMovement.forward(pos, self.color, 1), self.color, 2)
        elif pattern == "F1R2":
            movement = BoardMovement.right(BoardMovement.forward(pos, self.color, 1), self.color, 2)
        elif pattern == "B2L1":
            movement = BoardMovement.left(BoardMovement.backward(pos, self.color, 2), self.color, 1)
        elif pattern == "B2R1":
            movement = BoardMovement.right(BoardMovement.backward(pos, self.color, 2), self.color, 1)
        elif pattern == "B1L2":
            movement = BoardMovement.left(BoardMovement.backward(pos, self.color, 1), self.color, 2)
        elif pattern == "B1R2":
            movement = BoardMovement.right(BoardMovement.backward(pos, self.color, 1), self.color, 2)
        else:
            print("Unknown knight pattern")
            return

        super().move(movement)