from dataclasses import dataclass


@dataclass
class EEGFilterConfig:
    """脑电滤波器配置"""
    eeg_channel_count: int  # EEG总通道数
    sample_rate: float  # 采样率
    fftWindow: int  # FFT窗长
    fl: float  # 下截止频率
    fh: float  # 上截止频率


@dataclass
class IRFilterConfig:
    """近红外滤波器配置"""
    ir_sample_rate: float  # 近红外采样率
    ir_channel: int  # 近红外通道数
    fl: float  # 下截止频率
    fh: float  # 上截止频率


@dataclass
class SignalConfig:
    """信号处理配置"""
    eeg_filter: EEGFilterConfig  # 脑电滤波器配置
    ir_filter: IRFilterConfig  # 近红外滤波器配置

    @classmethod
    def default(cls) -> 'SignalConfig':
        """创建默认配置"""
        return cls(
            eeg_filter=EEGFilterConfig(
                eeg_channel_count=2,
                sample_rate=250.0,
                fftWindow=512,
                fl=1,
                fh=45
            ),
            ir_filter=IRFilterConfig(
                ir_sample_rate=10.0,
                ir_channel=8,
                fl=0.01,
                fh=0.5
            )
        )
