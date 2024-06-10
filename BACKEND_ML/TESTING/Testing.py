import time
import torch
import mlflow
import mlflow.pytorch
from captum.attr import IntegratedGradients
from captum.attr import GradientShap
from captum.attr import Occlusion
##
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
import numpy as np
from TOOLS.TOOLS import plot_spectrogram
from ML_Model.ML_DATASET import mapeo_etiquetas,etiquetas_texto

def IMAGE_PROCESSING(Image):
    #values=np.log(np.abs(np.transpose(Image.squeeze().cpu().detach().numpy())))
    #max_value = np.max(values)
    #min_value= np.min(values)
    #re_scale=(1/(max_value-min_value))*(values-min_value)
    return Image.squeeze().cpu().detach().numpy()

def EVALUATION_MODEL(model,test_loader,device,RESULT_DIR,method,method_name,args):
    SPECTOGRAM_dir=method_name
    iterator = iter(test_loader)
    model.eval()
    for i in range(6):
        input,_,label, _,_=next(iterator)
        input=input.to(device)
        with torch.no_grad():
            outputs = model(input)
            _, predicted = outputs.max(1)
        integrated_gradients = method(model)
        #args["input"]=input
        args["target"]=predicted
        attributions_ig = integrated_gradients.attribute(input,**args)
        Image=IMAGE_PROCESSING(attributions_ig)
        input=input.squeeze().cpu().detach().numpy()

        #IMAGE BLOCK
        if SPECTOGRAM_dir=="occlusion":
            color="coolwarm"
        elif SPECTOGRAM_dir=="GRADIENT":
            color="viridis"
        gender=mapeo_etiquetas[label[0]]
        fig, axs = plt.subplots(1, 2, figsize=(10, 5))
        plot_spectrogram(Image,fig,axs[0],color)
        axs[0].set_title("MODELO CAPTUM")
        axs[0].axis('off')  # Ocultar losa ejes
        # Mostrar la segunda imagen en el segundo cuadro
        plot_spectrogram(input,fig,axs[1],'viridis')
        axs[1].set_title("ESPECTROGRAMA GENERO {} ETIQUETA {}  ".format(gender,label))
        axs[1].axis('off')  # Ocultar los ejes
        # Ajustar el layout para que no haya solapamientos
        #plt.tight_layout()
        # Guardar la figura en un archivo
        image_dir=RESULT_DIR+"GRADIENT/"+SPECTOGRAM_dir+str(i)+".jpg"
        plt.savefig(image_dir)




def CAPTUM_DEFINE_GRADIENT(model,test_loader,device,RESULT_DIR):

    SPECTOGRAM_dir="SPECTROM_GRADIENT"
    iterator = iter(test_loader)
    model.eval()
    for i in range(6):
        input,_,label, _,_=next(iterator)
        input=input.to(device)
        with torch.no_grad():
            outputs = model(input)
            _, predicted = outputs.max(1)
        integrated_gradients = IntegratedGradients(model)
        attributions_ig = integrated_gradients.attribute(input, target=predicted, n_steps=50)
        Image=IMAGE_PROCESSING(attributions_ig)
        input=input.squeeze().cpu().detach().numpy()
        #IMAGE BLOCK
        gender=mapeo_etiquetas[label[0]]
        fig, axs = plt.subplots(1, 2, figsize=(10, 5))
        plot_spectrogram(Image,fig,axs[0],'coolwarm')
        axs[0].set_title("MODELO CAPTUM")
        axs[0].axis('off')  # Ocultar losa ejes
        # Mostrar la segunda imagen en el segundo cuadro
        plot_spectrogram(input,fig,axs[1],'viridis')
        axs[1].set_title("ESPECTROGRAMA GENERO {} ETIQUETA {}  ".format(gender,label))
        axs[1].axis('off')  # Ocultar los ejes
        # Ajustar el layout para que no haya solapamientos
        #plt.tight_layout()
        # Guardar la figura en un archivo
        image_dir=RESULT_DIR+"GRADIENT/"+SPECTOGRAM_dir+str(i)+".jpg"
        plt.savefig(image_dir)
       

