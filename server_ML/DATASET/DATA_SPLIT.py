import json
from sklearn.model_selection import train_test_split
from collections import Counter
import os
import pandas as pd


def DATA_INIT(TRAINING_DATASET,TESTING_DATASET,DATASET_DIR,TAG_FILE,CONF):
    tag_file=TAG_FILE
    data_directory=DATASET_DIR
    train_directory=TRAINING_DATASET
    test_directory=TESTING_DATASET
    tag_file=read_tag_json(tag_file)
    route=get_file_paths(data_directory,tag_file)
    df = pd.DataFrame(route)
    train, test = train_test_split(df, test_size=0.2, random_state=0, stratify=df[*CONF["TAG"]])
    train=train.to_dict(orient='records')
    test=test.to_dict(orient='records')
    load_tag_json(train,train_directory)
    load_tag_json(train,test_directory)



def load_tag_json(dataset,route):
    with open(route, 'w') as json_file:
        json.dump(dataset, json_file, indent=4)


def read_tag_json(archivo_txt):
    with open(archivo_txt, 'r') as archivo:
        datos_json = json.load(archivo)
    return datos_json

def get_file_paths(directory,tag_file):
        file_paths = []
        for root, _, files in os.walk(directory):
          for tag in tag_file.keys():
            if root.endswith(tag):
              for file in files:
                  if file.endswith(('.wav', '.mp3')):
                      file_paths.append({"file":os.path.join(root, file),"tag":tag_file[tag]["gender"],"person":tag})

        for i in range(len(file_paths)):
            file_paths[i]["index"]=i

        return file_paths

