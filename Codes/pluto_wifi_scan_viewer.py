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

# ===== 新增：瀑布图缓存 =====
waterfall_cache = [None] * len(channels)

current_idx = 0

# =========================
# 图形界面布局
# =========================
plt.rcParams["font.size"] = 9
fig = plt.figure(figsize=(16, 9))

ax_bar = plt.subplot2grid((3, 4), (0, 0), colspan=4)
ax_wf  = plt.subplot2grid((3, 4), (1, 0), colspan=3, rowspan=2)
ax_fft = plt.subplot2grid((3, 4), (1, 3), rowspan=2)

# ===== 按钮 =====
ax_scan = plt.axes([0.05, 0.02, 0.15, 0.05])
ax_prev = plt.axes([0.25, 0.02, 0.15, 0.05])
ax_next = plt.axes([0.45, 0.02, 0.15, 0.05])

btn_scan = Button(ax_scan, "Scan")
btn_prev = Button(ax_prev, "Channel ↓")
btn_next = Button(ax_next, "Channel ↑")

# =========================
# 功能函数
# =========================
def capture_waterfall(freq):
    sdr.rx_lo = int(freq)
    time.sleep(0.1)

    wf = []
    for _ in range(WATERFALL_FRAMES):
        samples = sdr.rx()
        samples *= np.hanning(len(samples))
        spectrum = np.fft.fftshift(np.fft.fft(samples, FFT_SIZE))
        power = 20 * np.log10(np.abs(spectrum) + 1e-12)
        wf.append(power)

    return np.array(wf)

def display_channel(idx):
    waterfall = waterfall_cache[idx]
    if waterfall is None:
        ax_wf.clear()
        ax_wf.set_title("No data – please press Scan")
        fig.canvas.draw_idle()
        return

    ch, freq = channels[idx]

    freqs = np.linspace(
        freq - SAMPLE_RATE / 2,
        freq + SAMPLE_RATE / 2,
        FFT_SIZE
    ) / 1e6

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

def update_bar():
    ax_bar.clear()
    ax_bar.bar(channel_numbers, channel_powers)
    ax_bar.set_title("2.4 GHz Wi-Fi Channel Energy Overview")
    ax_bar.set_xlabel("Channel")
    ax_bar.set_ylabel("Avg Power (dB)")
    ax_bar.grid(True, axis="y")

# =========================
# 按钮回调
# =========================
def scan_all(event):
    print("Scanning all channels...")
    for i, (_, freq) in enumerate(channels):
        wf = capture_waterfall(freq)
        waterfall_cache[i] = wf
        channel_powers[i] = np.mean(wf)

    update_bar()
    display_channel(current_idx)

def next_channel(event):
    global current_idx
    current_idx = (current_idx + 1) % len(channels)
    display_channel(current_idx)

def prev_channel(event):
    global current_idx
    current_idx = (current_idx - 1) % len(channels)
    display_channel(current_idx)

btn_scan.on_clicked(scan_all)
btn_next.on_clicked(next_channel)
btn_prev.on_clicked(prev_channel)

# =========================
# 初始显示
# =========================
update_bar()
display_channel(current_idx)
plt.show()
