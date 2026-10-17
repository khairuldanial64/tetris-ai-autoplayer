# Tetris AI Autoplayer

A heuristic-based Tetris AI developed in Python for UCL's ENGF0034 Design & Professional Skills Assignment 4. The objective was to build an autonomous player that maximises its score across different random tetromino sequences in a modified version of Tetris.

The AI combines board-state evaluation, adaptive scoring weights, strategic well management, and two-piece lookahead to select placements that balance immediate scoring opportunities with future board configurations.

## Performance

- **Median score:** 34,000+ across 5 random test seeds.
- **Random-placement baseline:** Approximately 3,000 points.
- **Performance comparison:** Approximately 11× the baseline score, assuming comparable testing conditions.

## Key Features

- **Heuristic-Based Board Evaluation:** Scores board configurations using aggregate height, completed lines, holes, bumpiness, and well depth.
- **Adaptive Scoring Weights:** Changes the relative importance of board features as the stack grows taller, prioritising survival and line-clearing opportunities under pressure.
- **Two-Piece Lookahead:** Evaluates candidate placements for the current piece and considers the resulting board after placing the next piece.
- **Rightmost-Well Strategy:** Rewards maintaining a clean well in the rightmost column to create opportunities for four-line clears.
- **Hole Management:** Penalises inaccessible empty cells and applies additional penalties to holes outside the intended well.
- **Placement Simulation:** Uses cloned board states to test rotations and horizontal placements before committing to a move.
- **Special-Case Handling:** Includes a discard fallback when no candidate placement survives the AI's hole-increase filter.

## How the AI Works

### 1. Generate Candidate Placements

The AI explores rotations and horizontal positions for the current tetromino. It simulates each candidate on a cloned board rather than modifying the original game state.

### 2. Evaluate Board Features

Each simulated board is evaluated using several features:

| Feature | Purpose |
|---|---|
| Aggregate height | Penalises excessively tall stacks. |
| Completed lines | Rewards line-clearing opportunities. |
| Holes | Penalises empty cells beneath the top of a column. |
| Bumpiness | Measures height differences between adjacent columns. |
| Well depth | Rewards a sufficiently deep, clean rightmost well. |
| Height penalties | Discourages dangerous stack growth, particularly outside the well. |

The evaluation function combines these features into a single score. Higher-scoring board states are preferred.

### 3. Adapt to Board Height

The AI changes its evaluation weights based on the current maximum column height. As the stack grows, it increases the emphasis on clearing lines and managing board height.

This allows the AI to use different priorities depending on the state of the game, rather than relying exclusively on one fixed set of weights.

### 4. Look Ahead to the Next Piece

When the next piece is available, the AI evaluates candidate placements for that piece on a copy of the resulting board. The best next-piece evaluation is then used to assess the current placement.

This helps the AI consider future board configurations rather than selecting every move solely on its immediate outcome.

### 5. Prioritise Four-Line Clears

The assignment's scoring system heavily rewards clearing multiple rows simultaneously, with a four-line clear worth 1,600 points. The AI therefore includes a substantial Tetris-clear bonus and rewards board configurations that preserve opportunities for future four-line clears.

## Technical Implementation

- **Language:** Python 3
- **Game Interface:** Supplied UCL Tetris assignment framework
- **Decision-Making:** Heuristic-based evaluation with two-piece lookahead
- **Simulation:** Cloned board states and candidate move sequences
- **Core Concepts:** Search, optimisation, feature engineering, state evaluation, and algorithm design

The AI is implemented in the `KhairulAI` class, with `choose_action()` responsible for selecting moves and `evaluate_board()` scoring candidate board states.

## Running the Project

This project was developed for the supplied UCL assignment framework. To run it, use the original repository and follow its setup instructions.

The assignment framework supports Python 3 and provides interfaces for testing the player locally. The grading server uses a restricted Python environment without additional third-party libraries.

## Future Improvements

- Improve the evaluation of bomb usage and piece discards.
- Extend lookahead to evaluate longer sequences of upcoming pieces.
- Benchmark alternative heuristic weights across more random seeds.
- Compare individual heuristics through ablation testing to measure their contribution to performance.

---

Developed independently as a UCL Computer Science assignment project.
