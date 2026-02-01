import adi
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
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

sdr.gain_control_mode = "manual"
sdr.rx_hardwaregain_chan0 = 55

# =========================
# Wi-Fi 信道表
# =========================
channels = [
    (1, 2.412e9), (2, 2.417e9), (3, 2.422e9),
    (4, 2.427e9), (5, 2.432e9), (6, 2.437e9),
    (7, 2.442e9), (8, 2.447e9), (9, 2.452e9),
    (10, 2.457e9), (11, 2.462e9),
    (12, 2.467e9), (13, 2.472e9)
]

channel_numbers = [ch for ch, _ in channels]
channel_powers = np.zeros(len(channels))

current_idx = 0   # 当前信道索引

# =========================
# 图形界面布局
# =========================
plt.rcParams["font.size"] = 9
fig = plt.figure(figsize=(16, 9))

ax_bar = plt.subplot2grid((3, 4), (0, 0), colspan=4)
ax_wf  = plt.subplot2grid((3, 4), (1, 0), colspan=3, rowspan=2)
ax_fft = plt.subplot2grid((3, 4), (1, 3), rowspan=2)

# 按钮区域
ax_btn = plt.axes([0.82, 0.02, 0.15, 0.05])
btn_next = Button(ax_btn, "Next Channel")

# =========================
# 核心：更新当前信道显示
# =========================
def update_channel(idx):
    ch, freq = channels[idx]
    print(f"Display CH{ch}")

    sdr.rx_lo = int(freq)
    time.sleep(0.1)

    waterfall = []

    for _ in range(WATERFALL_FRAMES):
        samples = sdr.rx()
        samples *= np.hanning(len(samples))
        spectrum = np.fft.fftshift(np.fft.fft(samples, FFT_SIZE))
        power = 20 * np.log10(np.abs(spectrum) + 1e-12)
        waterfall.append(power)

    waterfall = np.array(waterfall)

    # 更新柱状图能量
    channel_powers[idx] = np.mean(waterfall)

    freqs = np.linspace(
        freq - SAMPLE_RATE / 2,
        freq + SAMPLE_RATE / 2,
        FFT_SIZE
    ) / 1e6

    # ===== 柱状图 =====
    ax_bar.clear()
    ax_bar.bar(channel_numbers, channel_powers)
    ax_bar.set_title("2.4 GHz Wi-Fi Channel Energy Overview")
    ax_bar.set_xlabel("Channel")
    ax_bar.set_ylabel("Avg Power (dB)")
    ax_bar.grid(True, axis="y")

    # ===== 瀑布图 =====
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

    # ===== 瞬时频谱 =====
    ax_fft.clear()
    ax_fft.plot(freqs, waterfall[-1])
    ax_fft.set_title("Instantaneous Spectrum")
    ax_fft.set_xlabel("Frequency (MHz)")
    ax_fft.set_ylabel("Power (dB)")
    ax_fft.grid(True)

    fig.canvas.draw_idle()

# =========================
# 按钮回调函数
# =========================
def next_channel(event):
    global current_idx
    current_idx = (current_idx + 1) % len(channels)
    update_channel(current_idx)

btn_next.on_clicked(next_channel)

# =========================
# 初始显示
# =========================
update_channel(current_idx)
plt.show()
