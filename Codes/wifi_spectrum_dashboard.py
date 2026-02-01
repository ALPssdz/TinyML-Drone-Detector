import adi
import numpy as np
import matplotlib.pyplot as plt
import time

# =========================
# Pluto SDR 初始化
# =========================
sdr = adi.Pluto("ip:192.168.1.10")

SAMPLE_RATE = int(30e6)
RX_BW       = int(20e6)
FFT_SIZE    = 1024
WATERFALL_FRAMES = 120

sdr.sample_rate = SAMPLE_RATE
sdr.rx_rf_bandwidth = RX_BW
sdr.rx_buffer_size = FFT_SIZE

# 手动增益，避免 AGC 压平 Wi-Fi
sdr.gain_control_mode = "manual"
sdr.rx_hardwaregain_chan0 = 55

# =========================
# Wi-Fi 信道表
# =========================
channels = {
    1: 2.412e9,  2: 2.417e9,  3: 2.422e9,
    4: 2.427e9,  5: 2.432e9,  6: 2.437e9,
    7: 2.442e9,  8: 2.447e9,  9: 2.452e9,
    10: 2.457e9, 11: 2.462e9,
    12: 2.467e9, 13: 2.472e9
}

channel_numbers = list(channels.keys())
channel_powers = np.zeros(len(channel_numbers))

# =========================
# 图形界面布局（方案二）
# =========================
plt.rcParams["font.size"] = 9

fig = plt.figure(figsize=(16, 9))

# 上：全信道能量柱状图
ax_bar = plt.subplot2grid((3, 4), (0, 0), colspan=4)

# 左下：瀑布图
ax_wf = plt.subplot2grid((3, 4), (1, 0), colspan=3, rowspan=2)

# 右下：瞬时频谱
ax_fft = plt.subplot2grid((3, 4), (1, 3), rowspan=2)

# =========================
# 主扫描循环
# =========================
for idx, (ch, freq) in enumerate(channels.items()):
    print(f"Scanning CH{ch} @ {freq/1e9:.3f} GHz")

    sdr.rx_lo = int(freq)
    time.sleep(0.1)   # 模拟前端稳定

    waterfall = []

    for _ in range(WATERFALL_FRAMES):
        samples = sdr.rx()
        windowed = samples * np.hanning(len(samples))
        spectrum = np.fft.fftshift(np.fft.fft(windowed, FFT_SIZE))
        power = 20 * np.log10(np.abs(spectrum) + 1e-12)
        waterfall.append(power)

    waterfall = np.array(waterfall)

    # 计算该信道的平均能量（用于柱状图）
    channel_powers[idx] = np.mean(waterfall)

    # 频率轴
    freqs = np.linspace(
        freq - SAMPLE_RATE / 2,
        freq + SAMPLE_RATE / 2,
        FFT_SIZE
    ) / 1e6

    # =========================
    # 更新：全信道柱状图
    # =========================
    ax_bar.clear()
    ax_bar.bar(channel_numbers, channel_powers)
    ax_bar.set_title("2.4 GHz Wi-Fi Channel Energy Overview")
    ax_bar.set_xlabel("Channel")
    ax_bar.set_ylabel("Average Power (dB)")
    ax_bar.set_ylim(np.min(channel_powers) - 5,
                    np.max(channel_powers) + 5)
    ax_bar.grid(True, axis="y")

    # =========================
    # 更新：瀑布图
    # =========================
    ax_wf.clear()
    vmin = np.percentile(waterfall, 10)
    vmax = np.percentile(waterfall, 99)

    ax_wf.imshow(
        waterfall,
        aspect="auto",
        origin="lower",
        extent=[freqs[0], freqs[-1], 0, WATERFALL_FRAMES],
        vmin=vmin,
        vmax=vmax
    )
    ax_wf.set_title(f"Waterfall – Wi-Fi CH{ch}")
    ax_wf.set_xlabel("Frequency (MHz)")
    ax_wf.set_ylabel("Time")

    # =========================
    # 更新：瞬时频谱
    # =========================
    ax_fft.clear()
    ax_fft.plot(freqs, waterfall[-1])
    ax_fft.set_title("Instantaneous Spectrum")
    ax_fft.set_xlabel("Frequency (MHz)")
    ax_fft.set_ylabel("Power (dB)")
    ax_fft.grid(True)

    plt.tight_layout()
    plt.pause(0.01)

plt.show()
