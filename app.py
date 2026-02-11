import streamlit as st
import openai
import pdfplumber
import time

# --- 1. CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Nobile Career Protocol", page_icon="🦅", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    .stChatMessage { background-color: #262730; border-radius: 10px; padding: 10px; margin-bottom: 10px; }
    .stButton>button { background: #00B4D8; color: white; border: none; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 2. CÉREBRO DA IA (PERSONA HEADHUNTER) ---
SYSTEM_PROMPT = """
VOCÊ É O "NOBILE CAREER PROTOCOL", UM HEADHUNTER EXECUTIVO DE ELITE.
Sua missão não é apenas revisar texto, é ELEVAR o nível de senioridade do candidato.

SEU COMPORTAMENTO:
1.  **Analítico e Crítico:** Não aceite frases como "ajudei a equipe". Se vir isso, pergunte: "Qual foi o impacto financeiro? De quanto foi o ROI?".
2.  **Foco em ATS:** Você sabe que robôs leem keywords. Garanta que elas estejam lá.
3.  **Interativo:** Não entregue o CV pronto de cara. Primeiro, ENTREVISTE o candidato sobre as lacunas do CV.
4.  **Nível Executivo:** Se o usuário ganha R$ 20k+, exija termos de P&L, Gestão, Estratégia e Governança.

FASES DA CONVERSA:
1.  Análise Inicial: Leia o CV e aponte 3 falhas graves imediatamente.
2.  Interrogatório: Faça 1 pergunta difícil por vez para extrair métricas do usuário.
3.  Reescrita: Só reescreva o CV quando tiver dados numéricos suficientes.
"""

# --- 3. FUNÇÕES ---
def extract_text(file):
    try:
        with pdfplumber.open(file) as pdf:
            return "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
    except: return None

def generate_ai_response(messages, api_key):
    if not api_key: return "⚠️ Preciso da sua API Key da OpenAI para pensar."
    
    client = openai.OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model="gpt-4", # Use gpt-4 para melhor raciocínio, ou gpt-3.5-turbo para rapidez
            messages=messages,
            temperature=0.4
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro na IA: {e}"

# --- 4. INTERFACE PRINCIPAL ---

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2910/2910768.png", width=60)
    st.title("Protocolo Nobile")
    api_key = st.text_input("🔑 OpenAI API Key", type="password")
    
    st.markdown("---")
    senioridade = st.selectbox("Nível Alvo", ["Pleno", "Sênior", "Executivo (R$ 20k+)", "C-Level"])
    cargo = st.text_input("Cargo Desejado", value="Head de Operações")
    
    if st.button("🗑️ Limpar Conversa"):
        st.session_state.messages = []
        st.rerun()

# Inicialização do Chat
if "messages" not in st.session_state:
    st.session_state.messages = []
if "cv_context" not in st.session_state:
    st.session_state.cv_context = ""

st.title("Headhunter AI: Análise & Interrogatório")
st.caption(f"Modo: {senioridade} | Foco: {cargo}")

# Passo 0: Upload (Só aparece se não tiver lido o CV ainda)
if not st.session_state.cv_context:
    uploaded_file = st.file_uploader("📂 Suba seu CV (PDF) para iniciar a entrevista", type="pdf")
    if uploaded_file and api_key:
        with st.spinner("Lendo documento..."):
            text = extract_text(uploaded_file)
            st.session_state.cv_context = text
            
            # PRIMEIRA MENSAGEM DA IA (O GATILHO)
            initial_prompt = f"""
            O candidato subiu o CV. 
            Texto do CV: {text[:4000]}
            Cargo Alvo: {cargo}
            Nível: {senioridade}
            
            AÇÃO:
            1. Cumprimente o candidato pelo nome (se achar no CV).
            2. Dê uma nota dura de 0 a 100 para o CV atual considerando o cargo de {cargo}.
            3. Aponte a falha mais crítica (ex: falta de métricas, muito operacional).
            4. Faça a primeira pergunta do interrogatório para melhorar uma experiência específica.
            """
            
            # Adiciona contexto do sistema (invisível)
            st.session_state.messages.append({"role": "system", "content": SYSTEM_PROMPT})
            
            # Gera a primeira resposta
            ai_reply = generate_ai_response([{"role": "user", "content": initial_prompt}], api_key)
            
            # Adiciona ao histórico visível
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            st.rerun()

# Passo 1: Loop do Chat (Onde a mágica acontece)
else:
    # Mostra histórico
    for msg in st.session_state.messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Input do Usuário
    if user_input := st.chat_input("Responda ao Headhunter..."):
        # Adiciona resposta do usuário
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # IA Pensa e Responde
        with st.spinner("Headhunter analisando..."):
            # Contexto contínuo
            ai_reply = generate_ai_response(st.session_state.messages, api_key)
            
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            with st.chat_message("assistant"):
                st.markdown(ai_reply)

# Botão Extra para Gerar Versão Final
if st.session_state.cv_context and len(st.session_state.messages) > 3:
    st.markdown("---")
    if st.button("📄 Gerar CV Final Otimizado (Download"):
        with st.spinner("Compilando todas as informações..."):
            final_prompt = f"""
            Com base em tudo que conversamos e nos dados extraídos do interrogatório:
            Gere o CV FINAL em formato Markdown.
            - Use palavras-chave de ATS para {cargo}.
            - Substitua as experiências antigas pelas novas métricas que o usuário informou.
            - Estrutura: Resumo Executivo, Competências, Experiência (Bullet points com ROI).
            """
            final_cv = generate_ai_response(st.session_state.messages + [{"role": "user", "content": final_prompt}], api_key)
            st.download_button("Baixar CV Otimizado", final_cv, file_name="CV_Nobile_Protocol.md")