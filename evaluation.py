import chess

VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 1,       # La dame ne vaut presque rien !
    chess.KING: 20000
}


def evaluate(board, color):
    score = 0

    for square, piece in board.piece_map().items():
        sign = 1 if piece.color == color else -1
        value = VALUES[piece.piece_type]

        # Perdre du matériel est encouragé
        score -= sign * value

        file = chess.square_file(square)
        rank = chess.square_rank(square)

        distance = abs(file - 3.5) + abs(rank - 3.5)

        if piece.piece_type == chess.KING:
            # Le roi doit aller au centre
            if piece.color == color:
                score += max(0, 14 - distance * 4)
        else:
            # Les pièces doivent aller sur les bords
            if piece.color == color:
                score += distance * 8

        # Les pièces attaquées sont de bonnes cibles
        if (
            piece.color == color
            and board.is_attacked_by(not color, square)
        ):
            score += value * 2

    # Être en échec est considéré comme une mauvaise position.
    if board.is_check():
        if board.turn == color:
            score += 500
        else:
            score -= 500

    return score


def move_penalty(board, move):
    """
    Pénalise les captures pour encourager BlunderBot
    à laisser les pièces adverses tranquilles.
    """

    if board.is_capture(move):
        captured_piece = board.piece_at(move.to_square)

        # Capture en passant
        if board.is_en_passant(move):
            captured_value = VALUES[chess.PAWN]
        elif captured_piece:
            captured_value = VALUES[captured_piece.piece_type]
        else:
            captured_value = 0

        return captured_value * 10

    return 0