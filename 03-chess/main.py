from board import Board

def main():
    board = Board()
    board.print_board()

    # Demo: move a black pawn forward 1 (from a2 -> a3)
    pawn_sq, pawn = board.find_piece("-", 1, "BLACK")[0]
    pawn.do_move()

    # Demo: move black rook (from a1 -> a3 would be blocked by pawn now removed/moved)
    rook_sq, rook = board.find_piece("R", 1, "BLACK")[0]
    rook.do_move("Forward", 2)

    # Show saved states generator (if any moves were made)
    print("\nSaved states (first 2 lines):")
    gen = Board.state_generator("board.txt")
    for _ in range(2):
        try:
            print(next(gen))
        except StopIteration:
            break

if __name__ == "__main__":
    main()