import numpy as np
import random
import numba
import time
from typing import List, Tuple, Optional  # 添加这个导入

COLOR_BLACK = -1
COLOR_WHITE = 1
COLOR_NONE = 0
C_X_POINTS = [(0, 1), (1, 0), (1, 1), (0, 6), (1, 6), (1, 7),
              (6, 0), (6, 1), (7, 1), (6, 6), (6, 7), (7, 6)]


# ===== 原有的AI类 =====
class AI(object):
    def __init__(self, chessboard_size=8, color=COLOR_NONE, time_out=5.0):
        self.chessboard_size = chessboard_size
        self.color = color
        self.time_out = time_out
        self.candidate_list = []

        # 17个遗传算法参数 + 2个搜索参数
        # 位置权重参数 v[0]-v[9]
        self.weight_vector = [10.49359640524536, 6.074361821653552, 23.23132876440326, 20.868211117335303, 9.069621066840796, 44.692108180301766, 29.28046185627584, 15.448222357571511, -31.312624292985586, 25.819962143728134]
        # 稳定子权重
        self.stability_weight = 112.40179879351612
        # 行动力权重(前中期各2个)
        self.mobility_weight = (20.89397854731418, 32.46275224220238, 30.92215133159721, 48.41880892378325)
        # 前沿子权重(前中期各1个)
        self.frontier_weight = (35.84674738800028, 25.62800134444401)
        # 搜索参数 (UTILITY_THRESHOLD, MAX_DEPTH)
        self.search_params = (15, 6)

        # 棋盘权重矩阵:
        # [v[9], v[8], v[6], v[3], v[3], v[6], v[8], v[9]]
        # [v[8], v[7], v[5], v[2], v[2], v[5], v[7], v[8]]
        # [v[6], v[5], v[4], v[1], v[1], v[4], v[5], v[6]]
        # [v[3], v[2], v[1], v[0], v[0], v[1], v[2], v[3]]
        # [v[3], v[2], v[1], v[0], v[0], v[1], v[2], v[3]]
        # [v[6], v[5], v[4], v[1], v[1], v[4], v[5], v[6]]
        # [v[8], v[7], v[5], v[2], v[2], v[5], v[7], v[8]]
        # [v[9], v[8], v[6], v[3], v[3], v[6], v[8], v[9]]
        self.chessboard_weight = np.array([
            [25.81996214372813, -31.31262429298559, 29.28046185627584, 20.86821111733530, 20.86821111733530, 29.28046185627584, -31.31262429298559, 25.81996214372813],
            [-31.31262429298559, 15.44822235757151, 44.69210818030177, 23.23132876440326, 23.23132876440326, 44.69210818030177, 15.44822235757151, -31.31262429298559],
            [29.28046185627584, 44.69210818030177, 9.06962106684080, 6.07436182165355, 6.07436182165355, 9.06962106684080, 44.69210818030177, 29.28046185627584],
            [20.86821111733530, 23.23132876440326, 6.07436182165355, 10.49359640524536, 10.49359640524536, 6.07436182165355, 23.23132876440326, 20.86821111733530],
            [20.86821111733530, 23.23132876440326, 6.07436182165355, 10.49359640524536, 10.49359640524536, 6.07436182165355, 23.23132876440326, 20.86821111733530],
            [29.28046185627584, 44.69210818030177, 9.06962106684080, 6.07436182165355, 6.07436182165355, 9.06962106684080, 44.69210818030177, 29.28046185627584],
            [-31.31262429298559, 15.44822235757151, 44.69210818030177, 23.23132876440326, 23.23132876440326, 44.69210818030177, 15.44822235757151, -31.31262429298559],
            [25.81996214372813, -31.31262429298559, 29.28046185627584, 20.86821111733530, 20.86821111733530, 29.28046185627584, -31.31262429298559, 25.81996214372813]
        ])
        self.directions = ((1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1))
        self.corners = [(0, 0), (0, 7), (7, 0), (7, 7)]  # 角落位置

        self.INF = 1e+8
        self.WIN_GAME = 1e+5
        self.chessboard = None

    def set_params(self, params: dict):
        """从外部设置AI参数"""
        if 'weight_vector' in params:
            self.weight_vector = params['weight_vector']
            self.chessboard_weight = assign_weight_array(self.weight_vector, self.chessboard_size)
        if 'stability_weight' in params:
            self.stability_weight = params['stability_weight']
        if 'mobility_weight' in params:
            self.mobility_weight = params['mobility_weight']
        if 'frontier_weight' in params:
            self.frontier_weight = params['frontier_weight']
        if 'search_params' in params:
            self.search_params = params['search_params']

    def to_list(self):
        """将参数转化为列表，用于遗传算法"""
        return (list(self.weight_vector) +
                [self.stability_weight] +
                list(self.mobility_weight) +
                list(self.frontier_weight) +
                list(self.search_params))

    def from_list(self, arg_list):
        """从列表加载参数"""
        self.weight_vector = arg_list[:10]
        self.stability_weight = arg_list[10]
        self.mobility_weight = (arg_list[11], arg_list[12], arg_list[13], arg_list[14])
        self.frontier_weight = (arg_list[15], arg_list[16])
        self.search_params = (int(arg_list[17]), int(arg_list[18]))

        self.chessboard_weight = assign_weight_array(self.weight_vector, self.chessboard_size)

    def get_move(self, board: np.ndarray, player: int = None) -> Tuple[Optional[tuple], List[tuple]]:
        """获取AI的移动决策"""
        if player is not None:
            self.color = player

        self.chessboard = np.array(board, dtype=int)
        self.candidate_list = []
        self.go(self.chessboard)

        if len(self.candidate_list) > 0:
            best_move = self.candidate_list[-1] if len(self.candidate_list) > 1 else None
            return best_move, self.candidate_list
        return None, []

    def go(self, chessboard):
        """主要决策函数 - 强制避免角落"""
        self.candidate_list.clear()
        self.chessboard = chessboard

        # 时间管理
        start_time = time.time()
        deadline = start_time + min(max(self.time_out - 0.05, 0.5), 4.5)

        # 获取所有合法移动
        all_possible_actions = generate_actions_filter(chessboard, self.color)

        # 首先排除角落移动（除非没有其他选择）
        non_corner_actions = [action for action in all_possible_actions if action not in self.corners]

        if non_corner_actions:
            # 有非角落移动可用，优先使用这些
            possible_actions = non_corner_actions
            forced_corner = False
        else:
            # 只有角落移动可用，被迫使用
            possible_actions = all_possible_actions
            forced_corner = True

        # 必须返回所有合法移动（包括角落）
        for action in all_possible_actions:
            self.candidate_list.append(tuple(action))

        if not all_possible_actions:
            return []

        # 迭代深化搜索
        UTILITY_THRESHOLD, MAX_DEPTH = self.search_params
        blank_points = np.sum(chessboard == COLOR_NONE)

        best_move = possible_actions[0]

        if blank_points <= UTILITY_THRESHOLD:
            # 终局完全搜索
            best_move = self.terminal_search(possible_actions, blank_points)
        else:
            # 迭代深化搜索
            best_move = self.iterative_deepening_search(possible_actions, MAX_DEPTH, deadline)

        # 最终决策：如果最佳移动是角落且不是被迫的，重新选择
        final_move = best_move
        if best_move in self.corners and not forced_corner:
            # 在非角落移动中选择次佳的
            if len(possible_actions) > 1:
                # 重新评估，排除角落
                non_corner_values = []
                for action in possible_actions:
                    if action not in self.corners:
                        update_array = update_chessboard(self.chessboard, action, self.color)
                        value = self._eval()
                        revert_chessboard(self.chessboard, action, self.color, update_array)
                        non_corner_values.append((value, action))

                if non_corner_values:
                    non_corner_values.sort(reverse=True)
                    final_move = non_corner_values[0][1]

        self.candidate_list.append(tuple(final_move))
        return self.candidate_list

    def iterative_deepening_search(self, possible_actions, max_depth, deadline):
        """迭代深化搜索"""
        best_move = possible_actions[0]
        best_value = -self.INF

        # 移动排序：角落优先（但会在后续避免）
        sorted_actions = self._sort_moves(possible_actions)

        try:
            for depth in range(2, max_depth + 1):
                if time.time() > deadline:
                    break

                current_best_move = None
                current_best_value = -self.INF
                alpha = -self.INF

                for action in sorted_actions:
                    if time.time() > deadline:
                        break

                    # 使用可逆操作
                    update_array = update_chessboard(self.chessboard, action, self.color)
                    value = self._min_value(-self.color, depth - 1, alpha, self.INF, deadline)
                    revert_chessboard(self.chessboard, action, self.color, update_array)

                    if value is None:  # 超时，使用之前的最佳值
                        continue

                    if value > current_best_value:
                        current_best_value = value
                        current_best_move = action

                    alpha = max(alpha, current_best_value)

                # 只有当这一层有有效结果时才更新最佳移动
                if current_best_move is not None:
                    best_move = current_best_move
                    best_value = current_best_value

        except Exception:
            pass

        return best_move

    def terminal_search(self, possible_actions, blank_points):
        """终局完全搜索 - 使用简化评估"""
        best_move = possible_actions[0]
        best_value = -self.INF

        for action in possible_actions:
            update_array = update_chessboard(self.chessboard, action, self.color)
            value = self._min_value_terminal(-self.color, blank_points - 1)
            revert_chessboard(self.chessboard, action, self.color, update_array)

            if value > best_value:
                best_value = value
                best_move = action

        return best_move

    def _max_value(self, player, depth, alpha, beta, deadline):
        """Max节点搜索 - 优化移动生成"""
        if time.time() > deadline:
            return None

        if depth == 0:
            return self._eval()

        # 直接使用优化函数生成合法移动
        possible_actions = generate_actions_filter(self.chessboard, player)

        if not possible_actions:
            # 如果没有合法移动，检查游戏是否结束
            if not generate_actions_filter(self.chessboard, -player):
                return self._eval_terminal()  # 游戏结束
            return self._min_value(-player, depth, alpha, beta, deadline)  # 对手继续

        value = -self.INF

        # 在搜索中也避免角落
        non_corner_actions = [action for action in possible_actions if action not in self.corners]
        actions_to_search = non_corner_actions if non_corner_actions else possible_actions

        # 移动排序
        sorted_actions = self._sort_moves(actions_to_search)

        for action in sorted_actions:
            if time.time() > deadline:
                return None

            update_array = update_chessboard(self.chessboard, action, player)
            child_value = self._min_value(-player, depth - 1, alpha, beta, deadline)
            revert_chessboard(self.chessboard, action, player, update_array)

            if child_value is None:
                continue  # 超时，继续下一个移动而不是直接返回

            value = max(value, child_value)
            alpha = max(alpha, value)
            if alpha >= beta:
                break

        return value if value != -self.INF else None

    def _min_value(self, player, depth, alpha, beta, deadline):
        """Min节点搜索 - 优化移动生成"""
        if time.time() > deadline:
            return None

        if depth == 0:
            return self._eval()

        # 直接使用优化函数生成合法移动
        possible_actions = generate_actions_filter(self.chessboard, player)

        if not possible_actions:
            # 如果没有合法移动，检查游戏是否结束
            if not generate_actions_filter(self.chessboard, -player):
                return self._eval_terminal()  # 游戏结束
            return self._max_value(-player, depth, alpha, beta, deadline)  # 对手继续

        value = self.INF

        # 在搜索中也避免角落
        non_corner_actions = [action for action in possible_actions if action not in self.corners]
        actions_to_search = non_corner_actions if non_corner_actions else possible_actions

        # 移动排序
        sorted_actions = self._sort_moves(actions_to_search)

        for action in sorted_actions:
            if time.time() > deadline:
                return None

            update_array = update_chessboard(self.chessboard, action, player)
            child_value = self._max_value(-player, depth - 1, alpha, beta, deadline)
            revert_chessboard(self.chessboard, action, player, update_array)

            if child_value is None:
                continue  # 超时，继续下一个移动

            value = min(value, child_value)
            beta = min(beta, value)
            if alpha >= beta:
                break

        return value if value != self.INF else None

    def _min_value_terminal(self, player, remaining_depth):
        """终局搜索的Min节点 """
        if remaining_depth == 0:
            return self._eval_terminal()

        value = self.INF
        has_valid_move = False

        possible_actions = generate_actions_filter(self.chessboard, player)

        if not possible_actions:
            if not generate_actions_filter(self.chessboard, -player):
                return self._eval_terminal()
            return self._max_value_terminal(-player, remaining_depth)

        for action in possible_actions:
            has_valid_move = True
            update_array = update_chessboard(self.chessboard, action, player)
            child_value = self._max_value_terminal(-player, remaining_depth - 1)
            revert_chessboard(self.chessboard, action, player, update_array)
            value = min(value, child_value)

        return value

    def _max_value_terminal(self, player, remaining_depth):
        """终局搜索的Max节点 """
        if remaining_depth == 0:
            return self._eval_terminal()

        value = -self.INF
        has_valid_move = False

        possible_actions = generate_actions_filter(self.chessboard, player)

        if not possible_actions:
            if not generate_actions_filter(self.chessboard, -player):
                return self._eval_terminal()
            return self._min_value_terminal(-player, remaining_depth)

        for action in possible_actions:
            has_valid_move = True
            update_array = update_chessboard(self.chessboard, action, player)
            child_value = self._min_value_terminal(-player, remaining_depth - 1)
            revert_chessboard(self.chessboard, action, player, update_array)
            value = max(value, child_value)

        return value

    def _sort_moves(self, moves):
        """快速移动排序"""

        def priority(move):
            r, c = move
            score = -self.chessboard_weight[r, c] * 10  # 基础权重

            # 角落惩罚
            if move in self.corners:
                score -= 10000
            # C_X位置奖励
            elif move in C_X_POINTS:
                score += 3000
            elif r == 0 or r == 7 or c == 0 or c == 7:
                if move not in [(0, 1), (1, 0), (0, 6), (1, 7), (6, 0), (7, 1), (6, 7), (7, 6)]:
                    score -= 1000
            return score

        return sorted(moves, key=priority, reverse=True)

    def _eval(self):
        """正常局面评估函数，使用17个参数"""
        return evaluate_chessboard(
            chessboard=self.chessboard,
            color=self.color,
            stability_weight=self.stability_weight,
            mobility_weight=self.mobility_weight,
            frontier_weight=self.frontier_weight,
            chessboard_weight=self.chessboard_weight
        )

    def _eval_terminal(self):
        return evaluate_chessboard(
            chessboard=self.chessboard,
            color=self.color,
            stability_weight=self.stability_weight,
            mobility_weight=self.mobility_weight,
            frontier_weight=self.frontier_weight,
            chessboard_weight=self.chessboard_weight
        )


