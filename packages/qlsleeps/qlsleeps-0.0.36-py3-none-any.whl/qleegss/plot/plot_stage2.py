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


def plot_stage(eeg, eeg_start_time, sf_eeg, eeg_path, acc, stage_res):
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(20, 4 * 4))
    # spectrogram
    t = plot_spectrogram(ax1, eeg, eeg_start_time, sf_eeg)
    # acc
    plot_acc(ax2, acc, eeg_start_time)
    # posture
    plot_sleep_posture(ax3, sleep_posture_analyse(acc), eeg_start_time)
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


def sleep_posture_analyse(acc, sf=50):
    """
    分析睡眠姿势
    
    Parameters:
    -----------
    acc : numpy.ndarray
        加速度数据，shape为(3, n)，分别代表x,y,z轴
    sf : int
        采样频率，默认50Hz
    
    Returns:
    --------
    grade : numpy.ndarray
        姿势角度，范围在[-π, π]之间
    """
    # 确保数据类型为float64
    acc_y = acc[1, :].astype(np.float64)
    acc_z = acc[2, :].astype(np.float64)
    
    # 首先对原始加速度信号进行滤波，去除高频噪声
    window_length = int(sf/2)  # 使用0.5秒的窗口
    if window_length % 2 == 0:
        window_length += 1
    acc_y = savgol_filter(acc_y, window_length=window_length, polyorder=2)
    acc_z = savgol_filter(acc_z, window_length=window_length, polyorder=2)
    
    # 计算倾角
    denominator = np.sqrt(acc_z * acc_z + acc_y * acc_y)
    cos = np.divide(acc_z, denominator, out=np.zeros_like(acc_z, dtype=np.float64), where=denominator!=0)
    cos = np.clip(cos, -1, 1)
    
    # 计算角度
    upper_grade = np.arccos(cos)
    direction = np.sign(acc_y)
    grade = upper_grade * direction
    
    # 使用更长的窗口进行最终平滑
    window_length = int(sf * 3)  # 使用3秒的窗口
    if window_length % 2 == 0:
        window_length += 1
    grade = savgol_filter(grade, window_length=window_length, polyorder=2)
    
    # 将角度规范化到[-π, π]区间
    grade = np.mod(grade + np.pi, 2 * np.pi) - np.pi
    
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
