//! 音效：用 rodio 生成正弦波提示音。

use std::sync::OnceLock;
use std::time::Duration;

use rodio::{source::SineWave, DeviceSinkBuilder, MixerDeviceSink, Source};

static SINK: OnceLock<Option<MixerDeviceSink>> = OnceLock::new();

fn sink() -> Option<&'static MixerDeviceSink> {
    SINK
        .get_or_init(|| DeviceSinkBuilder::open_default_sink().ok())
        .as_ref()
}

/// 启动时预初始化音频设备，避免首次播放时的卡顿。
pub fn init() {
    let _ = sink();
}

fn play_tone(freq: f32, duration: Duration) {
    if let Some(sink) = sink() {
        let source = SineWave::new(freq).take_duration(duration).amplify(0.2);
        sink.mixer().add(source);
    }
}

pub fn play_reveal() {
    play_tone(880.0, Duration::from_millis(40));
}

pub fn play_flag() {
    play_tone(660.0, Duration::from_millis(60));
}

pub fn play_explosion() {
    play_tone(200.0, Duration::from_millis(220));
}

pub fn play_win() {
    play_tone(1047.0, Duration::from_millis(300));
}
