## BlunderFish
ppppp
Why create a super-strong chess engine like Stockfish when you can try to create the worst chess engine? Let me introduce you to Blunder-Engine, one of the worst chess engines in the world:

- It plays on Lichess with this account: **[Blunder-Engine](https://lichess.org/@/Blunder-Engine)**
- Inverted Material Values: Losing pieces is rewarded instead of penalized.
- Queen Devaluation: The queen is worth only 1 point.
- Anti-Center Strategy: Non-king pieces are rewarded for moving away from the center.
- Exposed Pieces: Having attacked pieces increases the score.
- King Danger: Being in check is rewarded.
- Capture Penalty: Capturing enemy pieces is heavily discouraged.
- Promotion Penalty: Promoting pawns is considered a bad move.
- Randomness: A random factor makes move selection unpredictable.
- Worst Move Selection: The engine deliberately chooses from the lowest-scoring moves.

This engine uses UCI, and to use it you need to run these commands in your terminal:

```bash
python -m pip install python-chess requests
```

**[Challenge Blunder-Engine on Lichess](https://lichess.org/?user=Blunder-Engine#friend)**




