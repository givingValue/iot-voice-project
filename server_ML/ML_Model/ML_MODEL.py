import torch.nn as nn
from torchvision.models import mobilenet_v2
import torch.optim as optim
import torch.nn.functional as F_neuronal

class SPECTROGRAM_MODEL(nn.Module):
    def __init__(self, num_classes):
        super(SPECTROGRAM_MODEL, self).__init__()
        self.mobilenet = mobilenet_v2(pretrained=True)  # Cargar MobileNetV2 preentrenado
        self.mobilenet.features[0][0] = nn.Conv2d(1, 32, kernel_size=(3, 3), stride=(2, 2), padding=(1, 1), bias=False)  # Cambiar el número de canales de entrada a 1
        self.mobilenet.classifier[1] = nn.Linear(1280, num_classes)  # Cambiar la capa de clasificación

    def forward(self, x):
        return self.mobilenet(x)
    
class HIPERPARAMETERS():
    def __init__(self):
        self.Loss_function=nn.CrossEntropyLoss
        self.Optimizador=optim.Adam
        self.num_epochs=10

class Spectrogram_AST(nn.Module):
    def __init__(self):
        super(Spectrogram_AST, self).__init__()
        self.Deit = torch.hub.load('facebookresearch/deit:main', 'deit_base_patch16_224', pretrained=True)
        self.T_1=nn.Linear(1000, 48)
        self.T_2=nn.Linear(48, 2)
    def Split_image(self,image,size):
      blocks = image.unfold(2, 16, 16).unfold(3, size, size)
      blocks_T = blocks.contiguous().view( -1,image.size(0), size, size)
      return blocks_T

    def forward(self, x):

        if x.shape[1] == 1:  # Verificar si la imagen tiene un solo canal
            x = x.repeat(1, 3, 1, 1)  # Repetir el canal para obtener 3 canales
        x=self.Deit(x)
        x=self.T_1(x)
        print("1 Test_".format(x.size))
        x=torch.flatten(x,start_dim=1)
        print("2 Test_".format(x.size))
        x=self.T_2(x)
        return x