# ===== 你原有的numba函数 =====
@numba.njit(cache=True)
def find_boundaries(chessboard: np.ndarray):
    chessboard_size = chessboard.shape[0]
    max_index = chessboard_size - 1

    black_boundaries = np.zeros((chessboard_size, chessboard_size), dtype=np.intc)
    white_boundaries = np.zeros((chessboard_size, chessboard_size), dtype=np.intc)

    for x, y in ((0, 0), (0, 1), (1, 0), (1, 1)):
        i_depth, j_depth = chessboard_size, chessboard_size
        capturing_player = chessboard[x * max_index, y * max_index]
        if capturing_player == COLOR_NONE:
            continue

        for i in range(0, chessboard_size, 1):
            for j in range(0, j_depth, 1):
                point = max_index - i if x else i, max_index - j if y else j
                if chessboard[point] == capturing_player:
                    if capturing_player == COLOR_BLACK:
                        black_boundaries[point] = 1
                    else:
                        white_boundaries[point] = 1
                else:
                    j_depth = j - 1
                    break
            if j_depth < 0:
                break

        for j in range(0, chessboard_size, 1):
            for i in range(0, i_depth, 1):
                point = max_index - i if x else i, max_index - j if y else j
                if chessboard[point] == capturing_player:
                    if capturing_player == COLOR_BLACK:
                        black_boundaries[point] = 1
                    else:
                        white_boundaries[point] = 1
                else:
                    i_depth = i - 1
                    break
            if i_depth < 0:
                break

    return np.sum(black_boundaries), np.sum(white_boundaries)


