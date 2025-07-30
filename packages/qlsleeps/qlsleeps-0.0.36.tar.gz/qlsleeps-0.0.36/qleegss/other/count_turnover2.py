import numpy as np
# 尝试导入 stride_tricks，如果失败则定义一个辅助函数
try:
    from numpy.lib.stride_tricks import sliding_window_view
    HAS_SLIDING_WINDOW_VIEW = True
except ImportError:
    HAS_SLIDING_WINDOW_VIEW = False
    # 简单的辅助函数实现滑动窗口（如果 numpy 版本较旧）
    def sliding_window_view_manual(arr, window_shape, step=1):
        """ 手动实现类似 numpy 1.20+ 的 sliding_window_view 功能 """
        in_shape = np.array(arr.shape)
        window_shape = np.array(window_shape)
        step = np.array(step) if isinstance(step, (list, tuple, np.ndarray)) else np.full(arr.ndim, step)

        out_shape = (in_shape - window_shape) // step + 1
        if np.any(out_shape <= 0):
             raise ValueError("窗口太大或步长太大，无法生成有效窗口")

        n_dim = arr.ndim
        view_shape = tuple(out_shape) + tuple(window_shape)

        in_strides = np.array(arr.strides)
        view_strides = tuple(in_strides * step) + tuple(in_strides)

        return np.lib.stride_tricks.as_strided(arr, shape=view_shape, strides=view_strides)


def count_turnover(acc, window_sec=10, step_sec=5, sf=50, activity_threshold=0.1, use_std_dev=False):
    """
    计算加速度数据中的翻身次数 (修订版 - 针对 3xN 输入)

    使用滑动窗口计算活动度量（基于原始代码的总绝对差分 或 标准差），
    并通过检测活动状态的变化来识别和计数翻身事件。

    参数:
    acc: numpy.ndarray, 加速度计数据 (3 x N)，单位应一致 (例如 g 或 m/s^2).
    window_sec: float, 滑动窗口大小（秒）。默认10秒。
    step_sec: float, 滑动窗口步长（秒）。默认5秒 (50%重叠)。
    sf: int, 采样频率（Hz），默认50。
    activity_threshold: float, 活动阈值。窗口活动度量超过此值则为“活跃”。
                              需要根据数据和 use_std_dev 选择进行调整。
                              默认 0.1 是一个示例值。
    use_std_dev: bool, 如果为 True，则窗口活动度量使用标准差，否则使用原始代码的
                       平均总绝对差分。标准差通常更鲁棒。默认 False。

    返回:
    int: 估算的翻身次数。
    """
    if acc.shape[0] != 3:
        raise ValueError(f"输入加速度数据应为 3 x N 形状, 实际为 {acc.shape}")
    n_axes, n_samples = acc.shape

    if n_samples == 0:
        print("警告: 输入的加速度数据为空。")
        return 0

    # --- 1. 计算核心运动度量 ---
    # 计算相邻样本差值: acc[axis, t+1] - acc[axis, t]
    diff_acc = np.diff(acc, axis=1) # Shape: (3, N-1)

    if use_std_dev:
        # 方案 A: 计算每个时间点差分向量的幅度，后续窗口计算其标准差
        # delta_mag = np.sqrt(np.sum(diff_acc**2, axis=0)) # L2 范数
        delta_mag = np.sum(np.abs(diff_acc), axis=0) # L1 范数 (更接近原始代码)
        # delta_mag shape: (N-1,)
        signal_for_windowing = delta_mag
    else:
        # 方案 B: 使用原始代码的核心度量：总绝对差分
        # sum_abs_diff = np.sum(np.abs(diff_acc), axis=0) # Shape: (N-1,)
        signal_for_windowing = np.sum(np.abs(diff_acc), axis=0) # Shape: (N-1,)

    if signal_for_windowing.size == 0:
        print("警告: 计算差分后数据为空。")
        return 0

    # --- 2. 定义窗口和步长的样本数 ---
    win_samples = int(window_sec * sf)
    step_samples = int(step_sec * sf)

    # 基本检查
    if win_samples <= 0: raise ValueError("窗口大小必须为正数。")
    if step_samples <= 0: raise ValueError("窗口步长必须为正数。")
    if win_samples > signal_for_windowing.shape[0]:
        print(f"警告: 数据长度 ({signal_for_windowing.shape[0]} 个变化点) 不足以容纳一个完整的窗口 ({win_samples} 点)。")
        return 0

    # --- 3. 使用滑动窗口计算活动度量 ---
    try:
        if HAS_SLIDING_WINDOW_VIEW:
            # 使用 NumPy 1.20+ 的高效实现
            windows = sliding_window_view(signal_for_windowing, window_shape=win_samples)[::step_samples]
        else:
            # 使用手动实现的版本（效率较低）
            windows = sliding_window_view_manual(signal_for_windowing, window_shape=win_samples, step=step_samples)

        if use_std_dev:
            # 计算每个窗口的标准差
            window_activity = np.std(windows, axis=1)
        else:
            # 计算每个窗口的平均总绝对差分 (模拟原始代码的窗口度量)
            window_activity = np.mean(windows, axis=1)

    except ValueError as e:
        print(f"错误: 创建滑动窗口时出错: {e}")
        return 0 # 或者其他错误处理

    # --- 4. 识别和计数翻身事件 ---
    is_active = window_activity > activity_threshold
    is_active_int = is_active.astype(int)
    # prepend=0 假设开始时是非活动状态
    changes = np.diff(is_active_int, prepend=0)
    # 计算从非活动变为活动 (0 -> 1) 的次数
    turnover_count = np.sum(changes == 1)

    return turnover_count

# --- 示例用法 (假设数据是 3xN) ---
# sf_real = 50
# np.random.seed(0)
# duration_minutes = 30
# n_points = duration_minutes * 60 * sf_real
# # 生成 3xN 的数据
# my_acc_data_3xn = np.random.randn(3, n_points) * 0.1
# # 模拟几次 "翻身"
# for _ in range(5):
#     start = np.random.randint(0, n_points - 5 * sf_real)
#     end = start + np.random.randint(2*sf_real, 5*sf_real)
#     my_acc_data_3xn[:, start:end] += np.random.randn(3, end-start) * 0.5

# print(f"生成的测试数据形状: {my_acc_data_3xn.shape}")

# # 调用修订后的函数 (使用原始代码的度量逻辑)
# estimated_turnovers_orig_metric = count_turnover_revised_3xn(
#     my_acc_data_3xn,
#     window_sec=10,
#     step_sec=5,
#     sf=sf_real,
#     activity_threshold=0.05, # !!! 阈值需要根据数据和 use_std_dev=False 重新调整 !!!
#     use_std_dev=False
# )
# print(f"估算的翻身次数 (基于平均总绝对差分): {estimated_turnovers_orig_metric}")

# # 调用修订后的函数 (使用标准差作为度量)
# estimated_turnovers_stddev_metric = count_turnover_revised_3xn(
#     my_acc_data_3xn,
#     window_sec=10,
#     step_sec=5,
#     sf=sf_real,
#     activity_threshold=0.08, # !!! 阈值需要根据数据和 use_std_dev=True 重新调整 !!!
#     use_std_dev=True
# )
# print(f"估算的翻身次数 (基于标准差): {estimated_turnovers_stddev_metric}")