def CAPTUM_DEFINE_OCCLUSION(model,test_loader,device,RESULT_DIR):
    SPECTOGRAM_dir="SPECTROM_OCCLUSION"
    iterator = iter(test_loader)
    model.eval()
    for i in range(6):
        input,_,label, _,_=next(iterator)
        input=input.to(device)
        with torch.no_grad():
            outputs = model(input)
            _, predicted = outputs.max(1)
        occlusion  = Occlusion(model)
        attributions_ig = occlusion.attribute(input, target=predicted, sliding_window_shapes=(1,15, 15))
        Image=IMAGE_PROCESSING(attributions_ig)
        input=input.squeeze().cpu().detach().numpy()
        #IMAGE BLOCK
        gender=mapeo_etiquetas[label[0]]
        fig, axs = plt.subplots(1, 2, figsize=(10, 5))
        plot_spectrogram(Image,fig,axs[0],'coolwarm')
        axs[0].set_title("MODELO CAPTUM")
        axs[0].axis('off')  # Ocultar losa ejes
        # Mostrar la segunda imagen en el segundo cuadro
        plot_spectrogram(input,fig,axs[1],'viridis')
        axs[1].set_title("ESPECTROGRAMA GENERO {} ETIQUETA {}  ".format(gender,label))
        axs[1].axis('off')  # Ocultar los ejes
        # Ajustar el layout para que no haya solapamientos
        #plt.tight_layout()
        # Guardar la figura en un archivo
        image_dir=RESULT_DIR+"OCCLUSION/"+SPECTOGRAM_dir+str(i)+".jpg"
        plt.savefig(image_dir)

def config_captum(name):
    if name=="occlusion":
        args={"target":"","sliding_window_shapes":(1,15,15)}
    elif name =="GRADIENT":
        args={"target":"","n_steps":50}
    return args

    
def Testing(model,test_loader,device,RESULT_DIR):
    test_correct = 0
    test_total = 0
    predicted_labels = []
    true_labels = []
    init = time.time()
    model.eval()  # Establecer el modelo en modo de evaluación
    with torch.no_grad():
        for inputs,_,labels, _,_  in test_loader:
            outputs = model(inputs.to(device))
            #class_id = outputs.squeeze(0).softmax(0).argmax().item()
            _, predicted = outputs.max(1)
            labels = [mapeo_etiquetas[etiqueta] for etiqueta in labels]
            labels=torch.tensor(labels).to(device)
            test_total += labels.size(0)
            test_correct += predicted.eq(labels).sum().item()
            predicted_labels.extend(predicted.tolist())
            true_labels.extend(labels.tolist())
    test_accuracy = test_correct / test_total
    print(f'Test Accuracy: {100 * test_accuracy:.2f}%')
    mlflow.log_metric('accuracy', test_accuracy)
    end = time.time()
    print("The training took {}".format(end-init))
    conf_matrix = confusion_matrix(true_labels, predicted_labels)
    sns.heatmap(conf_matrix, annot=True,xticklabels=etiquetas_texto,yticklabels=etiquetas_texto, fmt='d', cmap='Blues')
    plt.savefig(RESULT_DIR+"/HEATMAP.jpg")
    return model

def run_experiment_Test(model,test_loader,device,RUNNAME,RESULT_DIR,EXPERIMENT):
    mlflow.set_tracking_uri(uri="http://127.0.0.1:8080")
    # Create a new MLflow Experiment
    mlflow.set_experiment(EXPERIMENT)
    with mlflow.start_run():
        # Crear y entrenar el modelo
        mlflow.set_tag("mlflow.runName", RUNNAME)
        model = Testing(model,test_loader,device,RESULT_DIR)
        # Registrar los hiperparámetros y métricas en MLflow
        mlflow.log_params({'epochs': 100, 'lr': 0.001})
        mlflow.log_artifact(RESULT_DIR, artifact_path="images")
        # Interpretación de modelo con CAPTUM (escogemos 5 imagenes y las guardamos)
        # Aplicamos Dos Algoritmos para poder diferenciar
        # CAPTUM_DEFINE_GRADIENT(model,test_loader,device,RESULT_DIR)
        # CAPTUM_DEFINE_OCCLUSION(model,test_loader,device,RESULT_DIR)
        
        # METODOS ACTUALIZADO PARA MEJORAR EL CÓDIGO Y LOS MÉTODOS
        EVALUATION_MODEL(model,test_loader,device,RESULT_DIR,IntegratedGradients,"GRADIENT",config_captum("GRADIENT"))
        EVALUATION_MODEL(model,test_loader,device,RESULT_DIR,Occlusion,"occlusion",config_captum("occlusion"))
        # Guardar el modelo entrenado
        mlflow.log_artifact(RESULT_DIR, artifact_path="images")
        mlflow.pytorch.log_model(model, 'model')
