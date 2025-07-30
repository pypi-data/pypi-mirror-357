"""
计算加速度数据中的翻身次数
"""
import numpy as np


def count_turnover(acc, win=15, sf=50):
    """
    计算加速度数据中的翻身次数
    
    参数:
    acc: numpy.ndarray, 加速度计数据
    win: int, 窗口大小（秒），默认15
    sf: int, 采样频率（Hz），默认50
    
    返回:
    int: 翻身次数
    """
    if acc.size > 0:
        diff_acc = np.abs(acc[:, 1:] - acc[:, 0:-1])
        diff_acc = np.c_[diff_acc, [0, 0, 0]]

        avg_diff_acc = np.sum(np.reshape(np.sum(diff_acc, axis=0), [-1, sf * win]), axis=1) / (sf * win)
        # set max diff acc to 500
        avg_diff_acc[avg_diff_acc > 500] = 500
        normal_state = 100

        turnover = np.where(avg_diff_acc > normal_state)[0].shape[0]
    else:
        turnover = 0

    return turnover
