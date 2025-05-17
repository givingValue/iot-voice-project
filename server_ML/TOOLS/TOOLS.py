import librosa

def plot_spectrogram(spec,fig,axs,cmap, title=None, ylabel='freq_bin', xmax=None):
  
  axs.set_title(title or 'Spectrogram (db)')
  axs.set_ylabel(ylabel)
  axs.set_xlabel('frame')
  img = librosa.display.specshow(librosa.power_to_db(spec),cmap=cmap, x_axis='time', y_axis='mel', ax=axs)
  if xmax:
    axs.set_xlim((0, xmax))
  fig.colorbar(img, ax=axs)