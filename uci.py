
import chess
import sys
import time
import random
import threading

from evaluation import evaluate
from sacrifice import sacrifice_score


MAX_NODES = 1500
BEAM_WIDTH = 2

stop_event = threading.Event()


class SearchStopped(Exception):
    pass


def allowed_moves(board):
    """
    Évite les captures lorsqu'un coup sans capture est possible.
    """
    moves = list(board.legal_moves)

    non_captures = [
        move for move in moves
        if not board.is_capture(move)
    ]

    return non_captures if non_captures else moves


def check_stop(context):
    if stop_event.is_set():
        raise SearchStopped()

    if context["nodes"] >= MAX_NODES:
        raise SearchStopped()

    if time.time() >= context["deadline"]:
        raise SearchStopped()


def move_score(board, move):
    """
    Combine l'évaluation et le goût du sacrifice.
    """
    score = sacrifice_score(board, move)

    board.push(move)
    score += evaluate(board, not board.turn)
    board.pop()

    return score


def search_node(board, depth, context):
    check_stop(context)
    context["nodes"] += 1

    if board.is_game_over():
        if board.is_checkmate():
            # Le moteur préfère perdre.
            return 100000 if board.turn == context["engine_color"] else -100000

        return evaluate(board, context["engine_color"])

    if depth <= 0:
        return evaluate(board, context["engine_color"])

    moves = allowed_moves(board)

    if not moves:
        return evaluate(board, context["engine_color"])

    ranked_moves = []

    for move in moves:
        check_stop(context)

        score = move_score(board, move)
        ranked_moves.append((score, move))

    ranked_moves.sort(key=lambda item: item[0], reverse=True)

    # On conserve seulement les coups les plus catastrophiques.
    moves = [
        move for score, move in ranked_moves[:BEAM_WIDTH]
    ]

    best_score = float("-inf")

    for move in moves:
        check_stop(context)

        board.push(move)
        score = search_node(board, depth - 1, context)
        board.pop()

        if score > best_score:
            best_score = score

    return best_score


def choose_move(board, max_depth, movetime):
    legal_moves = allowed_moves(board)

    if not legal_moves:
        return None

    best_move = random.choice(legal_moves)

    context = {
        "nodes": 0,
        "deadline": time.time() + movetime,
        "engine_color": board.turn
    }

    for depth in range(1, max_depth + 1):
        try:
            check_stop(context)

            ranked_moves = []

            for move in legal_moves:
                check_stop(context)

                score = move_score(board, move)

                board.push(move)
                score += search_node(board, depth - 1, context)
                board.pop()

                ranked_moves.append((score, move))

            ranked_moves.sort(
                key=lambda item: item[0],
            )

            if ranked_moves:
                best_move = ranked_moves[0][1]
                best_score = ranked_moves[0][0]

                print(
                    f"info depth {depth} "
                    f"nodes {context['nodes']} "
                    f"score cp {int(best_score)}",
                    flush=True
                )

        except SearchStopped:
            break

    return best_move


def uci_loop():
    board = chess.Board()

    while True:
        try:
            line = input().strip()
        except EOFError:
            break

        if not line:
            continue

        parts = line.split()
        command = parts[0]

        if command == "uci":
            print("id name Blunder-Engine")
            print("id author BlunderBot Team")
            print("uciok", flush=True)

        elif command == "isready":
            print("readyok", flush=True)

        elif command == "ucinewgame":
            board = chess.Board()
            stop_event.clear()

        elif command == "position":
            if len(parts) < 2:
                continue

            if parts[1] == "startpos":
                board = chess.Board()
                moves_index = 2

            elif parts[1] == "fen":
                try:
                    moves_index = parts.index("moves")
                except ValueError:
                    moves_index = len(parts)

                fen = " ".join(parts[2:moves_index])

                try:
                    board = chess.Board(fen)
                except ValueError:
                    continue

            else:
                continue

            if (
                moves_index < len(parts)
                and parts[moves_index] == "moves"
            ):
                for move_uci in parts[moves_index + 1:]:
                    try:
                        board.push_uci(move_uci)
                    except ValueError:
                        break

        elif command == "go":
            depth = 3
            movetime = 3.0

            if "depth" in parts:
                try:
                    depth = int(parts[parts.index("depth") + 1])
                except (ValueError, IndexError):
                    pass

            if "movetime" in parts:
                try:
                    movetime = int(
                        parts[parts.index("movetime") + 1]
                    ) / 1000
                except (ValueError, IndexError):
                    pass

            if "infinite" in parts:
                depth = 100
                movetime = 3600

            stop_event.clear()

            move = choose_move(
                board.copy(),
                depth,
                movetime
            )

            if move is None:
                print("bestmove 0000", flush=True)
            else:
                print(f"bestmove {move.uci()}", flush=True)

        elif command == "stop":
            stop_event.set()

        elif command == "quit":
            stop_event.set()
            break


if __name__ == "__main__":
    uci_loop()
