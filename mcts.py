import math
import random
import numpy as np
from board import Board

class Node:
    def __init__(self, board, parent=None, move=None):
        self.board = board
        self.parent = parent
        self.move = move
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untried_moves = self._get_sorted_moves(board)

    def _get_sorted_moves(self, board):
        """获取排序后的移动列表，优先考虑关键位置"""
        valid_moves = board.get_valid_moves()
        if not valid_moves:
            return []
        
        # 如果是第一步，返回中心位置
        if len(valid_moves) == board.size * board.size:
            center = board.size // 2
            return [(center, center)]
        
        # 检查必胜/必防位置
        critical_moves = []
        high_priority_moves = []
        normal_moves = []
        
        for move in valid_moves:
            # 检查是否能赢
            if self._is_winning_move(board, move, board.current_player):
                return [move]  # 立即返回必胜着法
            
            # 检查是否需要防守
            if self._is_winning_move(board, move, -board.current_player):
                critical_moves.append(move)
                continue
            
            # 评估移动的价值
            score = self._evaluate_move(board, move)
            if score >= 5000:  # 高优先级移动（形成活三或以上）
                high_priority_moves.append((score, move))
            else:
                normal_moves.append((score, move))
        
        # 按优先级返回移动
        if critical_moves:
            return critical_moves
        
        # 对其他移动按分数排序
        high_priority_moves.sort(reverse=True)
        normal_moves.sort(reverse=True)
        
        # 组合移动列表，限制总数为10个
        sorted_moves = [move for _, move in high_priority_moves]
        sorted_moves.extend([move for _, move in normal_moves])
        return sorted_moves[:10]

    def _is_winning_move(self, board, move, player):
        """检查是否是必胜着法"""
        test_board = board.copy()
        test_board.board[move[0]][move[1]] = player
        
        # 检查四个方向
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

    def _evaluate_move(self, board, move):
        """评估移动的价值"""
        i, j = move
        score = 0
        player = board.current_player
        opponent = -player
        
        # 在移动位置模拟落子
        test_board = board.copy()
        test_board.board[i][j] = player
        
        # 评估四个方向
        directions = [(1,0), (0,1), (1,1), (1,-1)]
        for di, dj in directions:
            # 评估进攻
            attack_score = self._evaluate_line(test_board, i, j, di, dj, player)
            score += attack_score
            
            # 评估防守
            defense_score = self._evaluate_line(board, i, j, di, dj, opponent)
            score += defense_score * 1.1  # 略微提高防守权重
        
        # 考虑位置的中心性
        center = board.size // 2
        distance_to_center = abs(i - center) + abs(j - center)
        score -= distance_to_center * 10
        
        # 考虑与最近棋子的距离
        min_distance = self._get_min_distance_to_pieces(board, move)
        if min_distance > 2:  # 如果离最近的棋子太远，大幅降低分数
            score *= 0.1
        
        return score

    def _evaluate_line(self, board, i, j, di, dj, player):
        """评估某个方向的棋型"""
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
        
        # 评分规则
        if consecutive >= 5:
            return 100000  # 连五
        elif consecutive == 4:
            if blocked == 0:
                return 50000  # 活四
            elif blocked == 1:
                return 10000  # 冲四
        elif consecutive == 3:
            if blocked == 0:
                return 8000  # 活三
            elif blocked == 1:
                return 3000  # 眠三
        elif consecutive == 2:
            if blocked == 0:
                return 1000  # 活二
            elif blocked == 1:
                return 300  # 眠二
        
        return 100  # 基础分

    def _get_min_distance_to_pieces(self, board, move):
        """计算到最近棋子的距离"""
        min_distance = float('inf')
        i, j = move
        
        for x in range(max(0, i-2), min(board.size, i+3)):
            for y in range(max(0, j-2), min(board.size, j+3)):
                if board.board[x][y] != 0:
                    distance = abs(x-i) + abs(y-j)
                    min_distance = min(min_distance, distance)
        
        return min_distance

    def select_child(self):
        """使用UCB1公式选择最有希望的子节点"""
        c = 1.414  # UCB1探索参数
        s = sorted(self.children, key=lambda x: x.wins/x.visits + 
                  c * math.sqrt(2 * math.log(self.visits)/x.visits))
        return s[-1]

    def add_child(self, move):
        """添加子节点"""
        new_board = self.board.copy()
        new_board.make_move(move)
        child = Node(new_board, self, move)
        self.untried_moves.remove(move)
        self.children.append(child)
        return child

    def update(self, result):
        """更新节点的统计信息"""
        self.visits += 1
        self.wins += result

