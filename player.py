from board import Direction, Rotation, Action
from random import Random
import time


class Player:
    def choose_action(self, board):
        raise NotImplementedError


class KhairulAI(Player):
    def __init__(self):
       
        self.weights = {
            "aggregate_height": -0.5,
            "complete_lines": 0.7,
            "holes": -1.0,
            "bumpiness": -0.35,
            "well_depth": 0.8,
            "tetris_bonus": 5.0
        }

    #  Feature calculations 
    def get_column_heights(self, board):
        heights = [0]*10
        for x in range(10):
            for y in range(24):
                if (x, y) in board.cells:
                    heights[x] = 24 - y
                    break
        return heights

    def get_aggregate_height(self, board):
        return sum(self.get_column_heights(board))

    def get_complete_lines(self, board):
        lines = 0
        for y in range(24):
            if all((x, y) in board.cells for x in range(10)):
                lines += 1
        return lines

    def get_holes(self, board):
        holes = 0
        heights = self.get_column_heights(board)
        for x in range(10):
            top = 24 - heights[x]
            for y in range(top, 24):
                if (x, y) not in board.cells:
                    holes += 1
        return holes

    def get_bumpiness(self, board):
        heights = self.get_column_heights(board)
        return sum(abs(heights[i]-heights[i+1]) for i in range(9))

    def get_rightmost_well(self, board):
        right_col = [((9, y) in board.cells) for y in range(24)]
        well_depth = 0
        block_seen = False
        hole_below_block = False

        for y in reversed(range(24)):
            if right_col[y]:
                block_seen = True
            elif not block_seen:
                well_depth += 1
            elif block_seen:
                hole_below_block = True

        return well_depth, not hole_below_block

    def get_board_height(self, board):
        return max(self.get_column_heights(board))

    def get_hole_distribution(self, board):
        holes_in_well = 0
        holes_elsewhere = 0
        heights = self.get_column_heights(board)
        for x in range(10):
            top = 24 - heights[x]
            for y in range(top, 24):
                if (x, y) not in board.cells:
                    if x == 9:
                        holes_in_well += 1
                    else:
                        holes_elsewhere += 1
        return holes_in_well, holes_elsewhere
    
    def get_well_flatness(self, board):
        heights = self.get_column_heights(board)
        platform_heights = heights[:9] 
        if not platform_heights:
            return 0
        avg_height = sum(platform_heights) / len(platform_heights)
        variance = sum((h - avg_height) ** 2 for h in platform_heights) / len(platform_heights)
        return variance

    #  Scoring function 
    def evaluate_board(self, board):
        agg_height = self.get_aggregate_height(board)
        lines = self.get_complete_lines(board)
        holes = self.get_holes(board)
        bumpiness = self.get_bumpiness(board)
        well_depth, is_clean = self.get_rightmost_well(board)
        board_height = self.get_board_height(board)
        holes_in_well, holes_elsewhere = self.get_hole_distribution(board)
        well_flatness = self.get_well_flatness(board)

        if board_height > 18:
            w_height = -10.0   
            w_lines = 5000.0   
            w_holes = -1.0     
            w_bump = -5.0      
            w_well = 0.0
            tetris_bonus = 10000.0 

        elif board_height > 14 and board_height <= 18:
            w_height = -3.0
            w_lines = 500.0   
            w_holes = -2.0
            w_bump = -2.0      
            w_well = 1.0
            tetris_bonus = 2000.0

        else:
            w_height = -0.51
            w_lines = 0.76
            w_holes = -3.5
            w_bump = -0.5      
            w_well = 5.0
            tetris_bonus = self.weights["tetris_bonus"]

        score = (
            w_height * agg_height
            + w_lines * lines
            + w_holes * holes
            + w_bump * bumpiness
        )

        if is_clean and well_depth > 0:
            score += w_well * well_depth
            if well_depth >= 10:
                score += 50
            if well_depth >= 12:
                score += 100

        score -= 4.0 * holes_elsewhere
        score -= 0.5 * holes_in_well

        score -= 0.5 * well_flatness  
        
        heights = self.get_column_heights(board)
        for i in range(9):  
            if heights[i] > 15:
                score -= 50.0 * (heights[i] - 15)  



        if lines == 4:
            score += tetris_bonus + 9000000
            if well_depth >= 8:
                score += 300

        ready_for_tetris = sum(1 for y in range(24) if sum(1 for x in range(9) if (x, y) in board.cells) == 9)
        if ready_for_tetris >= 3 and is_clean:
            score += 2 * ready_for_tetris

        if holes_elsewhere == 0 and bumpiness < 8:
            score += 20.0

        if lines > 0 and holes_elsewhere > 0:
            score += 1.5 * lines

        if lines == 4 and board_height < 12:
            score += tetris_bonus

        return score

    def simulate_piece(self, sandbox, target_rot, target_col):
        moves = []
        landed = False

        for _ in range(target_rot):
            if not landed:
                landed = sandbox.rotate(Rotation.Anticlockwise)
                moves.append(Rotation.Anticlockwise)

        while not landed and sandbox.falling.left > target_col:
            landed = sandbox.move(Direction.Left)
            moves.append(Direction.Left)
        while not landed and sandbox.falling.left < target_col:
            landed = sandbox.move(Direction.Right)
            moves.append(Direction.Right)

        if not landed:
            sandbox.move(Direction.Drop)
            moves.append(Direction.Drop)

        return moves

    def choose_action(self, board):
        best_score = float("-inf")
        best_moves = []

        if board.falling is None:
            return []


        initial_holes = self.get_holes(board)
        
        next_piece = board.next  

        board_height = self.get_board_height(board)


        emergency_mode = board_height >= 18
        panic_mode = board_height >= 20

        for rot1 in range(4):
            for col1 in range(10):
                sandbox1 = board.clone()
                moves1 = self.simulate_piece(sandbox1, rot1, col1)

                new_holes = self.get_holes(sandbox1)
                if new_holes > initial_holes:
                    continue

                score1 = self.evaluate_board(sandbox1)

                lines_cleared = self.get_complete_lines(sandbox1)
                if lines_cleared == 4:
                    if score1 > best_score:
                        best_score = score1
                        best_moves = moves1
                    continue  

                if next_piece:
                    best_score2 = float("-inf")
                    for rot2 in range(4):
                        for col2 in range(10):
                            sandbox2 = sandbox1.clone()
                            sandbox2.falling = next_piece.clone()
                            self.simulate_piece(sandbox2, rot2, col2)
                            score2 = self.evaluate_board(sandbox2)
                            if score2 > best_score2:
                                best_score2 = score2
                    score1 = best_score2

                if score1 > best_score:
                    best_score = score1
                    best_moves = moves1

        if best_moves == []:
            return [Action.Discard]

        return best_moves

SelectedPlayer = KhairulAI