@numba.njit(cache=True)
def generate_actions_filter(chessboard: np.ndarray, player: int):
    blank_index = np.where(chessboard == COLOR_NONE)
    blank_positions = zip(blank_index[0], blank_index[1])
    legal_moves = []
    for position in blank_positions:
        if is_legal_position(chessboard, position, player):
            legal_moves.append(position)
    return legal_moves


@numba.njit(cache=True)
def is_legal_position(chessboard: np.ndarray, position: tuple, player: int):
    chessboard_size = chessboard.shape[0]
    for direction in ((1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1)):
        iter_x = position[0] + direction[0]
        iter_y = position[1] + direction[1]
        if not (0 <= iter_x < chessboard_size and 0 <= iter_y < chessboard_size):
            continue
        while chessboard[iter_x, iter_y] == -player:
            iter_x += direction[0]
            iter_y += direction[1]
            if not (0 <= iter_x < chessboard_size and 0 <= iter_y < chessboard_size):
                break
            if chessboard[iter_x, iter_y] == player:
                return True
    return False


def assign_weight_array(v, csize):
    assert csize == 8
    weight_matrix = np.array([
        [v[9], v[8], v[6], v[3], v[3], v[6], v[8], v[9]],
        [v[8], v[7], v[5], v[2], v[2], v[5], v[7], v[8]],
        [v[6], v[5], v[4], v[1], v[1], v[4], v[5], v[6]],
        [v[3], v[2], v[1], v[0], v[0], v[1], v[2], v[3]],
        [v[3], v[2], v[1], v[0], v[0], v[1], v[2], v[3]],
        [v[6], v[5], v[4], v[1], v[1], v[4], v[5], v[6]],
        [v[8], v[7], v[5], v[2], v[2], v[5], v[7], v[8]],
        [v[9], v[8], v[6], v[3], v[3], v[6], v[8], v[9]]
    ])
    return weight_matrix


