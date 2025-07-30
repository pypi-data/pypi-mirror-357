import numpy as np
import sounddevice as sd
import soundfile as sf
import threading

class AudioListener:
    def __init__(self, position, listen_radius=10.0):
        self.position = np.array(position, dtype=float)
        self.listen_radius = listen_radius

class AudioSource:
    def __init__(self, position, sound_path, emit_radius=15.0):
        self.position = np.array(position, dtype=float)
        self.sound_path = sound_path
        self.emit_radius = emit_radius
        self.volume = 1.0
        self.loop = False
        self.playing = False
        self._thread = None
        self._stop_flag = False

    def _play_thread(self, volume):
        while not self._stop_flag:
            data, fs = sf.read(self.sound_path, dtype='float32')
            data *= volume  # tłumienie
            sd.play(data, fs)
            sd.wait()
            if not self.loop:
                break

    def play(self, distance):
        if self.playing:
            return
        attenuation = max(0.0, 1.0 - distance / (self.emit_radius + 0.001))
        volume = self.volume * attenuation
        self._stop_flag = False
        self._thread = threading.Thread(target=self._play_thread, args=(volume,))
        self._thread.start()
        self.playing = True

    def stop(self):
        if self.playing:
            self._stop_flag = True
            if self._thread:
                self._thread.join()
            sd.stop()
            self.playing = False


def update_audio_system(listener: AudioListener, sources: list, debug=False):
    for source in sources:
        dist = np.linalg.norm(listener.position - source.position)
        if dist <= (listener.listen_radius + source.emit_radius):
            if not source.playing:
                if debug:
                    print(f"[PLAY] {source.sound_path}")
                source.play(dist)
        else:
            if source.playing:
                if debug:
                    print(f"[STOP] {source.sound_path}")
                source.stop()
