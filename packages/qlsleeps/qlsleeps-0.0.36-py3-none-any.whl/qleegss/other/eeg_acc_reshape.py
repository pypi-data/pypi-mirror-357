import scipy.signal as signal
from qleegss.eeg2edf.qlelib import qle_sp_cal
from scipy import interpolate
from scipy.signal import resample_poly
import numpy as np


def eeg_acc_reshape(sample_rate, acc, *args):
    # 直接在原始数据上进行操作，不创建新的数组
    # acc只进行了长度裁剪，没有进行重采样
    # 15 * 50 表示每15秒有750个点，说明acc原始采样率为50Hz
    # acc = acc[:, : acc.shape[1] // (15 * 50) * (15 * 50)]
    acc = acc[:, : acc.shape[1] // (30 * 50) * (30 * 50)]
    fs = round(sample_rate)
    print(fs)
    #-------------zhd原代码--------------------------------
    # 使用列表推导式和切片来进行原地操作
    # EEG信号重采样：500Hz -> 100Hz
    # 原始：30秒 * 500Hz = 15000个点
    # 重采样后：30秒 * 100Hz = 3000个点
    # eeg_reshaped = [
    #     signal.resample(eeg[:eeg.shape[0] // (30 * fs) * (30 * fs)].reshape(-1, 30 * fs), 100 * 30, axis=1).ravel()
    #     for eeg in args]

    eeg_reshaped = [
        signal.resample(eeg[:eeg.shape[0] // (30 * 500) * (30 * 500)].reshape(-1, 30 * 500), 100 * 30, axis=1).ravel()
        for eeg in args]
    #-------------zhd原代码--------------------------------

    # ------------插值方法--------------------------------
    # print(sf_eeg)
    # eeg_reshaped = []
    # for eeg in args:
    #     print(len(eeg))
    #     t = len(eeg) / sf_eeg
    #     print(t)
    #     # t_actual = np.arange(0, t, 1/sf_eeg)
    #     # 创建插值函数
    #     # interp_func = interpolate.interp1d(t_actual, eeg, kind='linear', fill_value="extrapolate")
    #     # 生成新的时间轴
    #     # t_new = np.arange(0, t, 1/100)  # 目标采样率100Hz
    #     # eeg_resampled = interp_func(t_new)
    #     # 使用resample_poly进行重采样
    #     eeg_resampled = resample_poly(eeg, 100, round(sf_eeg))
    #     resampled_eeg = eeg_resampled[:eeg_resampled.shape[0] // (30 * 100) * (30 * 100)]
    #     # resampled_eeg = signal.resample(eeg_resampled[:eeg_resampled.shape[0] // (30 * 500) * (30 * 500)].reshape(-1, 30 * 500), 100 * 30, axis=1).ravel()
    #     eeg_reshaped.append(resampled_eeg)

    
    # 返回结果，使用解包来返回多个值
    return acc, *eeg_reshaped



def ecg_emg_reshape(ecg, emg, sample_rate):

    fs = round(sample_rate)

    #-------------zhd原代码--------------------------------
    # ECG和EMG信号重采样：500Hz -> 50Hz
    # 原始：30秒 * 500Hz = 15000个点
    # 重采样后：30秒 * 50Hz = 1500个点
    ecg = signal.resample(ecg[:ecg.shape[0] // (30 * fs) * (30 * fs)].reshape(-1, 30 * fs), 50 * 30, axis=1).ravel()
    emg = signal.resample(emg[:emg.shape[0] // (30 * fs) * (30 * fs)].reshape(-1, 30 * fs), 50 * 30, axis=1).ravel()
    #-------------zhd原代码--------------------------------

    # ------------插值方法--------------------------------
    # t = len(ecg) / sf_eeg
    # t_actual = np.arange(0, len(ecg)) / sf_eeg
    # # 重采样ecg
    # interp_func = interpolate.interp1d(t_actual, ecg, kind='linear', fill_value="extrapolate")
    # t_new = np.arange(0, len(ecg)) / 500  # 目标采样率500Hz
    # ecg_resampled = interp_func(t_new)
    # resampled_ecg = signal.resample(ecg_resampled[:ecg_resampled.shape[0] // (30 * 500) * (30 * 500)].reshape(-1, 30 * 500), 50 * 30, axis=1).ravel()

    # # 重采样emg
    # interp_func = interpolate.interp1d(t_actual, emg, kind='linear', fill_value="extrapolate")
    # t_new = np.arange(0, len(emg)) / 500  # 目标采样率500Hz
    # emg_resampled = interp_func(t_new)
    # resampled_emg = signal.resample(emg_resampled[:emg_resampled.shape[0] // (30 * 500) * (30 * 500)].reshape(-1, 30 * 500), 50 * 30, axis=1).ravel()


    # 返回结果，使用解包来返回多个值
    return ecg, emg

'''

def ecg_emg_reshape(ecg, emg, sample_rate):
    fs = round(sample_rate)
    
    # 新增采样率合理性校验
    if not (100 <= fs <= 1000):  # 生物电信号典型采样率范围
        raise ValueError(f"异常采样率: {fs}Hz，请检查设备配置")
    
    # 计算分段长度并确保最小数据长度
    segment_length = 30 * fs
    if len(ecg) < segment_length:
        raise ValueError(f"ECG数据过短（{len(ecg)}样本），无法满足{fs}Hz采样率要求")
    
    # 安全截断（显式长度校验）
    trunc_length = len(ecg) // segment_length * segment_length
    ecg_trunc = ecg[:trunc_length]
    emg_trunc = emg[:trunc_length]
    
    # 维度重塑校验
    try:
        ecg_reshaped = ecg_trunc.reshape(-1, segment_length)
        emg_reshaped = emg_trunc.reshape(-1, segment_length)
    except ValueError as e:
        raise ValueError(f"维度重塑错误: {e}，输入长度: {len(ecg_trunc)}，分段尺寸: {segment_length}") from e
    
    # 明确指定目标采样点数
    target_points = 50 * 30  # 50Hz采样率下30秒对应1500个点
    ecg_resampled = signal.resample(ecg_reshaped, target_points, axis=1)
    emg_resampled = signal.resample(emg_reshaped, target_points, axis=1)
    
    return ecg_resampled.ravel(), emg_resampled.ravel()

'''