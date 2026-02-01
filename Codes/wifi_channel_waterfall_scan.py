import adi
import numpy as np
import matplotlib.pyplot as plt
import time

# ======================
# Pluto SDR 初始化
# ======================
sdr = adi.Pluto("ip:192.168.1.10")

sample_rate = int(30e6)      # 30 MSPS
rx_bw       = int(20e6)      # 20 MHz
fft_size    = 1024
frames      = 120            # 每个信道的时间深度

sdr.sample_rate = sample_rate
sdr.rx_rf_bandwidth = rx_bw
sdr.rx_buffer_size = fft_size

# 手动增益（非常重要）
sdr.gain_control_mode = "manual"
sdr.rx_hardwaregain_chan0 = 55

# ======================
# Wi-Fi 信道表
# ======================
channels = {
    1: 2.412e9,  2: 2.417e9,  3: 2.422e9,
    4: 2.427e9,  5: 2.432e9,  6: 2.437e9,
    7: 2.442e9,  8: 2.447e9,  9: 2.452e9,
    10: 2.457e9, 11: 2.462e9,
    12: 2.467e9, 13: 2.472e9
}

# ======================
# 创建画布
# ======================
fig, axes = plt.subplots(4, 4, figsize=(16, 12))
axes = axes.flatten()

# ======================
# 主扫描循环
# ======================
for idx, (ch, freq) in enumerate(channels.items()):
    print(f"Scanning Wi-Fi Channel {ch} @ {freq/1e9:.3f} GHz")

    sdr.rx_lo = int(freq)
    time.sleep(0.1)   # 给模拟前端稳定时间

    waterfall = []

    for _ in range(frames):
        samples = sdr.rx()
        windowed = samples * np.hanning(len(samples))
        spectrum = np.fft.fftshift(np.fft.fft(windowed, fft_size))
        power = 20 * np.log10(np.abs(spectrum) + 1e-12)
        waterfall.append(power)

    waterfall = np.array(waterfall)

    # 频率轴
    freqs = np.linspace(
        freq - sample_rate/2,
        freq + sample_rate/2,
        fft_size
    ) / 1e6

    ax = axes[idx]
    vmin = np.percentile(waterfall, 10)
    vmax = np.percentile(waterfall, 99)

    ax.imshow(
        waterfall,
        aspect="auto",
        origin="lower",
        extent=[freqs[0], freqs[-1], 0, frames],
        vmin=vmin,
        vmax=vmax
    )

    ax.set_title(f"CH {ch}")
    ax.set_xlabel("MHz")
    ax.set_ylabel("Time")

# 多余子图关闭
for i in range(len(channels), len(axes)):
    axes[i].axis("off")

plt.tight_layout()
plt.show()
