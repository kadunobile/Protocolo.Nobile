"""
Configuração e constantes da aplicação Nobile Career Strategy
"""

import streamlit as st

# --- CONSTANTES ---
MAX_CV_TEXT_FOR_TRIGGER = 4000  # Máximo de caracteres do CV enviados no trigger inicial
MAX_CV_TEXT_LENGTH = 2000  # Máximo de caracteres do CV para extração de cargo
MAX_CV_TEXT_LENGTH_ATS = 3000  # Máximo de caracteres do CV para cálculo ATS
P4_DETECTION_KEYWORDS = ["P4", "Onde você mora", "localização"]  # Keywords para detectar a pergunta P4

# --- CONFIGURAÇÃO DA PÁGINA ---
def setup_page():
    """Configura a página Streamlit"""
    st.set_page_config(page_title="Nobile Career Strategy", page_icon="♟️", layout="wide")

# --- CSS CUSTOMIZADO (DARK MODE) ---
def apply_custom_css():
    """Aplica CSS customizado para dark mode"""
    st.markdown("""
    <style>
        .stApp { background-color: #0E1117; color: #FAFAFA; }
        .stButton>button {
            background-color: #238636;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            font-weight: bold;
        }
        .stButton>button:hover { background-color: #2ea043; }
        .stChatMessage[data-testid="user"] { background-color: #0d4a2b; }
    </style>
    """, unsafe_allow_html=True)