@numba.njit(cache=True)
def find_sentinels(chessboard: np.ndarray):
    max_index = chessboard.shape[0] - 1
    blanks_indexes = np.where(chessboard == COLOR_NONE)
    sentinel_map = np.zeros_like(chessboard)
    for dx, dy in ((1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1)):
        for point in zip(blanks_indexes[0] + dx, blanks_indexes[1] + dy):
            if 0 <= point[0] <= max_index and 0 <= point[1] <= max_index:
                sentinel_map[point] = 1
    black_sentinels = (chessboard == COLOR_BLACK) & sentinel_map
    white_sentinels = (chessboard == COLOR_WHITE) & sentinel_map
    return np.sum(black_sentinels), np.sum(white_sentinels)


def revert_chessboard(chessboard, position, player, update_array):
    chessboard[position] = COLOR_NONE
    for point in update_array:
        chessboard[point[0], point[1]] = -player


def update_chessboard(chessboard, position, player):
    update_list = get_update_list(chessboard, position, player)
    chessboard[position] = player
    for point in update_list:
        chessboard[point] = player
    return np.array(update_list, dtype=int)


@numba.njit(cache=True)
def get_update_list(chessboard, position, player):
    update_list = []
    chessboard_size = np.shape(chessboard)[0]
    for direction in ((1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1)):
        iter_x = position[0] + direction[0]
        iter_y = position[1] + direction[1]
        direction_indexes_list = [(iter_x, iter_y)]
        if not (0 <= iter_x < chessboard_size and 0 <= iter_y < chessboard_size):
            continue
        while chessboard[iter_x, iter_y] == -player:
            iter_x += direction[0]
            iter_y += direction[1]
            if not (0 <= iter_x < chessboard_size and 0 <= iter_y < chessboard_size):
                break
            if chessboard[iter_x, iter_y] == player:
                [update_list.append(x) for x in direction_indexes_list]
                break
            direction_indexes_list.append((iter_x, iter_y))
    return update_list


