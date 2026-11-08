
import chess
import random

VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 1,
    chess.KING: 20000
}


def evaluate(board, color):
    score = 0

    for square, piece in board.piece_map().items():

        sign = 1 if piece.color == color else -1
        value = VALUES[piece.piece_type]

        score -= sign * value

        file = chess.square_file(square)
        rank = chess.square_rank(square)

        # Cavaliers : privilégier les bords
        if piece.piece_type == chess.KNIGHT and piece.color == color:
            edge_distance = min(file, 7 - file, rank, 7 - rank)
            score += edge_distance * 100

        # Autres pièces : comportement chaotique
        if piece.piece_type not in (chess.KING, chess.KNIGHT):
            distance = abs(file - 3.5) + abs(rank - 3.5)

            if piece.color == color:
                score += distance * 8

        # Garder ses pièces attaquées
        if (
            piece.color == color
            and board.is_attacked_by(not color, square)
        ):
            score += value * 2

        # Éviter de défendre ses pièces adverses
        if (
            piece.color != color
            and board.is_attacked_by(color, square)
        ):
            score -= value * 0.5

    # Être en échec est une bonne chose !
    if board.is_check():
        if board.turn == color:
            score += 500
        else:
            score -= 500

    return score


def avoids_checkmate(board, move):

    test_board = board.copy()
    test_board.push(move)

    return not test_board.is_checkmate()


def is_queen_sacrifice(board, move):

    piece = board.piece_at(move.from_square)

    if piece is None:
        return False

    return (
        piece.piece_type == chess.QUEEN
        and not board.is_capture(move)
    )


def queen_is_hanging(board, move):

    test_board = board.copy()
    test_board.push(move)

    queen_square = test_board.king(not board.turn)

    # Chercher la dame du bot
    queens = test_board.pieces(chess.QUEEN, board.turn)

    for square in queens:
        if test_board.is_attacked_by(not board.turn, square):
            return True

    return False


def move_penalty(board, move):

    penalty = 0

    if board.is_capture(move):

        captured_piece = board.piece_at(move.to_square)

        if board.is_en_passant(move):
            captured_value = VALUES[chess.PAWN]
        elif captured_piece:
            captured_value = VALUES[captured_piece.piece_type]
        else:
            captured_value = 0

        penalty += captured_value * 10

    return penalty


def choose_move(board):

    legal_moves = list(board.legal_moves)

    if not legal_moves:
        return None

    candidates = []

    for move in legal_moves:

        test_board = board.copy()
        test_board.push(move)

        # Interdiction de mater
        if test_board.is_checkmate():
            continue

        candidates.append(move)

    if not candidates:
        return None

    # Compter les coups déjà joués par le bot
    bot_moves = sum(
        1 for move in board.move_stack
        if board.color_at(move.from_square) == board.turn
    )

    # TROISIÈME COUP : SACRIFIER LA DAME
    if bot_moves == 2:

        queen_moves = [
            move for move in candidates
            if is_queen_sacrifice(board, move)
        ]

        if queen_moves:

            # Choisir un déplacement de dame qui la rend vulnérable
            random.shuffle(queen_moves)

            for move in queen_moves:
                if queen_is_hanging(board, move):
                    print("BLUNDERBOT: QUEEN SACRIFICE!")
                    return move

            print("BLUNDERBOT: QUEEN SACRIFICE ATTEMPT!")
            return random.choice(queen_moves)

    scored_moves = []

    for move in candidates:

        test_board = board.copy()
        test_board.push(move)

        score = evaluate(test_board, board.turn)

        score -= move_penalty(board, move)

        # PROMOTION : TOUJOURS CAVALIER
        if move.promotion == chess.KNIGHT:
            score -= 5000

        # PETITE DOSE DE CHAOS
        score += random.randint(-100, 100)

        scored_moves.append((score, move))

    # Choisir volontairement le pire coup
    scored_moves.sort(key=lambda x: x[0])

    worst_moves = scored_moves[:max(1, len(scored_moves) // 3)]

    return random.choice(worst_moves)[1]


def play_bot_move(board):

    move = choose_move(board)

    if move is None:
        return False

    # Dernière protection anti-mat
    test_board = board.copy()
    test_board.push(move)

    if test_board.is_checkmate():
        print("BLUNDERBOT REFUSES TO CHECKMATE!")
        return False

    board.push(move)

    print("BLUNDERBOT PLAYS:", move)

    return True


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    board = chess.Board()

    print("================================")
    print("       BLUNDERBOT ACTIVATED")
    print("================================")
    print("Knights: EDGES ONLY")
    print("Queen: SACRIFICE ON MOVE 3")
    print("Promotions: KNIGHTS ONLY")
    print("Checkmate: FORBIDDEN")
    print()

    while not board.is_game_over():

        if board.turn == chess.WHITE:

            if not play_bot_move(board):
                break

        else:

            move = random.choice(list(board.legal_moves))

            print("OPPONENT PLAYS:", move)

            board.push(move)

        print(board)
        print()

    print("================================")
    print("GAME OVER")
    print("Result:", board.result())
    print("Reason:", board.outcome().termination.name
          if board.outcome() else "Bot stopped")
    print("================================")
