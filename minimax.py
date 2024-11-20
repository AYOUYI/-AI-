import numpy as np
from board import Board

class GomokuAI:
    def __init__(self, max_depth=4):
        self.max_depth = max_depth
        self.best_move = None
        
        # 棋型分数
        self.pattern_scores = {
            'win5': 100000,    # 连五
            'alive4': 10000,   # 活四
            'rush4': 5000,     # 冲四
            'alive3': 1000,    # 活三
            'sleep3': 500,     # 眠三
            'alive2': 100,     # 活二
            'sleep2': 50,      # 眠二
            'alive1': 10,      # 活一
        }

    def get_move(self, board):
        """获取最佳移动"""
        valid_moves = self._get_valid_moves(board)
        if not valid_moves:
            return None
            
        # 第一步下中心点
        if len(valid_moves) == board.size * board.size:
            center = board.size // 2
            return (center, center)
            
        # 检查必胜着法
        for move in valid_moves:
            if self._is_winning_move(board, move, board.current_player):
                return move
                
        # 检查必防着法
        for move in valid_moves:
            if self._is_winning_move(board, move, -board.current_player):
                return move
        
        alpha = float('-inf')
        beta = float('inf')
        best_score = float('-inf')
        best_move = None
        
        # 对每个可能的移动进行评估
        for move in valid_moves:
            new_board = board.copy()
            new_board.make_move(move)
            score = self._minimax(new_board, self.max_depth-1, False, alpha, beta)
            
            if score > best_score:
                best_score = score
                best_move = move
            
            alpha = max(alpha, best_score)
            
        return best_move

    def _get_valid_moves(self, board):
        """获取所有有效的移动，按照距离已有棋子的远近排序"""
        if len(board.get_valid_moves()) == board.size * board.size:
            center = board.size // 2
            return [(center, center)]
            
        moves = []
        for i in range(board.size):
            for j in range(board.size):
                if board.board[i][j] == 0 and self._has_neighbor(board, i, j):
                    score = self._evaluate_move(board, (i, j))
                    moves.append((score, (i, j)))
        
        # 按评分降序排序，只返回前15个最佳移动
        moves.sort(reverse=True)
        return [move for _, move in moves[:15]]

    def _has_neighbor(self, board, i, j):
        """检查位置(i,j)周围是否有棋子"""
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di == 0 and dj == 0:
                    continue
                ni, nj = i + di, j + dj
                if 0 <= ni < board.size and 0 <= nj < board.size:
                    if board.board[ni][nj] != 0:
                        return True
        return False

    def _minimax(self, board, depth, is_maximizing, alpha, beta):
        """极大极小搜索算法"""
        if depth == 0 or board.is_game_over():
            return self._evaluate_board(board)
        
        valid_moves = self._get_valid_moves(board)
        
        if is_maximizing:
            max_eval = float('-inf')
            for move in valid_moves:
                new_board = board.copy()
                new_board.make_move(move)
                eval = self._minimax(new_board, depth-1, False, alpha, beta)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in valid_moves:
                new_board = board.copy()
                new_board.make_move(move)
                eval = self._minimax(new_board, depth-1, True, alpha, beta)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def _is_winning_move(self, board, move, player):
        """检查是否是必胜着法"""
        test_board = board.copy()
        test_board.board[move[0]][move[1]] = player
        
        directions = [(1,0), (0,1), (1,1), (1,-1)]
        for di, dj in directions:
            count = 1
            # 正向检查
            ni, nj = move[0] + di, move[1] + dj
            while 0 <= ni < board.size and 0 <= nj < board.size and test_board.board[ni][nj] == player:
                count += 1
                ni += di
                nj += dj
            
            # 反向检查
            ni, nj = move[0] - di, move[1] - dj
            while 0 <= ni < board.size and 0 <= nj < board.size and test_board.board[ni][nj] == player:
                count += 1
                ni -= di
                nj -= dj
            
            if count >= 5:
                return True
        return False

    def _evaluate_board(self, board):
        """评估整个棋盘状态"""
        score = 0
        player = board.current_player
        opponent = -player
        
        # 评估所有方向
        directions = [(1,0), (0,1), (1,1), (1,-1)]
        for i in range(board.size):
            for j in range(board.size):
                if board.board[i][j] != 0:
                    for di, dj in directions:
                        # 评估当前玩家的棋型
                        if board.board[i][j] == player:
                            pattern = self._get_pattern(board, i, j, di, dj, player)
                            score += self._get_pattern_score(pattern)
                        # 评估对手的棋型
                        else:
                            pattern = self._get_pattern(board, i, j, di, dj, opponent)
                            score -= self._get_pattern_score(pattern) * 1.1  # 略微提高防守权重
        
        return score

    def _evaluate_move(self, board, move):
        """评估某个位置的价值"""
        score = 0
        i, j = move
        player = board.current_player
        opponent = -player
        
        # 模拟落子
        test_board = board.copy()
        test_board.board[i][j] = player
        
        # 评估进攻价值
        attack_score = self._evaluate_direction_all(test_board, i, j, player)
        score += attack_score
        
        # 评估防守价值
        test_board.board[i][j] = opponent
        defense_score = self._evaluate_direction_all(test_board, i, j, opponent)
        score += defense_score * 1.1  # 略微提高防守权重
        
        # 考虑位置的中心性
        center = board.size // 2
        distance_to_center = abs(i - center) + abs(j - center)
        score -= distance_to_center * 10
        
        return score

    def _evaluate_direction_all(self, board, i, j, player):
        """评估某个位置所有方向的价值"""
        score = 0
        directions = [(1,0), (0,1), (1,1), (1,-1)]
        
        for di, dj in directions:
            pattern = self._get_pattern(board, i, j, di, dj, player)
            score += self._get_pattern_score(pattern)
        
        return score

    def _get_pattern(self, board, i, j, di, dj, player):
        """获取某个方向的棋型"""
        consecutive = 1
        space_before = 0
        space_after = 0
        blocked = 0
        
        # 向前检查
        ni, nj = i - di, j - dj
        while 0 <= ni < board.size and 0 <= nj < board.size:
            if board.board[ni][nj] == 0:
                space_before += 1
                if space_before >= 2:
                    break
            elif board.board[ni][nj] == player:
                if space_before == 0:
                    consecutive += 1
                else:
                    break
            else:
                blocked += 1
                break
            ni -= di
            nj -= dj
        
        # 向后检查
        ni, nj = i + di, j + dj
        while 0 <= ni < board.size and 0 <= nj < board.size:
            if board.board[ni][nj] == 0:
                space_after += 1
                if space_after >= 2:
                    break
            elif board.board[ni][nj] == player:
                if space_after == 0:
                    consecutive += 1
                else:
                    break
            else:
                blocked += 1
                break
            ni += di
            nj += dj
        
        return (consecutive, blocked, space_before + space_after)

    def _get_pattern_score(self, pattern):
        """根据棋型返回分数"""
        consecutive, blocked, space = pattern
        
        if consecutive >= 5:
            return self.pattern_scores['win5']
        
        if consecutive == 4:
            if blocked == 0:
                return self.pattern_scores['alive4']
            elif blocked == 1:
                return self.pattern_scores['rush4']
        
        if consecutive == 3:
            if blocked == 0:
                return self.pattern_scores['alive3']
            elif blocked == 1:
                return self.pattern_scores['sleep3']
        
        if consecutive == 2:
            if blocked == 0:
                return self.pattern_scores['alive2']
            elif blocked == 1:
                return self.pattern_scores['sleep2']
        
        if consecutive == 1:
            if blocked == 0:
                return self.pattern_scores['alive1']
        
        return 0
