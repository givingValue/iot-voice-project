
from torch.utils.data import Dataset
import torch
import torchaudio
import torchaudio.functional as F
import torchaudio.transforms as T
from scipy.io.wavfile import write
import numpy as np
import json
import random
import os


class Compose(object):
    def __init__(self, transforms):
        self.transforms = transforms

    def __call__(self, waveform):
        for transform in self.transforms:
            waveform = transform(waveform)
        return waveform
    

class AudioDataset(Dataset):
    def __init__(self, data_dir,time_length,tag_file=None, transform=None):
        with open(data_dir, 'r') as archivo:
          datos_json = json.load(archivo)
        self.tag_file=datos_json
        self.file_paths = datos_json
        self.transform = transform
        self.time_length=time_length
        self.list_counting_directories={}
        self.sample_rate = 48000

    def _get_file_paths(self, directory):
        file_paths = []
        for root, _, files in os.walk(directory):
          for tag in self.tag_file.keys():
            if root.endswith(tag):
              for file in files:
                  if file.endswith(('.wav', '.mp3')):
                      file_paths.append({"file":os.path.join(root, file),"tag":self.tag_file[tag]["gender"],"person":tag})
        return file_paths

    def __len__(self):
        return len(self.file_paths)

    def __getitem__(self, idx):
       
      if isinstance(idx, int):
        return self.Selector(idx) 
      else:

        Waveform_spectrograms=[]
        Tag_list=[]
        for i in idx:
            a,_,c,_,_=self.Selector(i)
            Waveform_spectrograms.append(a)
            Tag_list.append(c)
        Waveform_spectrograms=torch.stack(Waveform_spectrograms)
        #Waveform_spectrograms=torch.Tensor(Waveform_spectrograms)
        print(Waveform_spectrograms.size())
        return Waveform_spectrograms,_,Tag_list,_,_


    def Selector(self,id):
        file_path = self.file_paths[id]
        waveform, sample_rate = torchaudio.load(file_path["file"])
        Resampling = T.Resample(sample_rate,  self.sample_rate)
        waveform=Resampling(waveform)
        if waveform.shape[1] < self.time_length:
            waveform = np.pad(waveform, ((0, 0), (0, self.time_length - waveform.shape[1])), mode='constant')
            waveform=torch.tensor(waveform, dtype=torch.float)
        elif waveform.shape[1] > self.time_length:
            waveform = waveform[:, :self.time_length]
        return self.transform(waveform),waveform,file_path["tag"],sample_rate,file_path["file"]
    #Metodo que aplicamos para copiar la rutas del dataset de lectura
       
    
    def copy(self):
      return AudioDataset(self.file_paths, self.tag_file)
    def save_sound(self,file_path,sound):
    #Método para salvar los nuevos archivos generados del dataset despues de una determinada transformación
      init_name="new_data_"
      directory_name, file_name = os.path.split(file_path)
      if directory_name not in self.list_counting_directories.keys():
        self.list_counting_directories[directory_name]=1
      else :
        self.list_counting_directories[directory_name]+=1
      index_sound=str(self.list_counting_directories[directory_name])
      file=init_name+index_sound+".wav"
      saved_file=os.path.join(directory_name, file)
      torchaudio.save(saved_file,sound,self.sample_rate)


class CustomBatchSampler():
    def __init__(self, batch_size,dataset):
        self.batch_size = batch_size
        self.dataset_file=dataset.tag_file  
        self.list_tags=list(set([ i["person"] for i in dataset.tag_file ]))
        

    def __iter__(self):
        # Itera hasta que se hayan seleccionado todos los elementos
        indice_locales=self.dataset_file.copy()
        etiquetas_locales=self.list_tags.copy()
        while len(indice_locales)>0 :
          indices_seleccionados=self.selection(indice_locales,etiquetas_locales)
          for index in sorted(indices_seleccionados, reverse=True):
            del indice_locales[index]
          yield indices_seleccionados
    def selection(self,indice_locales,etiquetas_locales):
        tag_values=etiquetas_locales.copy()
        for i in range(len(tag_values)):
          list_values=[ y for x,y in zip(indice_locales,range(len(indice_locales))) if x["person"]==tag_values[i] ]
          if len(list_values)==0:
            etiquetas_locales.remove(tag_values[i])
        if len(etiquetas_locales)>self.batch_size :
          elemento_seleccionado = random.sample(etiquetas_locales,  self.batch_size)
        else :
          elemento_seleccionado = etiquetas_locales

        indices_seleccionados=[]
        for i in range(len(elemento_seleccionado)):
          #Subconjunto
          list_values=[ y for x,y in zip(indice_locales,range(len(indice_locales))) if x["person"]==elemento_seleccionado[i] ]
          #print(len(list_values))
          n=random.choice(list_values)
          indices_seleccionados.append(n)
        return indices_seleccionados

    def __len__(self):
        # Calcula el número total de lotes
        return len(self.indices) // self.batch_size
