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
