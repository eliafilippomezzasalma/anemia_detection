from fastapi import FastAPI 
import joblib 
import numpy as np 
import pandas as pd 

# libreria necessaria per la generalizzazione del codice, affinchè funzioni anche per altri dataset e modelli 
from typing import Dict, Any 

app = FastAPI()

@app.post("/predict") 

def predict(data: Dict[str, Any]): 
    modello_path = data.get("modello_path", "Anemia.pkl")
    dataset_path = data.get("dataset_path", "/dataset/anemia.pkl")

    features = data.get("features")

    # caricamento del modello 
    model = joblib.load(f"/model/{modello_path}")

    df = pd.read_csv(dataset_path)
    target = df.columns[-1]
    df = df.drop(columns = [target])

    df_con_input = pd.concat([df, pd.DataFrame([features])], ignore_index = True) 
    input_df = pd.get_dummies(df_con_input, drop_first = True).tail(1) 

    try: 
        colonne_modello = model.feature_names_in_ 
        for col in colonne_modello: 
            if col not in input_df.columns: 
                input_df[col] = 0 
        input_df = input_df[colonne_modello]
    except AttributeError: 
        pass 

    prediction = model.predict(input_df)[0]
    probability = model.predict_proba(input_df)[0][1]

    return {"risultato": int(prediction), "probabilità": float(probability)}