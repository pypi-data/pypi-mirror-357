import pyedflib
import numpy as np
from scipy.signal import butter, lfilter, freqz
import matplotlib.pyplot as plt

def lowpass_filter(data, cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = lfilter(b, a, data)
    return y

def get_upright_periods(acc_data, g_magnitude=1.0, threshold_factor=0.9, min_duration_sec=20):
    """
    参数:
        acc_data (numpy.ndarray): 加速度计数据。
        g_magnitude (float): 重力加速度幅值 (例如 1.0 或 9.81)。
        threshold_factor (float): 用于确定主导轴阈值的因子。
        min_duration_sec (int): 直立时段被认为有效的最小持续时间（秒）。

    返回值:
        list: 元组列表，每个元组包含直立时段的 (开始时间, 结束时间, 持续时间)。
    """
        
    # 读取信号
    ax_orig = acc_data[0, :]
    ay_orig = acc_data[1, :]
    az_orig = acc_data[2, :]
    
    fs = 50
    # 应用1Hz低通滤波器
    cutoff_freq = 1.0  # 1 Hz
    ax_filtered = lowpass_filter(ax_orig, cutoff_freq, fs)
    ay_filtered = lowpass_filter(ay_orig, cutoff_freq, fs)
    az_filtered = lowpass_filter(az_orig, cutoff_freq, fs)

    n_samples = len(ax_filtered)
    is_upright = np.zeros(n_samples, dtype=bool)
    
    # 基于滤波后的加速度计数据确定直立姿态
    # 来自 acc_cal.py: 直立状态是当 ax ≈ -g 且为主导轴时
    # 传感器 +X 解剖学下方, +Y 解剖学右侧, +Z 解剖学前方
    # 直立状态: (-1g, 0, 0) -> ax 为主导轴且为负值

    threshold = g_magnitude * threshold_factor

    for i in range(n_samples):
        ax, ay, az = ax_filtered[i], ay_filtered[i], az_filtered[i]
        
        abs_ax = abs(ax)
        abs_ay = abs(ay)
        abs_az = abs(az)
        
        dominant_value = max(abs_ax, abs_ay, abs_az)

        if dominant_value < g_magnitude * 0.5: # 信号过弱或非静态
            is_upright[i] = False
            continue
        
        # 检查直立状态: Y轴主导且为负值
        if abs_ay >= threshold and abs_ay == dominant_value:# and ay < 0:
            is_upright[i] = True
        else:
            is_upright[i] = False
            
    # 查找直立时段的开始和结束时间
    upright_periods = []
    in_period = False
    start_sample = 0
    
    for i in range(n_samples):
        if is_upright[i] and not in_period:
            in_period = True
            start_sample = i
        elif not is_upright[i] and in_period:
            in_period = False
            end_sample = i -1 
            duration_samples = end_sample - start_sample + 1
            duration_sec = duration_samples / fs
            
            if duration_sec >= min_duration_sec:
                start_time = start_sample / fs
                end_time = (end_sample + 1) / fs # 结束时间应该是下一个时段的排他性开始，或指向实际结束
                upright_periods.append((start_time, end_time, duration_sec))
                
    # 如果最后一个时段是直立且延续到记录结束
    if in_period:
        end_sample = n_samples - 1
        duration_samples = end_sample - start_sample + 1
        duration_sec = duration_samples / fs
        if duration_sec >= min_duration_sec:
            start_time = start_sample / fs
            end_time = n_samples / fs
            upright_periods.append((start_time, end_time, duration_sec))
            
    # 创建一个仅反映经过确认和持续时间过滤的直立时段的掩码
    confirmed_upright_mask = np.zeros(n_samples, dtype=bool)
    for start_time, end_time, _ in upright_periods:
        start_sample_idx = int(start_time * fs)
        # 结束时间是排他性的或指向时段后下一个样本的开始
        # 因此，对于切片，end_sample_idx 应该是时段*内*的最后一个样本。
        # 如果 end_time = (actual_end_sample + 1) / fs，则 actual_end_sample = end_time * fs - 1
        end_sample_idx = int(end_time * fs) -1 
        # 确保索引在边界内，特别是对于最后一段
        if end_sample_idx >= n_samples:
            end_sample_idx = n_samples - 1
        if start_sample_idx < n_samples: # 确保 start_sample_idx 不超出边界，如果时段为空或异常
             confirmed_upright_mask[start_sample_idx : end_sample_idx + 1] = True

    return upright_periods, confirmed_upright_mask


    