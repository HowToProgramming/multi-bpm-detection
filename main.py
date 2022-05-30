import matplotlib.pyplot as plt
import soundfile as sf
import numpy as np
from utils import exp_smoothing

alpha = 0.15
ms = 10
fp = 'F. Chopin  - Nocturne op. 9 no. 1 in B flat minor (Rubinstein).wav'
raw, bitrate = sf.read(fp)
blocksize = bitrate * ms / 1000
blocks = sf.blocks(fp, blocksize=int(blocksize), overlap=0)
blocks = [np.mean(np.sqrt(np.sum(block ** 2))) for block in blocks]

def plot_exp_smoothing(blocks, alpha):
    plt.figure()
    plt.title(fp)
    plt.plot(blocks, label='original_file')
    plt.plot(exp_smoothing(blocks, alpha), label=f'exp_smooth_alpha_{alpha}')

def get_exp_smoothing_residual(blocks, alpha):
    exp_blocks = np.array(exp_smoothing(blocks, alpha))
    residual = blocks - exp_blocks
    return residual

def plot_residual(blocks, alpha):
    plt.plot(get_exp_smoothing_residual(blocks, alpha))
    
def get_outliers(residuals):
    q1 = np.quantile(residuals, 0.25)
    q3 = np.quantile(residuals, 0.75)
    iqr = q3 - q1
    outliers = np.where(residuals > (q3 + 1.5 * iqr))[0]
    return outliers

def clear_array(arr):
    final_arr = []
    prev = -10
    for x in arr:
        if abs(prev - x) < 5:
            prev = x
            continue
        final_arr.append(x)
        prev = x
    return np.array(final_arr)

def find_sounds(arr, t_start):
    exp_smooth_residual = get_exp_smoothing_residual(arr, alpha)
    outliers = get_outliers(exp_smooth_residual)
    outliers = clear_array(outliers)
    return (outliers + t_start) * 10

sounds = []
for i in range(0, len(blocks), 500):
    t_start, t_finish = i, i + 500
    sound = find_sounds(blocks[t_start:t_finish], t_start)
    sounds += sound.tolist()

ms_per_beat = []
for x0, x1 in zip(sounds[:-1], sounds[1:]):
    ms_per_beat.append(x1 - x0)

# template
# 5900.583333333334,122.45833333333334,4,1,0,20,1,0
with open('timings.txt', 'w+') as f:
    for offset, ms in zip(sounds, ms_per_beat):
        f.write(f"{offset},{ms},4,1,0,20,1,0\n")
    f.close()