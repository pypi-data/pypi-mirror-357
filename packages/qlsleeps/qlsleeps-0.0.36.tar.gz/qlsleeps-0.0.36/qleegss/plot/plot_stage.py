"""
绘制分期图
"""
import matplotlib.pyplot as plt
from qleegss.plot.plot_eeg_spectrogram import plot_spectrogram
import numpy as np
from datetime import timedelta, datetime
import matplotlib.dates as mdates
from scipy.signal import savgol_filter
from qleegss.plot.plot_acc import plot_acc
from scipy.signal import butter, filtfilt, medfilt



def plot_stage(eeg, eeg_start_time, sf_eeg, eeg_path, acc, stage_res):
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(20, 4 * 4))
    # spectrogram
    t = plot_spectrogram(ax1, eeg, eeg_start_time, sf_eeg)
    # acc
    plot_acc(ax2, acc, eeg_start_time)
    # posture
    plot_sleep_posture(ax3, sleep_posture_analyse_robust(acc), eeg_start_time)
    # stage
    plot_stage_res(ax4, stage_res, eeg_start_time)

    # config
    plt.tight_layout()
    save_path = eeg_path.replace('eeg.eeg', 'sleep_fig.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close('all')


def plot_sleep_posture(ax, grade, start_time):
    sf = 50
    # assert grade.shape[0] == 1, "The grade of head bias should be a 1-D ndarray"
    t = np.arange(grade.shape[0]) / sf / 3600
    timestamp = [start_time + timedelta(hours=hours) for hours in t]
    timestamp_num = mdates.date2num(timestamp)
    ax.plot(timestamp_num, grade, lw=1.5, color='b')
    ax.set_ylim(-3.5, 3.5)
    ax.tick_params(axis='y', labelsize=14)
    ax.tick_params(axis='x', labelsize=14)
    ax.set_yticks([-np.pi, -np.pi / 2, 0, np.pi / 2, np.pi])
    ax.set_yticklabels(['Sleep Face Down', 'Lie on the Left', 'Lie Flat', 'Lie on the Right', 'Sleep Face Down'], )
    ax.set_ylabel("Sleep Postures", fontdict={"fontsize": 18})
    ax.set_xlabel("Time [hrs]", fontdict={"fontsize": 18})
    ax.grid(visible=True, axis='y', linewidth=0.5)

    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.set_xlim(timestamp[0], timestamp[-1])


def sleep_posture_analyse(acc):
    # 滤波结果不佳，后续再调整
    # print(acc.shape)
    # # 添加10Hz高通滤波
    # sf = 50  # 采样频率
    # nyq = sf / 2  # 奈奎斯特频率
    # cutoff = 20  # 截止频率
    # order = 4  # 滤波器阶数
    # b, a = butter(order, cutoff/nyq, btype='low')
    
    # 对y和z轴信号进行滤波
    # acc_y = filtfilt(b, a, acc[1, :])
    # acc_z = filtfilt(b, a, acc[2, :])

    acc_y = acc[1, :]
    acc_z = acc[2, :]
    cos = acc_z / (np.sqrt(acc_z * acc_z + acc_y * acc_y))
    # denominator = np.sqrt(acc_z * acc_z + acc_y * acc_y)
    # cos = np.divide(acc_z, denominator, out=np.zeros_like(acc_z), where=denominator!=0)
    upper_grade = np.arccos(cos)
    grade = upper_grade * (acc_y / (np.abs(acc_y)+1e-16))    
    grade = savgol_filter(grade, window_length=10, polyorder=1)
    # grade = filtfilt(b, a, grade)

    return grade


def sleep_posture_analyse_revised(acc, sf=50, lowpass_cutoff=1.0, savgol_window_sec=3.0, savgol_order=1):
    """
    分析加速度数据，计算睡眠姿态角度 (修订版)

    使用 Y 轴和 Z 轴加速度数据，通过 atan2 计算头部在 Y-Z 平面相对于
    重力的角度，以区分平躺、左侧卧、右侧卧和俯卧等姿势。
    增加了低通滤波和更合适的 Savitzky-Golay 平滑。

    参数:
    acc: numpy.ndarray, 加速度计数据, 形状为 3xN (3轴, N个样本点)
    sf: int, 采样频率 (Hz)，默认 50
    lowpass_cutoff: float, 低通滤波器截止频率 (Hz)。用于去除与姿态无关的高频噪声。
                         设为 None 则禁用低通滤波。默认 1.0 Hz。
    savgol_window_sec: float, Savitzky-Golay 平滑窗口大小 (秒)。默认 3.0 秒。
    savgol_order: int, Savitzky-Golay 滤波器多项式阶数。默认 1 (线性)。

    返回:
    numpy.ndarray: 平滑后的姿态角度时间序列 (弧度)。
                   角度范围大致对应关系 (需要根据实际佩戴和校准确认):
                   - 接近 0: 平躺 (仰卧, Z轴向上)
                   - 接近 +pi/2 (约 +1.57): 右侧卧 (Y轴向上)
                   - 接近 -pi/2 (约 -1.57): 左侧卧 (Y轴向下)
                   - 接近 +pi 或 -pi (约 +/-3.14): 俯卧 (Z轴向下)
    """
    if acc.shape[0] != 3:
        raise ValueError(f"输入加速度数据应为 3 x N 形状, 实际为 {acc.shape}")
    n_axes, n_samples = acc.shape

    if n_samples == 0:
        print("警告: 输入的加速度数据为空。")
        return np.array([])

    acc_y = acc[1, :]
    acc_z = acc[2, :]

    # 1. [可选但推荐] 应用低通滤波去除高频噪声
    if lowpass_cutoff is not None and lowpass_cutoff > 0:
        try:
            nyq = 0.5 * sf
            cutoff_norm = lowpass_cutoff / nyq
            # 设计低通滤波器 (Butterworth 通常效果不错)
            # 注意: 阶数order可以调整，这里用4阶
            b, a = butter(4, cutoff_norm, btype='low', analog=False)
            # 对 Y 和 Z 轴数据进行零相位滤波
            acc_y = filtfilt(b, a, acc_y)
            acc_z = filtfilt(b, a, acc_z)
        except ValueError as e:
            print(f"警告: 低通滤波失败 (可能是截止频率相对于采样率过高或过低): {e}。将使用原始数据。")
            acc_y = acc[1, :] # 使用原始数据
            acc_z = acc[2, :]

    # 2. 使用 arctan2 计算角度
    #    np.arctan2(y, x) 计算 (x, y) 向量与 x 轴正方向的夹角
    #    我们用 (acc_z, acc_y)，计算的是重力在 YZ 平面的投影向量
    #    与传感器 Z 轴正方向的夹角。
    #    返回值范围是 (-pi, pi]
    grade = np.arctan2(acc_y, acc_z)

    # 3. 应用 Savitzky-Golay 滤波器平滑角度信号
    #    窗口长度需要是奇数，且大于多项式阶数
    window_length_samples = int(savgol_window_sec * sf)
    # 确保窗口长度是奇数
    if window_length_samples % 2 == 0:
        window_length_samples += 1
    # 确保窗口长度大于阶数
    if window_length_samples <= savgol_order:
        print(f"警告: Savitzky-Golay 窗口长度 ({window_length_samples}) 不大于阶数 ({savgol_order})。将尝试使用最小有效窗口长度 ({savgol_order + 1 + (savgol_order % 2)})。")
        window_length_samples = savgol_order + 1 + (savgol_order % 2) # 保证奇数且大于阶数

    if n_samples < window_length_samples:
         print(f"警告: 数据点数 ({n_samples}) 少于 Savitzky-Golay 窗口长度 ({window_length_samples})。无法进行平滑。")
         # 可以选择返回未平滑的角度，或者返回空数组/错误
         return grade # 返回未平滑的角度

    try:
        grade = savgol_filter(grade, window_length=window_length_samples, polyorder=savgol_order)
    except ValueError as e:
        print(f"错误: Savitzky-Golay 滤波失败: {e}")
        # 可以选择返回未平滑的角度，或者返回空数组/错误
        return grade # 返回未平滑的角度


    return grade



def sleep_posture_analyse_robust(acc, sf=50,
                                 lowpass_cutoff=0.5, # 降低默认截止频率
                                 use_median_filter=True, # 增加中值滤波选项
                                 median_filter_sec=2.1, # 中值滤波窗口
                                 savgol_window_sec=40.0, # 大幅增加默认 SavGol 窗口
                                 savgol_order=1):
    """
    分析加速度数据，计算睡眠姿态角度 (更鲁棒的版本)

    针对可能出现的剧烈震荡进行了优化，通过更强的低通滤波、
    可选的中值滤波和更长的 Savitzky-Golay 平滑窗口来抑制快速变化，
    关注慢速的姿态趋势。

    参数:
    acc: numpy.ndarray, 加速度计数据, 形状为 3xN (3轴, N个样本点)
    sf: int, 采样频率 (Hz)，默认 50
    lowpass_cutoff: float or None, 低通滤波器截止频率 (Hz)。设为 None 禁用。默认 0.5 Hz。
    use_median_filter: bool, 是否在 SavGol 滤波前使用中值滤波。默认 True。
    median_filter_sec: float, 中值滤波器窗口大小 (秒)。默认 1.5 秒。
    savgol_window_sec: float, Savitzky-Golay 平滑窗口大小 (秒)。默认 15.0 秒。
    savgol_order: int, Savitzky-Golay 滤波器多项式阶数。默认 1 (线性)。

    返回:
    numpy.ndarray: 平滑后的姿态角度时间序列 (弧度)。
                   角度范围大致对应关系 (需校准):
                   ~0: 平躺, ~+pi/2: 右侧卧, ~-pi/2: 左侧卧, ~+/-pi: 俯卧
    """
    if acc.shape[0] != 3:
        raise ValueError(f"输入加速度数据应为 3 x N 形状, 实际为 {acc.shape}")
    n_axes, n_samples = acc.shape

    if n_samples == 0:
        print("警告: 输入的加速度数据为空。")
        return np.array([])

    acc_y = acc[1, :]
    acc_z = acc[2, :]

    # 1. 应用低通滤波 (更低的默认截止频率)
    if lowpass_cutoff is not None and lowpass_cutoff > 0:
        try:
            nyq = 0.5 * sf
            cutoff_norm = lowpass_cutoff / nyq
            if cutoff_norm >= 1.0 or cutoff_norm <= 0:
                 raise ValueError("截止频率必须在 0 和 Nyquist 频率之间。")
            b, a = butter(4, cutoff_norm, btype='low', analog=False)
            acc_y = filtfilt(b, a, acc_y)
            acc_z = filtfilt(b, a, acc_z)
        except ValueError as e:
            print(f"警告: 低通滤波失败: {e}。将使用原始数据进行后续计算。")
            acc_y = acc[1, :]
            acc_z = acc[2, :]

    # 2. 使用 arctan2 计算角度
    grade = np.arctan2(acc_y, acc_z)

    # 3. [可选] 应用中值滤波去除脉冲噪声
    if use_median_filter:
        median_window_len = int(median_filter_sec * sf)
        # 确保窗口长度是奇数
        if median_window_len % 2 == 0:
            median_window_len += 1
        if median_window_len < 3:
             median_window_len = 3 # 最小有效长度

        if n_samples >= median_window_len:
            try:
                grade = medfilt(grade, kernel_size=median_window_len)
            except ValueError as e:
                 print(f"警告: 中值滤波失败: {e}。跳过中值滤波。")
        else:
            print(f"警告: 数据点数 ({n_samples}) 少于中值滤波窗口长度 ({median_window_len})。跳过中值滤波。")


    # 4. 应用 Savitzky-Golay 滤波器进行平滑 (更长的默认窗口)
    savgol_window_len = int(savgol_window_sec * sf)
    if savgol_window_len % 2 == 0:
        savgol_window_len += 1
    if savgol_window_len <= savgol_order:
        print(f"警告: Savitzky-Golay 窗口长度 ({savgol_window_len}) 不大于阶数 ({savgol_order})。调整为最小有效长度。")
        savgol_window_len = savgol_order + 1 + (savgol_order % 2)

    if n_samples < savgol_window_len:
         print(f"警告: 数据点数 ({n_samples}) 少于 Savitzky-Golay 窗口长度 ({savgol_window_len})。无法进行平滑。")
         return grade # 返回可能经过中值滤波但未经过 SavGol 平滑的角度

    try:
        grade = savgol_filter(grade, window_length=savgol_window_len, polyorder=savgol_order)
    except ValueError as e:
        print(f"错误: Savitzky-Golay 滤波失败: {e}")
        return grade # 返回可能经过中值滤波但未经过 SavGol 平滑的角度

    return grade


def plot_stage_res(ax, hypno, start_time):
    # print(hypno)
    win = 30
    t = np.arange(hypno.size) * win / 3600
    timestamp = [start_time + timedelta(hours=hours) for hours in t]
    timestamp_num = mdates.date2num(timestamp)

    n3_sleep = np.ma.masked_not_equal(hypno, 0)
    n2_sleep = np.ma.masked_not_equal(hypno, 1)
    n1_sleep = np.ma.masked_not_equal(hypno, 2)
    rem_sleep = np.ma.masked_not_equal(hypno, 3)
    wake = np.ma.masked_not_equal(hypno, 4)
    abnormal = np.ma.masked_not_equal(hypno, 5)

    ax.plot(timestamp_num, hypno, lw=2, color='k')
    ax.plot(timestamp_num, abnormal, lw=2, color='k')
    ax.plot(timestamp_num, wake, lw=2, color='orange')
    ax.plot(timestamp_num, rem_sleep, lw=2, color='lime')
    ax.plot(timestamp_num, n1_sleep, lw=2, color='yellowgreen')
    ax.plot(timestamp_num, n2_sleep, lw=2, color='deepskyblue')
    ax.plot(timestamp_num, n3_sleep, lw=2, color='royalblue')

    ax.set_ylim([-0.1, 5.8])
    ax.set_yticks([0, 1, 2, 3, 4, 5])
    ax.set_yticklabels(['N3 Sleep', 'N2 Sleep', 'N1 Sleep', 'REM Sleep', 'Wake', 'Abnormal'], )
    ax.tick_params(axis='y', labelsize=14)
    ax.tick_params(axis='x', labelsize=14)
    ax.set_ylabel("Sleep Staging Result", fontdict={"fontsize": 18})
    ax.set_xlabel("Time [hrs]", fontdict={"fontsize": 18})

    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.set_xlim([timestamp_num[0], timestamp_num[-1]])


if __name__ == '__main__':
    eeg_ = np.random.rand(30000)
    acc_ = np.random.rand(3, 30000)
    stage_res_ = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    plot_stage(eeg_, datetime.now(), 100, './eeg.eeg', acc_, stage_res_)
    plt.show()
