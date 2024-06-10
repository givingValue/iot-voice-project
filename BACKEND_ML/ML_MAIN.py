import fire
from ML_Model.ML_MODEL import SPECTROGRAM_MODEL
from DATASET.DATA_SPLIT import DATA_INIT,read_tag_json
from DATASET.DATA_AUGMENTATION import *
from DATASET.DATALOADER import Compose,AudioDataset,CustomBatchSampler
from TRAINING.Training import run_experiment
from TESTING.Testing import run_experiment_Test
import torch
from torchvision import transforms as T_image
from torch.utils.data import DataLoader
from ML_Model.ML_DATASET import spectrogram

transforms = Compose([
    spectrogram,
    T_image.Resize((224,224))
])

def select_device(CONF):
    if CONF["DEVICE"]== "cuda" and torch.cuda.is_available():
        device = torch.device("cuda")
    elif CONF["DEVICE"]== "cpu":
        device = torch.device("cpu")
    else :
        assert(False,"No se indico el dispositivo correctamente")
    return device

def ML_TRAINING(TUNNING,MODEL_DIR,STEP,RUNNAME,TRAINING_DATASET,EXPERIMENT,CONF):

    time_length=48000
    Train=AudioDataset(TRAINING_DATASET,time_length,transform=transforms)
    Sampler=CustomBatchSampler(32,Train)
    Train_dataset=DataLoader(Train, batch_sampler=Sampler)
    device=select_device(CONF)
    if TUNNING=="TUNING":
        model=torch.load(MODEL_DIR+".pt",map_location=device)
        MODEL_DIR+="_"+str(STEP)+".pt"
    else :
        model=SPECTROGRAM_MODEL(CONF["NUMBER OF CLASS"])
        torch.save(model.state_dict(), MODEL_DIR+".pth")
    if torch.cuda.is_available() and CONF["DEVICE"]=="cuda":
        model = model.to('cuda')
    print(device)
    run_experiment(model,Train_dataset,device,MODEL_DIR,RUNNAME,EXPERIMENT)

def ML_TESTING(MODEL_DIR,RUNNAME,STEP,TESTING_DATASET,RESULT_DIR,EXPERIMENT,CONF):
    data_dir=TESTING_DATASET
    time_length=48000
    Test=AudioDataset(data_dir,time_length,transform=transforms)
    TESTING_DATASET=DataLoader(Test,shuffle=False, batch_size=1)
    device=select_device(CONF)
    model=torch.load(MODEL_DIR+str(STEP)+".pt",map_location=device)
    run_experiment_Test(model,TESTING_DATASET,device,RUNNAME,RESULT_DIR,EXPERIMENT)

def DATASET_PROCESS(TRAINING_DATASET,TESTING_DATASET,DATASET_DIR,TAG_FILE,CONF):
    DATA_INIT(TRAINING_DATASET,TESTING_DATASET,DATASET_DIR,TAG_FILE,CONF)

function_list={"TRAINING":ML_TRAINING,"TESTING":ML_TESTING,"DATASET_PROCESS":DATASET_PROCESS}

def ML_function(MODE,TUNNING=None,MODEL_DIR=None,STEP="", RUNNAME=None,TRAINING_DATASET="",TESTING_DATASET="",RESULT_DIR="",DATASET_DIR="",EXPERIMENT="", TAG_FILE=""):
    # Main function definig the experiment Step for Data Pipeline
    CONF=read_tag_json("EXPERIMENT_JSON.json")
    f=function_list[MODE]
    if MODE in ["TRAINING"]  :
        f(TUNNING,MODEL_DIR,STEP,RUNNAME,TRAINING_DATASET,EXPERIMENT,CONF)
    elif MODE in ["TESTING"]:
        f(MODEL_DIR,RUNNAME,STEP,TESTING_DATASET,RESULT_DIR,EXPERIMENT,CONF)
    elif  MODE in ["DATASET_PROCESS"] :
        f(TRAINING_DATASET,TESTING_DATASET,DATASET_DIR,TAG_FILE,CONF)

if __name__ == '__main__':
    fire.Fire(ML_function)
    

