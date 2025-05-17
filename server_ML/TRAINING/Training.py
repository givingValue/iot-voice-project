import time
import torch
import torch.nn as nn
import torch.optim as optim
import mlflow
import mlflow.pytorch
from ML_Model.ML_MODEL import HIPERPARAMETERS
from ML_Model.ML_DATASET import mapeo_etiquetas


def Training(model,train_loader,device,Model_dir):
    num_epochs = 10
    init = time.time()
    criterion = HIPERPARAMETERS.Loss_function
    optimizer = HIPERPARAMETERS.Optimizador(model.parameters(), lr=0.001)
    for epoch in range(num_epochs):
        model.train()  # Establecer el modelo en modo de entrenamiento
        running_loss = 0.0
        correct = 0
        total = 0
        for inputs,_,labels, _ ,_ in train_loader:
            #inputs = torch.squeeze(inputs)  # Añadir dimensión de canal para la convolución
            outputs = model(inputs.to(device))
            labels = [mapeo_etiquetas[i] for i in labels]
            labels=torch.tensor(labels).to(device)
            loss = criterion(outputs, labels)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
        train_accuracy = correct / total
        mlflow.log_metric('accuracy', train_accuracy, step=epoch)
    end = time.time()
    PATH=Model_dir+".pth"
    torch.save(model, PATH)
    print("The training took {}".format(end-init))
    return model

def run_experiment(model,Train_dataset,device,MODEL_DIR,RUNNAME,EXPERIMENT):
    mlflow.set_tracking_uri(uri="http://127.0.0.1:8080")
    # Create a new MLflow Experiment
    mlflow.set_experiment(EXPERIMENT)
    with mlflow.start_run():
        # Crear y entrenar el modelo
        mlflow.set_tag("mlflow.runName", RUNNAME)
        model = Training(model,Train_dataset,device,MODEL_DIR)
        # Registrar los hiperparámetros y métricas en MLflow
        mlflow.log_params({'epochs': 100, 'lr': 0.001})
        # Guardar el modelo entrenado
        mlflow.pytorch.log_model(model, 'model')
