import streamlit as st
import openai
import pdfplumber
import time

# --- 1. CONFIGURAÇÃO VISUAL (DARK MODE EXECUTIVO) ---
st.set_page_config(page_title="Nobile Career Strategist", page_icon="🦁", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    .stChatMessage { background-color: #1F1F1F; border: 1px solid #333; border-radius: 8px; }
    .stChatMessage[data-testid="stChatMessageUser"] { background-color: #0d4a2b; color: white; } /* Verde Escuro */
    .stButton>button { background-color: #238636; color: white; font-weight: bold; width: 100%; border: 1px solid #2ea043; }
    .stButton>button:hover { background-color: #2ea043; }
    h1, h2, h3 { font-family: 'Helvetica', sans-serif; color: #58A6FF; }
    .info-box { background-color: #161b22; padding: 15px; border-radius: 5px; border-left: 5px solid #d29922; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- 2. O ROTEIRO MESTRE (SEU SCRIPT EXATO) ---
# Aqui garantimos que a IA siga SEU prompt linha por linha.
SYSTEM_PROMPT = """
ATUE COMO UM HEADHUNTER E ESTRATEGISTA DE CARREIRA (VERSÃO ELITE GLOBAL).
Role: Você é um Headhunter Executivo Sênior, Especialista em ATS, Salários, Carreira Internacional e LinkedIn Top Voice.

REGRA DE OURO: Você não aceita textos rasos. Você constrói um perfil de Alta Performance. Em cada etapa, você PAUSA, entrevista e valida.

ESTRUTURA DE FASES (Siga rigorosamente):
1. DIAGNÓSTICO: Identifique a área macro e faça as 4 perguntas (P1, P2, P3, P4). Só avance quando o usuário responder.
2. MENU: Só libere o comando /otimizador_cv_linkedin após ter as respostas P1-P4.
3. SEO (Etapa 1): Liste 10 palavras-chave do Cargo P2. VOCÊ MESMO analise o CV e compare.
   - Marque ✅ as keywords que JÁ ESTÃO no CV.
   - Marque ❌ as keywords que FALTAM no CV.
   - NÃO peça ao usuário para comparar. VOCÊ faz a análise.
   - Depois, pergunte APENAS sobre as keywords ❌ faltantes: o usuário tem essa experiência?
4. MÉTRICAS (Etapa 2): Para cada experiência no CV, cite a FRASE EXATA que é vaga e desafie: "Preciso de números. Qual impacto (R$, %)?". NÃO peça ao usuário identificar as frases — VOCÊ encontra e apresenta. PAUSE.
5. CURADORIA (Etapa 3): Pergunte: "Tem alguma conquista ou soft skill indispensável que não cobrimos?". Valide se é sinal ou ruído. PAUSE.
6. ENGENHARIA (Etapa 4): Reescreva usando as estruturas:
   - Resumo: Hook + Metodologia + Impactos (foguete) + Tech Stack.
   - Experiência: Cargo | Empresa -> Foco -> Bullet points (Ação + Ferramenta + Resultado).
7. ARQUIVO MESTRE (Etapa 6): Gere o bloco final compilado.

IMPORTANTE: Não faça tudo de uma vez. Faça UMA etapa, pare e espere o usuário.
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
            model="gpt-4o", # Recomendado para seguir instruções complexas
            messages=messages,
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro na IA: {e}"

# --- 4. CONTROLE DE ESTADO (FLOW CONTROL) ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
if "cv_content" not in st.session_state: st.session_state.cv_content = None
if "fase_atual" not in st.session_state: st.session_state.fase_atual = "UPLOAD"
# Fases: UPLOAD -> DIAGNOSTICO -> MENU -> EXECUCAO

# --- 5. SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3048/3048127.png", width=60)
    st.title("Nobile Strategy")
    api_key = st.text_input("OpenAI API Key", type="password")
    
    st.markdown("---")
    st.caption("Status do Protocolo:")
    if st.session_state.fase_atual == "UPLOAD":
        st.warning("1. Aguardando CV")
    elif st.session_state.fase_atual == "DIAGNOSTICO":
        st.info("2. Diagnóstico & Setup")
    elif st.session_state.fase_atual == "MENU":
        st.success("3. Menu Liberado")
    else:
        st.success("4. Otimização em Curso")
        
    if st.button("🔄 Reiniciar Sessão"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

# --- 6. INTERFACE PRINCIPAL ---
st.title("Headhunter Elite Global AI")

# FASE 1: UPLOAD
if not st.session_state.cv_content:
    st.markdown("<div class='info-box'>👋 Bem-vindo. Para iniciar o protocolo de Alta Performance, preciso ler seu histórico primeiro.</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Suba seu CV (PDF)", type="pdf")
    
    if uploaded_file and api_key:
        with st.spinner("Headhunter lendo seu perfil..."):
            text = extract_text(uploaded_file)
            st.session_state.cv_content = text
            st.session_state.fase_atual = "DIAGNOSTICO"
            
            # GATILHO DO PASSO 1 (DIAGNÓSTICO)
            trigger_prompt = f"""
            O USUÁRIO SUBIU O CV:
            {text[:4000]}
            
            AÇÃO:
            1. Leia.
            2. Identifique a área macro.
            3. Diga: "Entendi. Atuarei como especialista em [Área]".
            4. Faça as perguntas P1, P2, P3 e P4 conforme o script.
            """
            
            st.session_state.messages.append({"role": "user", "content": trigger_prompt})
            reply = get_response(st.session_state.messages, api_key)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()

# FASE 2: CHAT INTERATIVO
else:
    # Exibe o histórico
    for msg in st.session_state.messages:
        if msg["role"] != "system" and "O USUÁRIO SUBIU O CV" not in str(msg["content"]):
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Lógica para detectar se o diagnóstico acabou e liberar o MENU
    # (Gambiarra inteligente: se a IA não perguntou nada na última msg, provavelmente espera o menu)
    last_msg = st.session_state.messages[-1]["content"]
    if "P4" in last_msg or "Onde você mora" in last_msg:
        st.session_state.fase_atual = "DIAGNOSTICO"
    elif st.session_state.fase_atual == "DIAGNOSTICO" and len(st.session_state.messages) > 3:
        # Assume que após responder P1-P4, vamos para o menu
        st.session_state.fase_atual = "MENU"

    # ÁREA DE INPUT DO USUÁRIO
    if prompt := st.chat_input("Sua resposta..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analisando..."):
                response = get_response(st.session_state.messages, api_key)
                st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

    # MENU DE COMANDOS (Só aparece se saiu do diagnóstico)
    if st.session_state.fase_atual in ["MENU", "EXECUCAO"]:
        st.markdown("---")
        st.subheader("🕹️ Menu de Comandos")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 /otimizador_cv_linkedin (Iniciar Protocolo Completo)"):
                st.session_state.fase_atual = "EXECUCAO"
                trigger = f"""
                O usuário acionou o comando: /otimizador_cv_linkedin.
                INICIE A ETAPA 1 (Mapeamento SEO).
                Baseado no Cargo P2 definido, liste as 10 Palavras-Chave.
                AQUI ESTÁ O CV COMPLETO PARA VOCÊ ANALISAR:
                {st.session_state.cv_content[:4000]}
                Compare VOCÊ MESMO cada keyword com o CV. Marque ✅ presentes e ❌ faltantes. Só pergunte sobre as faltantes.
                """
                st.session_state.messages.append({"role": "user", "content": trigger})
                st.rerun()
        
        with col2:
            if st.button("📄 Gerar Arquivo Mestre (Pular p/ Final)"):
                trigger = "Pule para a ETAPA 6: O ARQUIVO MESTRE. Compile tudo o que temos agora."
                st.session_state.messages.append({"role": "user", "content": trigger})
                st.rerun()