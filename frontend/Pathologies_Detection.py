# import di streamlit per la realizzazione del front-end 
import streamlit as st

# necessaria per il caricamento del modello 
import joblib

# necessaria per far immettere i dati in input dall'utente 
import pandas as pd

import numpy as np 

# import delle librerie necessarie per l'inserimento dei grafici 
import matplotlib.pyplot as plt
import plotly.express as px

# librerie per il download e il caricamento di file 
from fpdf import FPDF
from datetime import datetime 

import plotly.graph_objects as go 

import os 

import requests 

from pathlib import Path 

input_valori = {} 

feature_slider = [] 
valori_arrotondati = {} 

# codice CSS per lo stile del sito 
st.markdown("""
<style>
    /* RIMOZIONE TOTALE E DEFINITIVA DI DEPLOY, 3 PUNTINI E STRUMENTI NATIVI */
    [data-testid="stStatusWidget"], 
    header[data-testid="stHeader"] [data-testid="stActionButton"],
    header[data-testid="stHeader"] .stDeployButton,
    header[data-testid="stHeader"] iframe, 
    div[data-testid="stConnectionStatus"],
    #MainMenu, 
    .stDeployButton {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }
            
    /* sfondo principale */
    .stApp {
        background-color: #0F2027;
        background-image: linear-gradient(135deg, #0F2027 0%, #203A43 50%, #2C5364 100%);
    }

    /* testo generale */
    .stApp, .stMarkdown, p, h1, h2, h3, label {
        color: #E0F7FA !important;
    }

    /* sidebar */
    [data-testid="stSidebar"] {
        background-color: #0A1A22 !important;
        border-right: 1px solid #00C9FF33;
    }

    /* pulsanti sidebar */
    [data-testid="stSidebar"] .stButton button {
        background-color: transparent !important;
        color: #00C9FF !important;
        border: 1px solid #00C9FF44 !important;
        border-radius: 8px !important;
        transition: all 0.2s ease;
    }
    [data-testid="stSidebar"] .stButton button:hover {
        background-color: #00C9FF22 !important;
        border-color: #00C9FF !important;
    }

    /* pulsanti principali */
    .stButton button {
        background: linear-gradient(90deg, #00C9FF22, #92FE9D22) !important;
        color: #92FE9D !important;
        border: 1px solid #92FE9D66 !important;
        border-radius: 8px !important;
        transition: all 0.2s ease;
    }
    .stButton button:hover {
        background: linear-gradient(90deg, #00C9FF44, #92FE9D44) !important;
        border-color: #92FE9D !important;
    }

    /* slider */
    .stSlider [data-testid="stSlider"] > div > div {
        background: linear-gradient(90deg, #00C9FF, #92FE9D) !important;
    }

    /* selectbox */
    .stSelectbox > div > div {
        background-color: #0A1A22 !important;
        border: 1px solid #00C9FF44 !important;
        color: #E0F7FA !important;
        border-radius: 8px !important;
    }

    /* success/error/info/warning */
    .stSuccess {
        background-color: #0A2A1A !important;
        border: 1px solid #92FE9D !important;
        color: #92FE9D !important;
    }
    .stError {
        background-color: #2A0A0A !important;
        border: 1px solid #FF6B6B !important;
        color: #FF6B6B !important;
    }
    .stInfo {
        background-color: #0A1A2A !important;
        border: 1px solid #00C9FF !important;
        color: #00C9FF !important;
    }

    /* linea separatrice */
    hr {
        border-color: #00C9FF33 !important;
    }

    /* download button */
    .stDownloadButton button {
        background: linear-gradient(90deg, #00C9FF, #92FE9D) !important;
        color: #0F2027 !important;
        border: none !important;
        font-weight: 500 !important;
        border-radius: 8px !important;
    }
            
    /* scelta della lingua del sito in ogni momento */ 
    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }
    
    header[data-testid="stHeader"]::before {
        content: "";
        position: absolute;
        top: 12px;
        /* Spostato a sinistra dei bottoni di deploy/menu di Streamlit */
        right: 160px; 
        z-index: 999999;
    }

    .custom-lang-bar {
        position: fixed;
        top: 12px;
        right: 160px;
        z-index: 9999999;
        display: flex;
        gap: 12px;
        background: #0A1A22;
        padding: 5px 12px;
        border-radius: 20px;
        border: 1px solid #00C9FF44;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }

    .flag-link {
        font-size: 19px;
        cursor: pointer;
        text-decoration: none;
        user-select: none;
        transition: transform 0.1s;
    }

    .flag-link:hover {
        transform: scale(1.25);
    }

    /* Nasconde i banner pubblicitari e i widget grafici grezzi di Google */
    .goog-te-banner-frame.skiptranslate, .goog-te-gadget, #goog-gt-tt {
        display: none !important;
    }
    body {
        top: 0px !important;
    }

</script>
<script type="text/javascript" src="//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit"></script>
""", unsafe_allow_html=True)

