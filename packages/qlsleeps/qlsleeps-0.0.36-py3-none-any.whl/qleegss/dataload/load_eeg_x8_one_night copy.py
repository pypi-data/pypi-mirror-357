"""
load eeg x8 data
"""
import numpy as np
from datetime import datetime, timedelta


def load_eeg_x8_one_night(eeg_path):
    channel_count = 2
    with open(eeg_path, 'rb') as eeg_data:
        eeg_data.seek(8, 0)
        length = int.from_bytes(eeg_data.read(4), byteorder='little', signed=False)
        eeg_data.seek(21, 0)
        sample_count = int.from_bytes(eeg_data.read(4), byteorder='little', signed=False)
        eeg_data.seek(16, 0)
        point_bytes = int.from_bytes(eeg_data.read(1), byteorder='little', signed=False)
        # start time
        eeg_data.seek(33, 0)
        start_time = int.from_bytes(eeg_data.read(8), byteorder='little', signed=False) / 1000
        eeg_start_time = datetime.fromtimestamp(start_time)
        # end_time
        eeg_data.seek(41, 0)
        end_time = int.from_bytes(eeg_data.read(8), byteorder='little', signed=False) / 1000
        eeg_end_time = datetime.fromtimestamp(end_time)

    with open(eeg_path, 'rb') as f:
        byte_data = f.read()

    all_package = np.frombuffer(byte_data, dtype=np.uint8)[length:]
    del byte_data
    package_length = sample_count * point_bytes * channel_count + 18
    # -----------------------------------------------------------------------------------------------------
    # 之前计算丢包率的方法  copy by zheng xin
    all_package_time = all_package.reshape(-1, package_length)[:, 2:10]
    all_package_id = all_package.reshape(-1, package_length)[:, 10:14]

    # computing package loss rate/disconnection rate
    all_package_id = all_package_id.astype(np.uint8)
    all_package_id = np.apply_along_axis(int_from_bytes_4bit, axis=1, arr=all_package_id)
    all_package_id = all_package_id.astype(np.int32)

    all_package_time = all_package_time.astype(np.uint8)
    all_package_time = np.apply_along_axis(int_from_bytes_8bit, axis=1, arr=all_package_time)
    all_package_time = all_package_time.astype(np.int32)

    package_time_interval = all_package_time[1:] - all_package_time[:-1]
    disconnect_point = np.where(package_time_interval > 3000)[0]

    disconnection_sum = 0

    package_segment = [0]
    if disconnect_point is not None and len(disconnect_point) > 0:
        for i in range(len(disconnect_point)):
            package_segment.append(disconnect_point[i])
            package_segment.append(disconnect_point[i] + 1)
            disconnection_sum += all_package_time[disconnect_point[i] + 1] - all_package_time[disconnect_point[i]]

    disconnect_rate = disconnection_sum / all_package_time[-1]

    package_segment.append(all_package_id.shape[0] - 1)
    package_segment = np.array(package_segment).reshape([-1, 2])

    package_sum = 0
    loss_package_sum = 0
    for i in range(package_segment.shape[0]):
        left = package_segment[i][0]
        right = package_segment[i][1]
        package_sum += all_package_id[right] - 0 + 1
        loss_package_sum += all_package_id[right] - 0 + 1 - (right - left + 1)
    package_loss_rate = loss_package_sum / package_sum
    # -----------------------------------------------------------------------------------------------------
    all_package = all_package.reshape(-1, package_length)[:, 18:package_length].reshape(-1, point_bytes)
    all_package_data = all_package[:, 0] + all_package[:, 1] * 256
    del all_package
    raw_data = np.squeeze(all_package_data)
    del all_package_data
    data = np.transpose(raw_data.reshape(-1, channel_count))[0, :].astype(np.int32)
    del raw_data
    eeg = (data - 32767) / 32767 * 2.5 * 1000 * 1000 / 192
    del data

    # 断连和丢包率
    # disconnect_rate = 0
    # package_loss_rate = 0
    # -----------------------------------------------------------------------------------------------------
    # patch 结束时间显示问题 bug
    eeg_end_time = eeg_end_time if eeg_end_time > eeg_start_time else eeg_start_time + timedelta(seconds=int(eeg.size/500))

    return eeg, eeg_start_time, eeg_end_time, disconnect_rate, package_loss_rate


def int_from_bytes_8bit(byte_arr):
    buffer = np.asarray(
        [1, 256, np.power(np.int64(256), 2), np.power(np.int64(256), 3), np.power(np.int64(256), 4),
         np.power(np.int64(256), 5), np.power(np.int64(256), 6), np.power(np.int64(256), 7)])

    res = byte_arr[0] * buffer[0] + byte_arr[1] * buffer[1] + byte_arr[2] * buffer[2] + byte_arr[3] * buffer[
        3] + byte_arr[4] * buffer[4] + byte_arr[5] * buffer[5] + byte_arr[6] * buffer[6] + byte_arr[7] * buffer[7]
    return np.sum(res)


def int_from_bytes_4bit(byte_arr):
    buffer = np.asarray([1, 256, np.power(np.int64(256), 2), np.power(np.int64(256), 3)])
    res = byte_arr[0] * buffer[0] + byte_arr[1] * buffer[1] + byte_arr[2] * buffer[2] + byte_arr[3] * buffer[3]
    return np.sum(res)


if __name__ == '__main__':
    eeg_path_ = r'D:\X8_dataset\13639\eeg.eeg'
    data_ = load_eeg_x8_one_night(eeg_path_)
    print(data_[0].shape)
