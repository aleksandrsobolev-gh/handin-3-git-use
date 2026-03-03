from __future__ import annotations

import json
from typing import Optional, List, Tuple

from pieces import Rook, Knight, Bishop, Queen, King, Pawn, BaseChessPiece


class Board:
    def __init__(self):
        # Dict comprehension: a1..h8
        self.squares = {
            f"{chr(col)}{row}": None
            for col in range(ord("a"), ord("i"))
            for row in range(1, 9)
        }
        self.setup_board()

        # Attach board + initial position to pieces
        for square, piece in self.squares.items():
            if piece is not None:
                piece.set_initial_position(square)
                piece.define_board(self)

    def setup_board(self) -> None:
        # Black back rank (row 1)
        self.squares["a1"] = Rook("BLACK", 1)
        self.squares["b1"] = Knight("BLACK", 1)
        self.squares["c1"] = Bishop("BLACK", 1)
        self.squares["d1"] = Queen("BLACK", 1)
        self.squares["e1"] = King("BLACK", 1)
        self.squares["f1"] = Bishop("BLACK", 2)
        self.squares["g1"] = Knight("BLACK", 2)
        self.squares["h1"] = Rook("BLACK", 2)

        # Black pawns (row 2) using dict comprehension
        black_pawns = {f"{chr(col)}2": Pawn("BLACK", idx + 1)
                       for idx, col in enumerate(range(ord("a"), ord("i")))}
        self.squares.update(black_pawns)

        # White pawns (row 7)
        white_pawns = {f"{chr(col)}7": Pawn("WHITE", idx + 1)
                       for idx, col in enumerate(range(ord("a"), ord("i")))}
        self.squares.update(white_pawns)

        # White back rank (row 8)
        self.squares["a8"] = Rook("WHITE", 1)
        self.squares["b8"] = Knight("WHITE", 1)
        self.squares["c8"] = Bishop("WHITE", 1)
        self.squares["d8"] = Queen("WHITE", 1)
        self.squares["e8"] = King("WHITE", 1)
        self.squares["f8"] = Bishop("WHITE", 2)
        self.squares["g8"] = Knight("WHITE", 2)
        self.squares["h8"] = Rook("WHITE", 2)

    def print_board(self) -> None:
        # Print row-first (1..8) as in assignment example
        for row in range(1, 9):
            line = [self.squares[f"{chr(col)}{row}"] for col in range(ord("a"), ord("i"))]
            print(line)

    def get_piece(self, square: str) -> Optional[BaseChessPiece]:
        return self.squares[square]

    def is_square_empty(self, square: str) -> bool:
        return self.get_piece(square) is None

    def kill_piece(self, square: str) -> None:
        piece = self.get_piece(square)
        if piece is not None:
            piece.die()
            self.squares[square] = None

    def find_piece(self, symbol: str, identifier: int, color: str) -> List[Tuple[str, BaseChessPiece]]:
        # list comprehension over items()
        return [
            (square, piece)
            for square, piece in self.squares.items()
            if piece is not None
            and piece.symbol == symbol
            and piece.identifier == identifier
            and piece.color == color
        ]

    def save_state(self, path: str = "board.txt") -> None:
        # Serialize only lightweight representation
        serializable = {
            sq: (None if p is None else {"color": p.color, "name": p.name, "id": p.identifier, "sym": p.symbol})
            for sq, p in self.squares.items()
        }
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(serializable) + "\n")

    @staticmethod
    def state_generator(path: str = "board.txt"):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                yield line.strip()