if "input_valori" not in st.session_state: 
    st.session_state["input_valori"] = {}

if "lingua" not in st.session_state:
    st.session_state["lingua"] = "inglese"

BASE_DIR = Path(__file__).resolve().parent.parent

# caricamento di CSV e modello dell'utente 
dataset_path = st.session_state.get("dataset_path", BASE_DIR / "dataset" / "dataset_unito.csv")
modello_path = st.session_state.get("modello_path", BASE_DIR / "model" / "Anemia_combined.pkl")

# se il custom non esiste usa il default 
if not os.path.exists(dataset_path): 
    dataset_path = BASE_DIR / "dataset" / "dataset_unito.csv"
if not os.path.exists(modello_path): 
    modello_path = BASE_DIR / "model" / "Anemia_combined.pkl"

df = pd.read_csv(dataset_path)
model = joblib.load(modello_path)

colonna_sesso = next((col for col in df.columns if col.lower() in ["sex", "gender", "male"]), None) 

if colonna_sesso: 
    df[colonna_sesso] = df[colonna_sesso].map({1: "Male", 0: "Female"}).fillna(df[colonna_sesso])

# la colonna target è l'ultima, tutte le altre sono features 
target = df.columns[-1]
features = df.columns[:-1].tolist()

if df[target].dtype == "object" or df[target].nunique() <= 10: 
    tipo_target = "classificazione"
else: 
    tipo_target = "regressione"

if "probabilità_testo" not in st.session_state:
    st.session_state["probabilità_testo"] = 0 

if "pred" not in st.session_state:
    st.session_state["pred"] = None

