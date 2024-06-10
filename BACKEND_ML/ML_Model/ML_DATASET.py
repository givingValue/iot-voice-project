import torchaudio.transforms as T

#Dedicated Dataset for Tag and define data annotation information 
#It will be configured here: 
etiquetas_texto = ['female', 'male']
mapeo_etiquetas = {etiqueta: indice for indice, etiqueta in enumerate(set(etiquetas_texto))}
spectrogram = T.Spectrogram(
      n_fft=450,
      win_length=400,
      hop_length=80,
      center=True,
      pad_mode="reflect",
      power=2.0,
  )