class MCTS:
    def __init__(self, time_limit=5.0, max_moves=1000):
        self.time_limit = time_limit
        self.max_moves = max_moves

    def get_move(self, board):
        """获取最佳移动"""
        import time
        root = Node(board)
        
        # 首先检查必胜/必防着法
        for move in root.untried_moves:
            # 检查必胜
            if root._is_winning_move(board, move, board.current_player):
                return move
            # 检查必防
            if root._is_winning_move(board, move, -board.current_player):
                return move
        
        end_time = time.time() + self.time_limit
        
        # 在时间限制内进行尽可能多的模拟
        while time.time() < end_time:
            node = root
            
            # Selection
            while node.untried_moves == [] and node.children != []:
                node = node.select_child()
            
            # Expansion
            if node.untried_moves != []:
                move = node.untried_moves[0]  # 选择最高分的移动
                node = node.add_child(move)
            
            # Simulation
            board_state = node.board.copy()
            current_player = board_state.current_player
            
            # 快速模拟
            while not board_state.is_game_over():
                moves = board_state.get_valid_moves()
                if not moves:
                    break
                
                # 检查必胜/必防移动
                winning_move = None
                blocking_move = None
                
                for move in moves[:min(6, len(moves))]:
                    # 检查是否能赢
                    if self._is_winning_move(board_state, move):
                        winning_move = move
                        break
                    # 检查是否需要防守
                    elif self._is_winning_move(board_state, move, check_opponent=True):
                        blocking_move = move
                
                if winning_move:
                    chosen_move = winning_move
                elif blocking_move:
                    chosen_move = blocking_move
                else:
                    # 使用启发式选择移动
                    move_scores = [(self._quick_evaluate_move(board_state, move), move) 
                                 for move in moves[:min(6, len(moves))]]
                    move_scores.sort(reverse=True)
                    chosen_move = move_scores[0][1]
                
                board_state.make_move(chosen_move)
            
            # Backpropagation
            result = board_state.check_win()
            while node is not None:
                if result == 0:
                    node.update(0.5)
                else:
                    node.update(1 if result == current_player else 0)
                node = node.parent
        
        # 选择访问次数最多的移动
        return sorted(root.children, key=lambda x: x.visits)[-1].move

    def _is_winning_move(self, board, move, check_opponent=False):
        """检查是否是必胜/必防移动"""
        player = -board.current_player if check_opponent else board.current_player
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

    def _quick_evaluate_move(self, board, move):
        """快速评估移动的价值（用于模拟阶段）"""
        i, j = move
        score = 0
        player = board.current_player
        
        # 检查四个方向
        directions = [(1,0), (0,1), (1,1), (1,-1)]
        for di, dj in directions:
            consecutive = 1
            blocked = 0
            space = 0
            
            # 向两个方向检查
            for direction in [1, -1]:
                ni, nj = i + direction * di, j + direction * dj
                while 0 <= ni < board.size and 0 <= nj < board.size:
                    if board.board[ni][nj] == player:
                        if space == 0:
                            consecutive += 1
                        else:
                            break
                    elif board.board[ni][nj] == 0:
                        space += 1
                        if space >= 2:
                            break
                    else:
                        blocked += 1
                        break
                    ni += direction * di
                    nj += direction * dj
            
            # 评分
            if consecutive >= 5:
                score += 100000
            elif consecutive == 4:
                if blocked == 0:
                    score += 50000
                elif blocked == 1:
                    score += 10000
            elif consecutive == 3:
                if blocked == 0:
                    score += 5000
                elif blocked == 1:
                    score += 1000
            elif consecutive == 2:
                if blocked == 0:
                    score += 500
                elif blocked == 1:
                    score += 100
        
        return score

    def get_best_move(self, board):
        """获取最佳移动并返回相关统计信息"""
        move = self.get_move(board)
        return move