# funzione per colorare gli slider in base ai valori a norma 
def barra_valori(valore, minimo_norma, massimo_norma, minimo_slider, massimo_slider):
    fig = go.Figure()

    # zona verde (nella norma)
    fig.add_shape(type="rect", x0=minimo_norma, x1=massimo_norma, y0=0.35, y1=0.65,
        fillcolor="#44BB44", opacity=0.8, line_width=0)
    # zona rossa (non nella norma) 
    for x0, x1 in [(minimo_slider, minimo_norma), (massimo_norma, massimo_slider)]:
        fig.add_shape(type="rect", x0=x0, x1=x1, y0=0.35, y1=0.65,
            fillcolor="#FF4444", opacity=0.8, line_width=0)
    # stanghetta della barra sotto 
    fig.add_shape(type="line", x0=valore, x1=valore, y0=0.15, y1=0.85,
        line=dict(color="white", width=3))

    # arrotondamento dei valori minimi e massimi a 1 cifra dopo la virgola 
    fig.add_annotation(x=minimo_norma, y=0.1, text=str(round(minimo_norma, 1)),
        showarrow=False, font=dict(color="white", size=10))
    fig.add_annotation(x=massimo_norma, y=0.1, text=str(round(massimo_norma, 1)),
        showarrow=False, font=dict(color="white", size=10))

    # formattazione della barra e posizione 
    fig.update_layout(
        height=50,
        margin=dict(l=10, r=10, t=10, b=0),
        xaxis=dict(range=[minimo_slider, massimo_slider], showgrid=False, showticklabels=False, zeroline=False), 
        yaxis=dict(visible=False, range=[0, 1]),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(fig, use_container_width=True)

# sidebar con pagine del sito e tasti per cambiare la lingua 
with st.sidebar: 

    col1, col2 = st.columns(2)
    with col1:
        if st.button("![UK](https://flagcdn.com/w20/gb.png)", use_container_width=True):
            st.session_state["lingua"] = "inglese"
            st.rerun()
    with col2:
        if st.button("![IT](https://flagcdn.com/w20/it.png)", use_container_width=True):
            st.session_state["lingua"] = "italiano"
            st.rerun()

    if st.session_state["lingua"] == "inglese": 
        if "schermata" not in st.session_state:
            st.session_state["schermata"] = "home page"
        
        if st.button("Home page", use_container_width = True): 
            st.session_state["schermata"] = "home page"
            st.rerun()
        if st.button("Detection", use_container_width = True): 
            st.session_state["schermata"] = "detection"
            st.rerun()    
        if st.button("Stats", use_container_width = True): 
            st.session_state["schermata"] = "stats"
            st.rerun() 
        if st.button("Upload CSV and model", use_container_width = True): 
            st.session_state["schermata"] = "carica"
            st.rerun() 
    else: 
        if "schermata" not in st.session_state:
            st.session_state["schermata"] = "home page"
        
        if st.button("Pagina principale", use_container_width = True): 
            st.session_state["schermata"] = "home page"
            st.rerun()
        if st.button("Previsione", use_container_width = True): 
            st.session_state["schermata"] = "detection"
            st.rerun()    
        if st.button("Grafici statistici", use_container_width = True): 
            st.session_state["schermata"] = "stats"
            st.rerun() 
        if st.button("Carica CSV e modello", use_container_width = True): 
            st.session_state["schermata"] = "carica"
            st.rerun() 

if st.session_state["schermata"] == "home page": 

    col1, col2, col3 = st.columns(3) 
    with col2: 
        if st.session_state["lingua"] == "inglese":
            st.title("AI created only for you🧠💻")
        else:
            st.title("AI creata solo per te🧠💻")

    st.markdown("---")
    
    if st.session_state["lingua"] == "inglese":
        st.markdown("""
            ### Welcome to the platform that reveals your future. 
            This site use **machine learning** models to analize 
            your values and your datas and calculate the probability that an event will happen to you in the future.
            """)         
    else:
        st.markdown("""
            ### Benvenuto alla piattaforma che rivela il tuo futuro. 
            Questo sito usa modelli di **machine learning** per analizzare 
            i tuoi valori e i tuoi dati e calcola la probabilità che un evento ti accada nel futuro. 
            """)

    st.markdown("---") 



    if st.session_state["lingua"] == "inglese":
        st.markdown("""
            <div style="text-align: center; padding: 40px 0;">
                <h1 style="font-size: 3em; color: #2980B9;">🧠 AI Detection 💻</h1>
                <h3 style="color: #7F8C8D; font-weight: normal;">AI that's here for you</h3>
                <p style="font-size: 1.1em; color: #95A5A6;">With some informations the ML model will say you which will be your next events.</p>
            </div>
            """, unsafe_allow_html=True)     
    else:
        st.markdown("""
            <div style="text-align: center; padding: 40px 0;">
                <h1 style="font-size: 3em; color: #2980B9;">🧠 Detenzione dall'AI 💻</h1>
                <h3 style="color: #7F8C8D; font-weight: normal;">l'AI che è qui per te</h3>
                <p style="font-size: 1.1em; color: #95A5A6;">Con qualche informazione il modello di ML ti dirà quali saranno i prossimi eventi che ti accadranno.</p>
            </div>
            """, unsafe_allow_html=True)     

    st.markdown("---")

    # 3 card con icone SVG
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.session_state["lingua"] == "inglese":
            st.markdown("""
                <div style="background-color: #1A4A6E; border-radius: 15px; padding: 25px; text-align: center;">
                    <div style="font-size: 3em;">🔬</div>
                    <h3 style="color: white;">fast analysis</h3>
                    <p style="color: #AED6F1;">Insert your datas and obtain an immediated result thanks of our ML model.</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style="background-color: #1A4A6E; border-radius: 15px; padding: 25px; text-align: center;">
                    <div style="font-size: 3em;">🔬</div>
                    <h3 style="color: white;">analisi veloci</h3>
                    <p style="color: #AED6F1;">Inserisci i tuoi dati e ottieni subito il risultato grazie ai nostri modelli di Machine Learning.</p>
                </div>
                """, unsafe_allow_html=True)      

    with col2:
        if st.session_state["lingua"] == "inglese":
           st.markdown("""
            <div style="background-color: #1A4A6E; border-radius: 15px; padding: 25px; text-align: center;">
                <div style="font-size: 3em;">📊</div>
                <h3 style="color: white;">Statistics</h3>
                <p style="color: #AED6F1;">Explore interactive graphs based on real datas to comprend events distribution.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background-color: #1A4A6E; border-radius: 15px; padding: 25px; text-align: center;">
                <div style="font-size: 3em;">📊</div>
                <h3 style="color: white;">Statistica</h3>
                <p style="color: #AED6F1;">Esplora i grafici interattivi basati su dati reali per comprendere gli eventi di distribuzione.</p>
            </div>
            """, unsafe_allow_html=True)

    with col3:
        if st.session_state["lingua"] == "inglese": 
            st.markdown("""
            <div style="background-color: #1A4A6E; border-radius: 15px; padding: 25px; text-align: center;">
                <div style="font-size: 3em;">📄</div>
                <h3 style="color: white;">PDF Report</h3>
                <p style="color: #AED6F1;">Download a PDF certificate containing the data you entered, the result of the prediction and the related date.</p>
            </div>
            """, unsafe_allow_html=True)
        else: 
            st.markdown("""
            <div style="background-color: #1A4A6E; border-radius: 15px; padding: 25px; text-align: center;">
                <div style="font-size: 3em;">📄</div>
                <h3 style="color: white;">Documento PDF</h3>
                <p style="color: #AED6F1;">Scarica il tuo certificato in versione PDF contenente i dati da te inseriti, il risultato della predizione e la relativa data.</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # come funziona
    if st.session_state["lingua"] == "inglese": 
        st.markdown("<h2 style='text-align: center;'>How does it work?</h2>", unsafe_allow_html=True) 
    else: 
        st.markdown("<h2 style='text-align: center;'>Come funziona?</h2>", unsafe_allow_html=True) 

    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.session_state["lingua"] == "inglese": 
            st.markdown("""
            <div style="text-align: center;">
                <div style="font-size: 2.5em;">1️⃣</div>
                <h4 style="text-align: center;">Insert your data</h4>
                <p style="color: #7F8C8D;">Insert your values and your data.</p>
            </div>
            """, unsafe_allow_html=True)
        else: 
            st.markdown("""
            <div style="text-align: center;">
                <div style="font-size: 2.5em;">1️⃣</div>
                <h4 style="text-align: center;">inserisci i tuoi dati</h4>
                <p style="color: #7F8C8D;">Inserisci i tuoi valori e i tuoi dati.</p>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        if st.session_state["lingua"] == "inglese": 
            st.markdown("""
            <div style="text-align: center;">
                <div style="font-size: 2.5em;">2️⃣</div>
                <h4 style="text-align: center;">Analyses</h4>
                <p style="color: #7F8C8D;">ML runs your informations and calculates your probability to go through a specific event.</p>
            </div>
            """, unsafe_allow_html=True)
        else: 
            st.markdown("""
            <div style="text-align: center;">
                <div style="font-size: 2.5em;">2️⃣</div>
                <h4 style="text-align: center;">Analisi</h4>
                <p style="color: #7F8C8D;">L'ML legge i dati inseriti e calcola la probabilità di andare incontro all'evento in questione.</p>
            </div>
            """, unsafe_allow_html=True)

    with col3:
        if st.session_state["lingua"] == "inglese": 
            st.markdown("""
            <div style="text-align: center;">
                <div style="font-size: 2.5em;">3️⃣</div>
                <h4 style="text-align: center;">Download</h4>
                <p style="color: #7F8C8D;">Receive your personalized PDF report.</p>
            </div>
            """, unsafe_allow_html=True) 
        else: 
            st.markdown("""
            <div style="text-align: center;">
                <div style="font-size: 2.5em;">3️⃣</div>
                <h4 style="text-align: center;">Scarica</h4>
                <p style="color: #7F8C8D;">Ricevi il tuo PDF personalizzato.</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # disclaimer 
    if st.session_state["lingua"] == "inglese": 
        st.warning("⚠️ This site was created to do prevention, it doesn't sobstitute an expert's opinion.") 
    else: 
        st.warning("⚠️ Questo sito è stato ideato per fare prevenzione, non sostituisce l'opinione di un esperto.")

if st.session_state["schermata"] == "detection": 

    # schermata principale (previsione) 
    if st.session_state["lingua"] == "inglese": 
        st.title(f"{target}'s Detection") # questo è il titolo che apparirà sulla nostra pagina 
    else: 
        st.title(f"Previsione di {target}") 

    for feature in features: 
        if df[feature].dtype == "object" or df[feature].nunique() <= 5:
            # feature categorica → selectbox
            opzioni = df[feature].unique().tolist()
            input_valori[feature] = st.selectbox(feature, options=opzioni) 
        else: 
            if st.session_state["lingua"] == "inglese":     
                if feature == "Hemoglobin": 
                    st.info("Hemoglobin: is the protein in red blood cells that transports oxygen to organs and tissues.")
                elif feature == "MCH":
                    st.info("MCH: indicates the average size of red blood cells.")
                elif feature == "MCHC":
                    st.info("MCHC: represents the average quantity of hemoglobin present in each single red blood cell.")
                elif feature == "MCV":
                    st.info("MCV: Red blood cell hemoglobin concentration calculator, cell color indicator (healthy or too pale).") 
            else: 
                if feature == "Hemoglobin": 
                    st.info("Emoglobina: è la proteina presente nei globuli rossi che trasportano ossigeno a organi e tessuti.")
                elif feature == "MCH":
                    st.info("MCH: indica la dimensione media dei globuli rossi.")
                elif feature == "MCHC":
                    st.info("MCHC: rappresenta la quantità media di emoglobina presente in ogni globulo rosso.")
                elif feature == "MCV":
                    st.info("MCV: la concentrazione di emoglobina nei globuli rossi, il colore della cellula ne indica lo stato di salute (sana o troppo pallida).") 

            feature_slider.append(feature)

            # feature numerica → slider
            min_val = float(df[feature].min())
            max_val = float(df[feature].max())
            mean_val = float(df[feature].mean())
            input_valori[feature] = st.slider(feature, min_value=min_val, max_value=max_val, value=mean_val, step=0.1)

            min_norma = float(df[feature].mean() - df[feature].std())
            max_norma = float(df[feature].mean() + df[feature].std())
            barra_valori(input_valori[feature], min_norma, max_norma, min_val, max_val)

    if st.session_state["lingua"] == "inglese": 
        if st.button("Predict"): # creazione del bottone con sotto all'if ciò che accade se l'utente clicca il bottone 
            
            st.session_state['input_valori'] = input_valori 

            # viene creata una riga del df con i valori inseriti dall'utente 
            risposta = requests.post("http://api:8000/predict", json={
                "features": input_valori,
                "modello_path": st.session_state.get("modello_path", "Anemia_combined.pkl"), 
                "dataset_path": st.session_state.get("dataset_path", "/dataset/dataset_unito.csv")
            })      

            pred_df = pd.DataFrame([risposta.json()])
            pred = [pred_df["risultato"].iloc[0]]

            if tipo_target == "classificazione": 
                probabilità = round(risposta.json()["probabilità"] * 100, 2)

                if probabilità < 50: 
                    st.success(f"Probability: {probabilità}%")
                else: 
                    st.error(f"Probability: {probabilità}%") 
            else: 
                probabilità = 0

            st.session_state['input_valori'] = input_valori

            for k, v in input_valori.items():
                if k in feature_slider:
                    if isinstance(v, float) and v != int(v):
                        valori_arrotondati[k] = round(v, 1) 
                    else:
                        valori_arrotondati[k] = int(v) 

            df_arrotondato = df[feature_slider].copy()
            for col in feature_slider:
                if np.issubdtype(df[col].dtype, np.floating):
                    df_arrotondato[col] = df[col].round(1)
                else:
                    df_arrotondato[col] = df[col].astype(int)

            ricerca = (df_arrotondato == pd.Series(valori_arrotondati)).all(axis=1)
            uguali = df[ricerca]

            # stampa del risultato della ricerca 
            if len(uguali) > 0: 
                st.info(f"Other {len(uguali)} people have values similar to yours.") 

                # conteggio e stampa a schermo del numero di persone anemiche e non anemiche tra queste 
                positivi = int((uguali[target] == 1).sum())
                negativi = int((uguali[target] == 0).sum())

                st.write(f"Of these, {positivi} has received a positive result from the analisy.")
                st.write(f"Of these, {negativi} has received a negative result from the analisy.")
            else: 
                st.info("No one had the values similar to yours.")

            st.session_state['probabilità_testo'] = probabilità 
            st.session_state['pred'] = pred[0]

            pdf = FPDF()
            pdf.add_page()

            # intestazione colorata
            pdf.set_fill_color(41, 128, 185)
            pdf.rect(0, 0, 210, 30, 'F')
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Arial", style="B", size=20)
            pdf.cell(200, 30, txt=f"{target} - Result", ln=True, align="C")
            pdf.ln(5)

            # sezione dati paziente
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", style="B", size=13)
            pdf.cell(200, 10, txt="User's values", ln=True)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(3)
            pdf.set_font("Arial", size=12)
            for feature, valore in st.session_state['input_valori'].items():
                if isinstance(valore, float):
                    valore = round(valore, 2)
                pdf.cell(200, 8, txt=f"{feature}: {valore}", ln=True)
            pdf.ln(5)

            # sezione risultato
            pdf.set_font("Arial", style="B", size=13)
            pdf.cell(200, 10, txt="Result", ln=True)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(3)
            if st.session_state['probabilità_testo'] < 50:
                pdf.set_fill_color(39, 174, 96)
            else:
                pdf.set_fill_color(192, 57, 43)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Arial", style="B", size=14)
            if tipo_target == "classificazione":
                pdf.cell(190, 12, txt=f"Result: {st.session_state['probabilità_testo']}%", ln=True, align="C", fill=True)
            else:
                pdf.cell(190, 12, txt=f"Predicted value: {round(st.session_state['pred'], 2)}", ln=True, align="C", fill=True)

            # testo che appare sotto al risultato 
            pdf.ln(5)
            pdf.set_font("Arial", size=10)
            pdf.set_text_color(100, 100, 100)
            pdf.multi_cell(190, 6, txt = f"""This document has been automatically generated by the system. The result printed rappresents a statistic prediction based on real cases. It doesn't sobstitute a professtionist's opinion.""")

            # piè di pagina con data e ora di stampa 
            pdf.set_y(-30)
            pdf.set_font("Arial", size=8)
            pdf.set_text_color(128, 128, 128)
            pdf.cell(180, 10, txt = f"{str(datetime.now())}", ln=True, align="R")

            pdf.output(f"Result {target}.pdf")
            with open(f"Result {target}.pdf", "rb") as f:
                pdf_bytes = f.read()

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.download_button(label="Download your ufficial certificate", data=pdf_bytes, file_name=f"ML result prediction.pdf", mime="application/pdf")

    else: 
        if st.button("Predici"): # creazione del bottone con sotto all'if ciò che accade se l'utente clicca il bottone 
            
            st.session_state['input_valori'] = input_valori 

            # viene creata una riga del df con i valori inseriti dall'utente 
            risposta = requests.post("http://api:8000/predict", json={
                "features": input_valori,
                "modello_path": st.session_state.get("modello_path", "Anemia_combined.pkl"), 
                "dataset_path": st.session_state.get("dataset_path", "/dataset/dataset_unito.csv")
            })      

            pred_df = pd.DataFrame([risposta.json()])
            pred = [pred_df["risultato"].iloc[0]]

            if tipo_target == "classificazione": 
                probabilità = round(risposta.json()["probabilità"] * 100, 2)

                if probabilità < 50: 
                    st.success(f"Probabilità: {probabilità}%")
                else: 
                    st.error(f"Probabilità: {probabilità}%") 
            else: 
                probabilità = 0

            st.session_state['input_valori'] = input_valori

            for k, v in input_valori.items():
                if k in feature_slider:
                    if isinstance(v, float) and v != int(v):
                        valori_arrotondati[k] = round(v, 1) 
                    else:
                        valori_arrotondati[k] = int(v) 

            df_arrotondato = df[feature_slider].copy()
            for col in feature_slider:
                if np.issubdtype(df[col].dtype, np.floating):
                    df_arrotondato[col] = df[col].round(1)
                else:
                    df_arrotondato[col] = df[col].astype(int)

            ricerca = (df_arrotondato == pd.Series(valori_arrotondati)).all(axis=1)
            uguali = df[ricerca]

            # stampa del risultato della ricerca 
            if len(uguali) > 0: 
                st.info(f"Altre {len(uguali)} persone hanno valori simili ai tuoi.") 

                # conteggio e stampa a schermo del numero di persone anemiche e non anemiche tra queste 
                positivi = int((uguali[target] == 1).sum())
                negativi = int((uguali[target] == 0).sum())

                st.write(f"Di queste, {positivi} hanno avuto esito positivo all'analisi.")
                st.write(f"Di queste, {negativi} hanno avuto esito negativo all'analisi.")
            else: 
                st.info("Nessun'altra persona ha vuto valori simili ai tuoi.")

            st.session_state['probabilità_testo'] = probabilità 
            st.session_state['pred'] = pred[0]

            pdf = FPDF()
            pdf.add_page()

            # intestazione colorata
            pdf.set_fill_color(41, 128, 185)
            pdf.rect(0, 0, 210, 30, 'F')
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Arial", style="B", size=20)
            pdf.cell(200, 30, txt=f"{target} - Risultato", ln=True, align="C")
            pdf.ln(5)

            # sezione dati paziente
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", style="B", size=13)
            pdf.cell(200, 10, txt="Valori dell'utente", ln=True)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(3)
            pdf.set_font("Arial", size=12)
            for feature, valore in st.session_state['input_valori'].items():
                if isinstance(valore, float):
                    valore = round(valore, 2)
                pdf.cell(200, 8, txt=f"{feature}: {valore}", ln=True)
            pdf.ln(5)

            # sezione risultato
            pdf.set_font("Arial", style="B", size=13)
            pdf.cell(200, 10, txt="Risultato", ln=True)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(3)
            if st.session_state['probabilità_testo'] < 50:
                pdf.set_fill_color(39, 174, 96)
            else:
                pdf.set_fill_color(192, 57, 43)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Arial", style="B", size=14)
            if tipo_target == "classificazione":
                pdf.cell(190, 12, txt=f"Risultato: {st.session_state['probabilità_testo']}%", ln=True, align="C", fill=True)
            else:
                pdf.cell(190, 12, txt=f"Valore predetto: {round(st.session_state['pred'], 2)}", ln=True, align="C", fill=True)

            # testo che appare sotto al risultato 
            pdf.ln(5)
            pdf.set_font("Arial", size=10)
            pdf.set_text_color(100, 100, 100)
            pdf.multi_cell(190, 6, txt = f"""Questo documento è stato generato automaticamente dal sistema. Il risultato stampato rappresenta una predizione statistica basata su casi reali. Ciò non sostituisce l'analisi di un professionista.""")

            # piè di pagina con data e ora di stampa 
            pdf.set_y(-30)
            pdf.set_font("Arial", size=8)
            pdf.set_text_color(128, 128, 128)
            pdf.cell(180, 10, txt = f"{str(datetime.now())}", ln=True, align="R")

            pdf.output(f"Risultato {target}.pdf")
            with open(f"Risultato {target}.pdf", "rb") as f:
                pdf_bytes = f.read()

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.download_button(label="Scarica il tuo certificato ufficiale", data=pdf_bytes, file_name=f"risultato previsione da ML.pdf", mime="application/pdf")

if st.session_state["schermata"] == "stats": 
    if st.session_state["lingua"] == "inglese": 
        st.title("Stats")
    else: 
        st.title("Statistica")

    df_visualizzazione = df.copy()
    
    if colonna_sesso: 
        # mapping di gender 
        df_visualizzazione[colonna_sesso] = df_visualizzazione[colonna_sesso].astype(str).map({
            "1": "Male", "1.0": "Male", "Male": "Male",
            "0": "Female", "0.0": "Female", "Female": "Female"
        }).fillna(df_visualizzazione[colonna_sesso])

    # mapping di result 
    df_visualizzazione[target] = df_visualizzazione[target].astype(str).map({
        "1": "Anemic", "1.0": "Anemic", "Anemic": "Anemic",
        "0": "Not anemic", "0.0": "Not anemic", "Not anemic": "Not anemic"
    }).fillna(df_visualizzazione[target]) 

    if st.session_state["lingua"] == "inglese":     
        # grafico conteggio target
        conteggio = df_visualizzazione[target].value_counts().reset_index()
        conteggio.columns = [target, "Number of people"]
        fig = px.bar(conteggio, x=target, y="Number of people", color=target, title=f"{target}'s distribution")
        st.plotly_chart(fig)
    else: 
        # grafico conteggio target
        conteggio = df_visualizzazione[target].value_counts().reset_index()
        conteggio.columns = [target, "Numero di persone"]
        fig = px.bar(conteggio, x=target, y="Numero di persone", color=target, title=f"Distribuzione di {target}")
        st.plotly_chart(fig)

    colori_pair = [
    ["#FF4444", "#FF9999"],
    ["#44BB44", "#99DD99"],
    ["#1E90FF", "#87CEEB"],
    ["#FFD700", "#FFE680"],
    ["#9B59B6", "#C39BD3"],
    ["#FF69B4", "#FFB6C1"],
    ["#FFA500", "#FFCC80"],
    ["#00008B", "#4444AA"]
    ]

    if st.session_state["lingua"] == "inglese":     
        for i, feature in enumerate(features):
            coppia = colori_pair[i % len(colori_pair)]
            
            if df[feature].nunique() <= 5:
                fig = px.histogram(df_visualizzazione, x=feature, color=target, color_discrete_sequence=coppia, title=f"Correlation between {feature} and {target}")
            else:
                fig = px.histogram(df_visualizzazione, x=feature, color=target, color_discrete_sequence=coppia, title=f"Distribution of {feature} in {target}")
            
            st.plotly_chart(fig)
    else: 
        for i, feature in enumerate(features):
            coppia = colori_pair[i % len(colori_pair)]
            
            if df[feature].nunique() <= 5:
                fig = px.histogram(df_visualizzazione, x=feature, color=target, color_discrete_sequence=coppia, title=f"Correlazione tra {feature} e {target}")
            else:
                fig = px.histogram(df_visualizzazione, x=feature, color=target, color_discrete_sequence=coppia, title=f"Distribuzione di {feature} in {target}")
            
            st.plotly_chart(fig)

    if st.session_state["lingua"] == "inglese": 
        # analisi di qual'è la feature più incisiva per la predizione 
        st.header("Most incisive feature")

        try:
            coefficienti = np.abs(model.coef_[0])
            
            if hasattr(model, 'feature_names_in_'):
                nomi_feature = list(model.feature_names_in_)
            else:
                nomi_feature = features

            if len(coefficienti) == len(nomi_feature):
                feature_importance = pd.DataFrame({
                    "Feature": nomi_feature,
                    "Importance": coefficienti
                }).sort_values("Importance", ascending=False).head(1)

                for i, row in feature_importance.iterrows():
                    st.markdown(f"""
                    <div style="background-color: #0A1A22; border: 1px solid #00C9FF44; border-radius: 8px; padding: 12px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #00C9FF; font-weight: 500;">{row['Feature']}</span>
                        <span style="color: #92FE9D;">{round(row['Importance'], 4)}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Feature importance not available: model and dataset are not compatible.")

        except AttributeError:
            st.info("The uploaded ML model doesn't support the most incisive feature's analysis.")

        # generazione del pdf con i grafici ogni volta che si apre la pagina stats 
        pdf_stats = FPDF()
        pdf_stats.add_page()
        pdf_stats.set_font("Arial", style = "B", size = 16)
        pdf_stats.cell(200, 10, txt = "Statistic Report", ln = True, align = "C")
        pdf_stats.ln(5)

        for i, feature in enumerate(features):
            fig_mpl, ax = plt.subplots(figsize = (8, 3))
            
            for val in df_visualizzazione[target].unique(): 
                subset = df_visualizzazione[df_visualizzazione[target] == val][feature]
                if df[feature].nunique() <= 5: 
                    subset.value_counts().plot(kind = "bar", ax = ax, label = str(val))
                else: 
                    ax.hist(subset, bins = 20, alpha = 0.7, label = str(val))
            
            ax.set_title(f"{feature} for {target}")
            ax.legend()
            img_path = f"temp_graph_{i}.png"
            fig_mpl.savefig(img_path, bbox_inches = "tight")
            plt.close(fig_mpl)
            pdf_stats.image(img_path, w = 180)
            pdf_stats.ln(3)
        
        pdf_stats.output("stats.pdf")
        with open("stats.pdf", "rb") as f: 
            pdf_stats_bytes = f.read()
        
        # mostra del bottone di download 
        col1, col2, col3 = st.columns([6, 3, 6])
        with col2: 
            st.download_button(label="Download stats", data=pdf_stats_bytes, file_name="Graphs.pdf", mime="application/pdf") 
    else: 
        # analisi di qual'è la feature più incisiva per la predizione 
        st.header("Caratteristica più incisiva")

        try:
            coefficienti = np.abs(model.coef_[0])
            
            if hasattr(model, 'feature_names_in_'):
                nomi_feature = list(model.feature_names_in_)
            else:
                nomi_feature = features

            if len(coefficienti) == len(nomi_feature):
                feature_importance = pd.DataFrame({
                    "Caratteristica": nomi_feature,
                    "Incisività": coefficienti
                }).sort_values("Incisività", ascending=False).head(1)

                for i, row in feature_importance.iterrows():
                    st.markdown(f"""
                    <div style="background-color: #0A1A22; border: 1px solid #00C9FF44; border-radius: 8px; padding: 12px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #00C9FF; font-weight: 500;">{row['Caratteristica']}</span>
                        <span style="color: #92FE9D;">{round(row['Incisività'], 4)}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Incisività della caratteristica non disponibile: il modello e il dataset non sono compatibili.")

        except AttributeError:
            st.info("Il modello di ML caricato non supporta l'analisi della caratteristica più incisiva.")

        # generazione del pdf con i grafici ogni volta che si apre la pagina stats 
        pdf_stats = FPDF()
        pdf_stats.add_page()
        pdf_stats.set_font("Arial", style = "B", size = 16)
        pdf_stats.cell(200, 10, txt = "Relazione statistica", ln = True, align = "C")
        pdf_stats.ln(5)

        for i, feature in enumerate(features):
            fig_mpl, ax = plt.subplots(figsize = (8, 3))
            
            for val in df_visualizzazione[target].unique(): 
                subset = df_visualizzazione[df_visualizzazione[target] == val][feature]
                if df[feature].nunique() <= 5: 
                    subset.value_counts().plot(kind = "bar", ax = ax, label = str(val))
                else: 
                    ax.hist(subset, bins = 20, alpha = 0.7, label = str(val))
            
            ax.set_title(f"{feature} per {target}")
            ax.legend()
            img_path = f"temp_graph_{i}.png"
            fig_mpl.savefig(img_path, bbox_inches = "tight")
            plt.close(fig_mpl)
            pdf_stats.image(img_path, w = 180)
            pdf_stats.ln(3)
        
        pdf_stats.output("grafici.pdf")
        with open("grafici.pdf", "rb") as f: 
            pdf_stats_bytes = f.read()
        
        # mostra del bottone di download 
        col1, col2, col3 = st.columns([6, 3, 6])
        with col2: 
            st.download_button(label="Scarica i grafici", data=pdf_stats_bytes, file_name="Grafici.pdf", mime="application/pdf")


if st.session_state["schermata"] == "carica": 
    if st.session_state["lingua"] == "inglese": 
        st.title("Upload your dataset and your ML model")

        csv_caricato = st.file_uploader("Upload dataset (.csv)", type = ["csv"]) 
        modello_caricato = st.file_uploader("Upload model (.pkl)", type = ["pkl"])

        if csv_caricato and modello_caricato: 
            if st.button("Save"): 
                with open("/dataset/dataset_custom.csv", "wb") as f: 
                    f.write(csv_caricato.read()) 
                with open("/model/modello_custom.pkl", "wb") as f: 
                    f.write(modello_caricato.read())

                st.session_state["dataset_path"] = "/dataset/dataset_custom.csv"
                st.session_state["modello_path"] = "modello_custom.pkl"

                st.success("Dataset and model uploaded successfully")
                st.rerun()

        if st.button("Restore"): 
            st.session_state["dataset_path"] = "/dataset/dataset_unito.csv"
            st.session_state["modello_path"] = "Anemia_combined.pkl"
            st.success("Dataset and model has been restored successfully")
            st.rerun() 
    else: 
        st.title("Carica il tuo dataset e il tuo modello di Machine Learning")

        csv_caricato = st.file_uploader("Carica dataset (.csv)", type = ["csv"]) 
        modello_caricato = st.file_uploader("Carica modello (.pkl)", type = ["pkl"])

        if csv_caricato and modello_caricato: 
            if st.button("Salva"): 
                with open("/dataset/dataset_custom.csv", "wb") as f: 
                    f.write(csv_caricato.read()) 
                with open("/model/modello_custom.pkl", "wb") as f: 
                    f.write(modello_caricato.read())

                st.session_state["dataset_path"] = "/dataset/dataset_custom.csv"
                st.session_state["modello_path"] = "modello_custom.pkl"

                st.success("Caricamento del dataset e del modello andato a buon fine")
                st.rerun()

        if st.button("Ripristina"): 
            st.session_state["dataset_path"] = "/dataset/dataset_unito.csv"
            st.session_state["modello_path"] = "Anemia_combined.pkl"
            st.success("Ripristino di dataset e modello avvenuto con successo")
            st.rerun() 