@numba.njit(cache=True)
def evaluate_chessboard(chessboard, color, stability_weight, mobility_weight, frontier_weight, chessboard_weight):
    step = np.sum(chessboard != COLOR_NONE) - 4
    my_actions = generate_actions_filter(chessboard, color)
    opponent_actions = generate_actions_filter(chessboard, -color)

    # 游戏结束判断
    if (not my_actions) and (not opponent_actions):
        advantage = np.sum(chessboard) * (-color)
        return 1e+5 if advantage > 0 else -1e+5 if advantage < 0 else 5e+4

    # 稳定子计算
    if color == COLOR_BLACK:
        my_boundary, opponent_boundary = find_boundaries(chessboard)
        my_sentinels, opponent_sentinels = find_sentinels(chessboard)
    else:
        opponent_boundary, my_boundary = find_boundaries(chessboard)
        opponent_sentinels, my_sentinels = find_sentinels(chessboard)

    # 正值对当前玩家有利
    stability_score = stability_weight * (opponent_boundary - my_boundary)

    # 分阶段权重
    if step < 30:
        mobility_score = len(my_actions) * mobility_weight[0] - len(opponent_actions) * mobility_weight[1]
        frontier_score = frontier_weight[0] * (opponent_sentinels - my_sentinels)
    else:
        mobility_score = len(my_actions) * mobility_weight[2] - len(opponent_actions) * mobility_weight[3]
        frontier_score = frontier_weight[1] * (opponent_sentinels - my_sentinels)

    positional_score = np.sum(np.multiply(chessboard, chessboard_weight)) * (-color)

    return positional_score + stability_score + mobility_score + frontier_score


# ===== AI服务封装 =====
class AIService:
    def __init__(self):
        self.ai_instances = {}

    def create_ai(self, ai_id: str, params: dict = None) -> AI:
        """创建新的AI实例"""
        # 明确传入棋盘大小、颜色、超时时间
        ai = AI(chessboard_size=8, color=COLOR_NONE, time_out=5.0)
        if params:
            ai.set_params(params)
        self.ai_instances[ai_id] = ai
        return ai

    def get_move(self, ai_id: str, board: List[List[int]], player: int) -> Tuple[Optional[tuple], List[tuple]]:
        if ai_id not in self.ai_instances:
            self.create_ai(ai_id)
        return self.ai_instances[ai_id].get_move(np.array(board), player)


# 全局AI服务实例
ai_service = AIService()