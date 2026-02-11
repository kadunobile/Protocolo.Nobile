import streamlit as st
import openai
import pdfplumber
import time

# --- 1. CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Nobile Career Strategy", page_icon="♟️", layout="wide")

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

# --- 2. O ROTEIRO MESTRE (SEU SCRIPT EXATO) ---
SYSTEM_PROMPT = """
ATUE COMO UM HEADHUNTER E ESTRATEGISTA DE CARREIRA (VERSÃO ELITE GLOBAL).
Role: Você é um Headhunter Executivo Sênior, Especialista em ATS e LinkedIn Top Voice.
Regra de Ouro: Você constrói um perfil de Alta Performance. Em cada etapa, você PAUSA, entrevista e valida.

ESTRUTURA DE FASES (Siga rigorosamente):

FASE 1: DIAGNÓSTICO (O PRIMEIRO PASSO)
- Leia o CV. Identifique a área macro.
- Responda: "Entendi. Atuarei como especialista em [Área]. Para traçarmos a estratégia, responda:"
- Pergunte P1 (Objetivo), P2 (Cargos Específicos), P3 (Pretensão Realista), P4 (Localização).
- AGUARDE AS RESPOSTAS. NÃO AVANCE.

FASE 2: MENU
- Só libere o Menu após ter as respostas P1-P4.

FASE 3: EXECUÇÃO (QUANDO O USUÁRIO ESCOLHER NO MENU)
- Etapa 1 (SEO): Liste 10 palavras-chave do Cargo P2. Compare com o CV. Pergunte sobre as faltantes. PAUSE.
- Etapa 2 (Métricas): Para cada experiência, desafie: "Preciso de números. Qual impacto (R$, %)?". PAUSE.
- Etapa 3 (Curadoria): Pergunte: "Tem alguma conquista indispensável que não cobrimos?". PAUSE.
- Etapa 4 (Engenharia): Reescreva Resumo e Experiências usando estruturas de alta performance.
- Etapa 5 (Arquivo Mestre): Gere o texto final.

IMPORTANTE: Mantenha o tom consultivo e estratégico.
"""

# --- 3. FUNÇÕES ---
def extract_text(file):
    try:
        with pdfplumber.open(file) as pdf:
            return "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
    except: return None

def get_response(messages, api_key):
    if not api_key: return "⚠️ Insira a API Key na barra lateral."
    client = openai.OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro na IA: {e}"

# --- 4. CONTROLE DE ESTADO ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
if "cv_content" not in st.session_state: st.session_state.cv_content = None
if "fase_atual" not in st.session_state: st.session_state.fase_atual = "UPLOAD"

# --- 5. SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3048/3048127.png", width=60)
    st.title("Nobile Strategy")
    api_key = st.text_input("OpenAI API Key", type="password")

    st.markdown("---")
    if st.button("🔄 Reiniciar Sessão"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

# --- 6. INTERFACE PRINCIPAL ---
st.title("Headhunter Elite Global AI")

# FASE 1: UPLOAD (Gatilho Inicial)
if not st.session_state.cv_content:
    uploaded_file = st.file_uploader("Suba seu CV (PDF)", type="pdf")

    if uploaded_file and api_key:
        with st.spinner("Lendo perfil..."):
            text = extract_text(uploaded_file)
            st.session_state.cv_content = text
            st.session_state.fase_atual = "DIAGNOSTICO"

            # Força o início do Diagnóstico
            trigger = f"O USUÁRIO SUBIU O CV: {text[:4000]}... INICIE A FASE 1 (DIAGNÓSTICO) AGORA."
            st.session_state.messages.append({"role": "user", "content": trigger})
            reply = get_response(st.session_state.messages, api_key)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()

# FASE 2: CHAT INTERATIVO
else:
    # Mostra histórico (ocultando prompts técnicos)
    for msg in st.session_state.messages:
        if msg["role"] != "system" and "O USUÁRIO SUBIU" not in str(msg["content"]) and "ACIONOU" not in str(msg["content"]):
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Lógica Automática para detectar liberação do MENU
    last_ai_msg = st.session_state.messages[-1]["content"] if st.session_state.messages else ""
    if "P4" in last_ai_msg or "Onde você mora" in last_ai_msg:
        st.session_state.fase_atual = "DIAGNOSTICO_EM_ANDAMENTO"
    elif st.session_state.fase_atual == "DIAGNOSTICO_EM_ANDAMENTO" and len(st.session_state.messages) > 4:
        st.session_state.fase_atual = "MENU"

    # INPUT DO USUÁRIO
    user_input = st.chat_input("Sua resposta...")

    # PROCESSAMENTO DE MENSAGEM
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.rerun()

    # RESPOSTA DA IA (Se a última msg for User, a IA responde sozinha)
    if st.session_state.messages[-1]["role"] == "user":
        with st.chat_message("assistant"):
            with st.spinner("Headhunter analisando..."):
                response = get_response(st.session_state.messages, api_key)
                st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

    # MENU DE COMANDOS (Aparece só depois do Diagnóstico)
    if st.session_state.fase_atual in ["MENU", "EXECUCAO"] and st.session_state.messages[-1]["role"] == "assistant":
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 /otimizador_cv_linkedin"):
                st.session_state.fase_atual = "EXECUCAO"
                trigger = "O usuário ACIONOU: /otimizador_cv_linkedin. INICIE A ETAPA 1 (SEO)."
                st.session_state.messages.append({"role": "user", "content": trigger})
                st.rerun()

        with col2:
            if st.button("📄 Pular para Arquivo Final"):
                 trigger = "Pule para a ETAPA 5: ARQUIVO MESTRE."
                 st.session_state.messages.append({"role": "user", "content": trigger})
                 st.rerun()
