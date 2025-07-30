#使用双模型进行预测
import numpy as np
import torch
import os
import torch.nn.functional as F
from qleegss.model.sleepyco_net import MainModel
import tracemalloc
import mne
import yasa
import warnings
from sklearn.exceptions import InconsistentVersionWarning

# 忽略特定的警告
warnings.filterwarnings('ignore', category=InconsistentVersionWarning)
warnings.filterwarnings('ignore', category=UserWarning)

def predict_one_trail(eeg):
    net = create_model()
    res = []
    prob = []
    temperature = 2
    net.eval()
    eeg = torch.from_numpy(eeg.reshape(-1, 100*30)).float()
    w_nn = 0.5
    w_yasa = 0.5
    with torch.no_grad():
        for i in range(eeg.shape[0]):
            if i < 10:
                inputs = eeg[:i + 1, :]
                inputs = inputs.reshape(1, 1, -1)
                outputs = net(inputs)
                outputs_sum = torch.zeros_like(outputs[0])
                for j in range(len(outputs)):
                    outputs_sum += outputs[j]
                scaled_outputs = outputs_sum / temperature
                probabilities = F.softmax(scaled_outputs, dim=-1)
                pro_all = probabilities
            else:
                inputs = eeg[i - 10:i, :]
                inputs = inputs.reshape(1, 1, -1)
                outputs = net(inputs)
                outputs_sum = torch.zeros_like(outputs[0])
                for j in range(len(outputs)):
                    outputs_sum += outputs[j]
                scaled_outputs = outputs_sum / temperature
                probabilities = F.softmax(scaled_outputs, dim=-1)

                try:
                    info = mne.create_info(ch_names=['EEG'], sfreq=100, ch_types=['eeg'])
                    eeg_data = inputs.squeeze().numpy()
                    eeg_data = eeg_data.reshape(1, -1)
                    raw = mne.io.RawArray(eeg_data, info)
                    sls = yasa.SleepStaging(raw, eeg_name='EEG')
                    predict_proba_df = sls.predict_proba()
                    predict_proba = torch.from_numpy(predict_proba_df.values).float()
                    predict_proba = predict_proba[-1:, :]  # 获取最后一行

                    # 创建6类的概率tensor
                    yasa_proba = torch.zeros((1, 6))
                    # 保持原始标签顺序，之后再映射
                    yasa_proba[0, :5] = predict_proba[0, :]  # 复制前5个类别的概率
                    yasa_proba[0, 5] = 0.0  # 异常类别概率为0

                    yasa_proba = yasa_proba.to(probabilities.device)
                    pro_all = w_nn * probabilities + w_yasa * yasa_proba
                except Exception as e:
                    print(f"YASA prediction failed: {e}")
                    pro_all = probabilities

            predicted = torch.argmax(pro_all, dim=-1)
            max_prob = pro_all[0, predicted]
            res.append(predicted.item())
            prob.append(max_prob.item())

        # 最后进行标签映射
        map_dict = {
            3: 0,  # N3
            2: 1,  # N2
            1: 2,  # N1
            4: 3,  # REM
            0: 4,  # Wake
            5: 5   # Abnormal
        }
        res = [map_dict.get(x, x) for x in res]
    return np.asarray(res), np.asarray(prob)


def yasa_predict(eeg_data, sfreq=100):
    # 确保数据是numpy数组
    if isinstance(eeg_data, torch.Tensor):
        eeg_data = eeg_data.numpy()
    
    # 创建MNE Raw对象
    info = mne.create_info(ch_names=['EEG'], sfreq=sfreq, ch_types=['eeg'])
    raw = mne.io.RawArray(eeg_data.reshape(1, -1), info)
    
    # 使用YASA进行睡眠分期
    sls = yasa.SleepStaging(raw, eeg_name='EEG')
    stages = sls.predict()
    
    # YASA标签映射到您的标签系统
    # YASA的标签: W=0, N1=1, N2=2, N3=3, REM=4
    yasa_to_model_map = {
        'W': 4,    # Wake -> 4
        'N1': 2,   # N1 -> 2
        'N2': 1,   # N2 -> 1
        'N3': 0,   # N3 -> 0
        'REM': 3,  # REM -> 3
    }
    
    # 应用映射
    mapped_stages = [yasa_to_model_map.get(stage, 5) for stage in stages]  # 未知标签映射为5(Abnormal)
    
    return np.asarray(mapped_stages)



def predict_one_epoch(eeg):
    net = create_model()
    net.eval()
    eeg = torch.from_numpy(eeg).reshape(1, 1, -1).float()
    with torch.no_grad():
        outputs = net(eeg)
        outputs_sum = torch.zeros_like(outputs[0])
        for j in range(len(outputs)):
            outputs_sum += outputs[j]
        predicted = torch.argmax(outputs_sum)
        map_dict = {
            3: 0,
            2: 1,
            1: 2,
            4: 3,
            0: 4,
            5: 5
        }
    return map_dict.get(int(predicted.item()))


def create_model():
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    net = MainModel()
    net.eval()
    state_dict = torch.load(script_dir + '/ckpt_fold-01.pth', map_location=torch.device('cpu'), weights_only=True)
    new_state_dict = {}
    for k, v in state_dict.items():
        name = k.replace('module.', '')
        new_state_dict[name] = v
    net.load_state_dict(new_state_dict)
    return net


if __name__ == '__main__':
    tracemalloc.start()
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB")
    x_ = torch.rand((1, 1, 30 * 100 * 10))
    net_ = create_model()
    net_.eval()
    with torch.no_grad():
        res_ = net_(x_)
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB")
