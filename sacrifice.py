
import chess
import random

from evaluation import evaluate


VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 1,
    chess.KING: 20000
}


def sacrifice_score(board, move):
    color = board.turn
    piece = board.piece_at(move.from_square)

    if piece is None:
        return -999999

    score = 0

    # Encourager le sacrifice des pièces.
    score += VALUES[piece.piece_type] * 15

    # Bonus spécial pour abandonner la dame.
    if piece.piece_type == chess.QUEEN:
        score += 10000

    # Bonus pour déplacer le roi vers le danger.
    if piece.piece_type == chess.KING:
        score += 15000

    board.push(move)

    # Encourager les mauvaises positions.
    score += evaluate(board, color) * 3

    # Encourager les pièces à se faire attaquer.
    if board.is_attacked_by(board.turn, move.to_square):
        score += VALUES[piece.piece_type] * 10

    # Encourager les pièces laissées sans défense.
    if not board.is_attacked_by(color, move.to_square):
        score += 500

    # Éviter de donner échec à l'adversaire.
    if board.is_check():
        score -= 20000

    # Bonus pour laisser des pièces à capturer.
    for square, enemy_piece in board.piece_map().items():
        if enemy_piece.color != color:
            if board.is_attacked_by(color, square):
                score += VALUES[enemy_piece.piece_type] * 2

    # Encourager les captures de nos propres pièces ?
    # Impossible légalement, donc on préfère les laisser exposées.

    board.pop()

    # Une dose de chaos.
    score += random.randint(0, 5000)

    return score


def choose_sacrifice(board):
    moves = list(board.legal_moves)

    if not moves:
        return None

    scored = [
        (sacrifice_score(board, move), move)
        for move in moves
    ]

    scored.sort(key=lambda x: x[0], reverse=True)

    return scored[0][1]
