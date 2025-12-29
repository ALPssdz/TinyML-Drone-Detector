# TinyML-Drone-Detector
An edge-AI RF spectrum sentinel powered by Renesas RA6M5. It uses 1D-CNN to distinguish non-cooperative DIY drones from Wi-Fi noise in real-time.

# Introduction (Project Overview)

TinyML-Drone-Detector (Internal Code: SkyHunter) is an intelligent edge-computing node designed for Low-Altitude Airspace Security.

Unlike traditional spectrum analyzers that only detect signal energy (RSSI), this project leverages the Renesas RA6M5 (Arm Cortex-M33) capabilities to perform Cognitive Detection. By combining real-time DSP frequency masking with a lightweight 1D-CNN (Convolutional Neural Network), it can successfully extract the unique "RF Fingerprints" of non-cooperative drones (e.g., ELRS/LoRa FPV drones) hidden within heavy Wi-Fi interference.

🚀 Key Features
Core Brain: Powered by Renesas RA6M5 @ 200MHz with Helium/DSP acceleration.

AI-Driven: Runs an Int8 quantized TinyML model (trained via Edge Impulse) entirely on-chip.

Anti-Jamming: Implements a dynamic Frequency Masking Algorithm to filter out broadband Wi-Fi noise.

Security: Utilizes Arm TrustZone® to protect alert logs and model weights in a hardware-isolated Secure World.

Performance: <10ms inference time, capable of handling 5Msps real-time sampling.

# 中文简介 (Chinese Introduction)

TinyML-Drone-Detector（中文代号：低空猎影）是一款专为低空安全防御设计的智能边缘侦测节点。

面对日益严峻的“黑飞”威胁，传统的能量侦测设备极易将合法的 Wi-Fi 信号误报为入侵目标。本项目充分利用 瑞萨 RA6M5 (Arm Cortex-M33) 的高性能算力，提出了一种**“认知侦测”**方案。通过 DSP 频域掩膜技术滤除宽带背景噪声，并结合轻量级 1D-CNN（一维卷积神经网络），实现了对隐蔽的自制无人机（如 ELRS/FPV 穿越机）射频指纹的精准捕获。

🚀 核心亮点
主控平台： 基于瑞萨 RA6M5 (200MHz)，利用 DSP 指令集加速 FFT 运算。

端侧 AI： 部署 Int8 量化的 TinyML 模型（基于 Edge Impulse 训练），实现毫秒级推理。

抗干扰算法： 独创动态频域掩膜 (Frequency Masking) 技术，完美解决“Wi-Fi 误报”痛点。

数据安全： 利用 Arm TrustZone® 构建可信执行环境（TEE），保障报警日志不可篡改。

工业级性能： 支持 5Msps 高速采样，系统响应零延迟。
