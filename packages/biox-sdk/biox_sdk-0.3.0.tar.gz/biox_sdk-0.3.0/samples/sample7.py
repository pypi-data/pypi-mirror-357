import asyncio
import time
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import pyqtgraph as pg
import collections
import threading
from bleak import BleakGATTCharacteristic
from pyqtgraph.Qt import QtWidgets, QtCore
from biox.ble.scanner import BluetoothScanner
from biox.collector.collector import Collector
from biox.data.decode import parse_packet
from biox.data.process import Processing
from biox.data.signal_config import SignalConfig

# 全局配置
PLOT_DURATION = 20  # 显示的时间长度（秒）
SAMPLING_RATE = 250  # 采样率（Hz）
BUFFER_SIZE = int(PLOT_DURATION * SAMPLING_RATE)  # 每个通道的缓冲区大小
NUM_CHANNELS = 2

# 创建Qt应用
app = QtWidgets.QApplication.instance()
if app is None:
    app = QtWidgets.QApplication(sys.argv)

# 创建主窗口
win = QtWidgets.QMainWindow()
win.setWindowTitle('Real-time EEG Visualization')
win.resize(1000, 800)

# 创建滚动区域
scroll_area = QtWidgets.QScrollArea()
scroll_area.setWidgetResizable(True)
win.setCentralWidget(scroll_area)

# 创建中央部件和布局
central_widget = QtWidgets.QWidget()
scroll_area.setWidget(central_widget)
layout = QtWidgets.QVBoxLayout(central_widget)

# 创建每个通道的绘图部件
plot_widgets = []
curves = []
data_buffers = []

# 固定时间轴（从0到PLOT_DURATION）
time_axis = np.linspace(0, PLOT_DURATION, BUFFER_SIZE)

# 创建每个通道的绘图区域
for i in range(NUM_CHANNELS):
    # 创建分组框
    group_box = QtWidgets.QGroupBox(f"Channel {i + 1}")
    group_layout = QtWidgets.QVBoxLayout()
    group_box.setLayout(group_layout)
    layout.addWidget(group_box)

    # 创建绘图部件
    plot_widget = pg.PlotWidget()
    plot_widget.setLabel('bottom', 'Time', 's')
    plot_widget.setLabel('left', 'Amplitude')
    plot_widget.showGrid(x=True, y=True)
    plot_widget.setXRange(0, PLOT_DURATION)  # 固定X轴范围

    # 创建曲线，使用connect='finite'避免断帧
    curve = plot_widget.plot(
        [], [],  # 初始化为空数组
        pen=pg.mkPen(color=(0, 100 + i * 20, 255 - i * 20), width=1),
        connect='finite'  # 确保曲线连续
    )

    group_layout.addWidget(plot_widget)

    # 存储引用
    plot_widgets.append(plot_widget)
    curves.append(curve)

    # 初始化数据缓冲区（固定长度）
    buffer = collections.deque([0.0] * BUFFER_SIZE, maxlen=BUFFER_SIZE)
    data_buffers.append(buffer)

# 添加间隔
layout.addStretch(1)


# 更新函数
def update_plot():
    for i in range(NUM_CHANNELS):
        # 将缓冲区转换为numpy数组
        # print(f"{i} data:{data_buffers[i]}")
        y_data = np.array(data_buffers[i])

        # 更新曲线数据（使用完整的固定时间轴）
        curves[i].setData(time_axis, y_data)


# 创建定时器
timer = QtCore.QTimer()
timer.timeout.connect(update_plot)
timer.start(50)  # 每50ms更新一次

# 显示窗口
win.show()


async def main():
    ble_device = None
    while ble_device is None:
        devices = await BluetoothScanner.scan()
        for device in devices:
            if device and device.device.name and "Biox" in device.device.name:
                ble_device = device
                break

    signal_config = SignalConfig.default()
    processtor = Processing(signal_config)

    collector = Collector(ble_device)

    # 数据处理回调
    def notification_handler(characteristic: BleakGATTCharacteristic, data: bytearray):
        start_time = time.time()  # 监控处理时间

        parsed = parse_packet(data)
        if parsed and parsed.pkg_type == 1:
            # 处理EEG数据（二维数组）

            result = processtor.process_eeg_data(2, parsed.brain_elec)
            print(f"result:{result}")

            # 将结果添加到缓冲区
            for ch_idx, channel_data in enumerate(result):
                if ch_idx < len(data_buffers):
                    # 添加每个数据点（自动移除旧数据）
                    for value in channel_data:
                        data_buffers[ch_idx].append(value)

            # print(f"data_buffers:{len(data_buffers[ch_idx])}")

            # 打印处理耗时
            proc_time = (time.time() - start_time) * 1000
            if proc_time > 10:  # 警告超过10ms
                print(f"Warning: Processing took {proc_time:.2f}ms")

    await collector.register_notify(callback=notification_handler)
    await collector.start()
    await collector.stop_data_collection()
    await collector.start_data_collection()

    # 在异步循环中处理Qt事件
    while True:
        await asyncio.sleep(0.05)  # 短暂休眠，让出控制权
        app.processEvents()  # 处理Qt事件，保持界面响应


if __name__ == '__main__':
    # 在单独的线程中运行异步主函数
    async_thread = threading.Thread(target=lambda: asyncio.run(main()), daemon=True)
    async_thread.start()

    # 启动Qt主循环
    app.exec()
