from torchaudio.utils import download_asset
import random

def rir_transform(signal,rir_signal):
  #Aplicamos la convolución, metodo basado Eco

  rir_raw, sample_rate=torchaudio.load("ECO.wav")
  rir = rir_raw[:, int(48000 * 1.01) : int(48000 * 1.3)]
  rir = rir / torch.linalg.vector_norm(rir, ord=2)
  return F.fftconvolve(signal, rir_signal,mode="same")

def add_noise(signal):
  # snr_dbs es un parametro que hace la escala de relación a ruido de la señal que generamos
  noise_signal=torchaudio.load("NOISE.wav")
  return F.add_noise(signal, noise_signal, torch.tensor([10]))

class RandomApplyTransform(object):
    def __init__(self, transform, probability=0.5):
        self.transform = transform
        self.probability = probability

    def __call__(self, signal):
        if random.random() < self.probability:
            return self.transform(signal)
        return signal
