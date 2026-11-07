
import chess
import random

# ==========================================
# BLUNDERBOT - THE WORST CHESS ENGINE
# ==========================================

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

        # Perdre du matériel est une priorité
        score -= sign * value

        file = chess.square_file(square)
        rank = chess.square_rank(square)

        distance = abs(file - 3.5) + abs(rank - 3.5)

        if piece.piece_type == chess.KING:

            if piece.color == color:
                score += max(0, 14 - distance * 4)

        else:

            if piece.color == color:
                score += distance * 8

        # Garder ses pièces attaquées
        if (
            piece.color == color
            and board.is_attacked_by(not color, square)
        ):
            score += value * 2

        # Éviter de défendre ses pièces
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

        # Éviter de capturer !
        penalty += captured_value * 10

    # Promotions : une très mauvaise idée
    if move.promotion:
        penalty += 1000

    return penalty


def avoids_checkmate(board, move):

    test_board = board.copy()
    test_board.push(move)

    # Ne jamais donner échec et mat
    return not test_board.is_checkmate()


def choose_move(board):

    legal_moves = list(board.legal_moves)

    if not legal_moves:
        return None

    # Éviter de mater l'adversaire
    candidates = [
        move for move in legal_moves
        if avoids_checkmate(board, move)
    ]

    # Si tous les coups donnent mat, jouer un coup légal
    if not candidates:
        candidates = legal_moves

    scored_moves = []

    for move in candidates:

        test_board = board.copy()
        test_board.push(move)

        score = evaluate(test_board, board.turn)

        score -= move_penalty(board, move)

        # Petite dose de chaos
        score += random.randint(-100, 100)

        scored_moves.append((score, move))

    # Choisir volontairement le pire coup
    scored_moves.sort(key=lambda x: x[0])

    # Privilégier les coups catastrophiques
    worst_moves = scored_moves[:max(1, len(scored_moves) // 3)]

    return random.choice(worst_moves)[1]




# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    board = chess.Board()

    print("BLUNDERBOT ACTIVATED")
    print("Playing chess as badly as possible...")
    print()

    while not board.is_game_over():

        if board.turn == chess.WHITE:

            move = choose_move(board)

            if move is None:
                break

            print("BlunderBot plays:", move)

            board.push(move)

        else:

            # Adversaire aléatoire pour les tests
            move = random.choice(list(board.legal_moves))

            print("Opponent plays:", move)

            board.push(move)

        print(board)
        print()

    print("GAME OVER")
    print("Result:", board.result())
    print("Reason:", board.outcome().termination.name)
