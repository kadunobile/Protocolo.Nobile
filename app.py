import streamlit as st

# Importar módulos do projeto
from config import setup_page, apply_custom_css, MAX_CV_TEXT_FOR_TRIGGER, P4_DETECTION_KEYWORDS
from prompts import SYSTEM_PROMPT, PromptTemplates
from utils import extract_text
from engine import get_response, extract_role_from_cv, calculate_ats_score

# --- 1. CONFIGURAÇÃO VISUAL ---
setup_page()
apply_custom_css()

# --- 4. CONTROLE DE ESTADO ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
if "cv_content" not in st.session_state: st.session_state.cv_content = None
if "fase_atual" not in st.session_state: st.session_state.fase_atual = "UPLOAD"
if "ats_data" not in st.session_state: st.session_state.ats_data = None
if "target_role" not in st.session_state: st.session_state.target_role = ""

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

# EXIBIR ATS SCORE NO TOPO (Dashboard sempre visível)
if st.session_state.ats_data and st.session_state.ats_data != "calculating":
    st.markdown("---")

    data = st.session_state.ats_data
    score = data.get('ats_score', 0)

    # Dashboard Header com Score
    col_header1, col_header2, col_header3 = st.columns([1, 2, 2])

    with col_header1:
        color = "#4CAF50" if score >= 70 else "#FF9800" if score >= 50 else "#FF5252"
        st.markdown(f"""
        <div style="background-color: #1E1E1E; border: 3px solid {color}; padding: 20px;
             border-radius: 10px; text-align: center;">
            <div style="font-size: 3.5em; font-weight: bold; color: {color};">{score}%</div>
            <div style="font-size: 1em; color: #AAA; margin-top: 5px;">ATS Score</div>
            <div style="font-size: 0.85em; color: #888; margin-top: 5px;">Cargo: {st.session_state.target_role}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_header2:
        st.markdown("**✅ Keywords Presentes:**")
        keywords_present = data.get('keywords_present', [])
        if keywords_present:
            for i, kw in enumerate(keywords_present[:5]):
                st.success(f"• {kw}", icon="✅")
        else:
            st.info("Nenhuma keyword identificada")

    with col_header3:
        st.markdown("**❌ Keywords Faltantes:**")
        keywords_missing = data.get('keywords_missing', [])
        if keywords_missing:
            for i, kw in enumerate(keywords_missing[:5]):
                st.error(f"• {kw}", icon="❌")
        else:
            st.success("Nenhuma keyword faltante!")

    # Recomendações em linha
    if data.get('recomendacoes'):
        with st.expander("💡 Ver Recomendações ATS", expanded=False):
            for rec in data.get('recomendacoes', []):
                st.info(f"• {rec}")

    st.markdown("---")

# FASE 1: UPLOAD (Gatilho Inicial)
if not st.session_state.cv_content:
    uploaded_file = st.file_uploader("Suba seu CV (PDF)", type="pdf")

    if uploaded_file and api_key:
        with st.spinner("Lendo perfil e calculando ATS Score..."):
            text = extract_text(uploaded_file)
            st.session_state.cv_content = text
            st.session_state.fase_atual = "DIAGNOSTICO"

            # Extrai o cargo do CV automaticamente
            detected_role = extract_role_from_cv(text, api_key)
            st.session_state.target_role = detected_role

            # Calcula ATS Score automaticamente
            ats_result = calculate_ats_score(text, detected_role, api_key)
            st.session_state.ats_data = ats_result

            # Força o início do Diagnóstico
            trigger = PromptTemplates.cv_upload_trigger(text[:MAX_CV_TEXT_FOR_TRIGGER])
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
    if any(keyword in last_ai_msg for keyword in P4_DETECTION_KEYWORDS):
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
                trigger = PromptTemplates.optimizer_trigger()
                st.session_state.messages.append({"role": "user", "content": trigger})
                st.rerun()

        with col2:
            if st.button("📄 Pular para Arquivo Final"):
                 trigger = PromptTemplates.skip_to_final_trigger()
                 st.session_state.messages.append({"role": "user", "content": trigger})
                 st.rerun()
