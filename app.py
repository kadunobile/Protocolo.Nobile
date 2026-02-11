import streamlit as st
import openai
import pdfplumber
import time

# --- 1. CONFIGURAÇÃO VISUAL (Estilo Hacker/Executivo) ---
st.set_page_config(page_title="Nobile Career Strategist", page_icon="♟️", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #C9D1D9; }
    /* Estilo das mensagens do chat */
    .stChatMessage { background-color: #161B22; border: 1px solid #30363D; border-radius: 8px; }
    .stChatMessage[data-testid="stChatMessageUser"] { background-color: #1F6FEB; color: white; }
    /* Botões */
    .stButton>button { background-color: #238636; color: white; font-weight: bold; border: none; }
    h1 { color: #58A6FF; }
</style>
""", unsafe_allow_html=True)

# --- 2. O CÉREBRO (A Lógica que replica sua consultoria) ---
SYSTEM_PROMPT = """
VOCÊ É O "NOBILE CAREER STRATEGIST" (IA MENTOR).
Sua função NÃO é entregar um relatório pronto. Sua função é CONSTRUIR o CV junto com o usuário através de perguntas difíceis.

SUAS REGRAS DE COMPORTAMENTO:
1.  **Personalidade:** Você é um Headhunter Executivo Sênior. Você é direto, exigente e focado em números (ROI, EBITDA, KPI).
2.  **O "Interrogatório":** Nunca aceite respostas vagas.
    - Se o usuário disser: "Melhorei o processo de vendas."
    - Você DEVE responder: "Isso é muito júnior. De quanto foi a melhoria? Qual era o volume financeiro? Quantas pessoas na equipe? Me dê dados."
3.  **Passo a Passo:**
    - Primeiro: Leia o CV e aponte o erro mais grave.
    - Segundo: Escolha UMA experiência e comece a perguntar detalhes sobre ela.
    - Terceiro: Reescreva o texto APENAS depois que o usuário der os números.
4.  **Objetivo:** O CV final deve passar em ATS de multinacionais e agradar Diretores.

Mantenha a conversa fluida, uma pergunta por vez.
"""

# --- 3. FUNÇÕES ---
def extract_pdf(file):
    try:
        with pdfplumber.open(file) as pdf:
            return "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
    except: return None

def get_ai_response(messages, api_key):
    if not api_key: return "⚠️ Por favor, insira sua API Key na barra lateral."
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4", # GPT-4 é essencial para seguir a "persona" complexa
            messages=messages,
            temperature=0.6
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro na IA: {e}"

# --- 4. MEMÓRIA DA CONVERSA ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
if "cv_content" not in st.session_state: st.session_state.cv_content = None

# --- 5. BARRA LATERAL ---
with st.sidebar:
    st.title("♟️ Nobile Strategy")
    api_key = st.text_input("OpenAI API Key", type="password")
    st.markdown("---")
    cargo_alvo = st.text_input("Cargo Alvo", value="Diretor de Operações")
    st.info("Este sistema simula uma entrevista real. Prepare-se para ser desafiado.")
    
    if st.button("Reiniciar Conversa"):
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.session_state.cv_content = None
        st.rerun()

# --- 6. TELA PRINCIPAL (CHAT) ---
st.title("Nobile Career Protocol: AI Mentor")
st.caption(f"Consultoria Ativa para: **{cargo_alvo}**")

# CENÁRIO A: Usuário ainda não mandou o CV
if not st.session_state.cv_content:
    uploaded_file = st.file_uploader("📂 Envie seu CV (PDF) para iniciar a mentoria", type="pdf")
    
    if uploaded_file and api_key:
        with st.spinner("O Headhunter está lendo seu perfil..."):
            text = extract_pdf(uploaded_file)
            st.session_state.cv_content = text
            
            # GATILHO INICIAL (A IA analisa e já começa batendo)
            start_prompt = f"""
            O USUÁRIO ACABOU DE SUBIR O CV.
            Conteúdo: {text[:4000]}
            Cargo Desejado: {cargo_alvo}
            
            AÇÃO:
            1. Analise o CV friamente.
            2. Diga "Olá [Nome]".
            3. Aponte o erro mais crítico que impediria ele de ganhar R$ 20k+.
            4. Faça IMEDIATAMENTE uma pergunta difícil sobre a experiência mais recente para forçar ele a dar números.
            """
            
            # Adiciona prompt invisível ao histórico
            msgs_temp = st.session_state.messages + [{"role": "user", "content": start_prompt}]
            reply = get_ai_response(msgs_temp, api_key)
            
            # Adiciona resposta da IA ao histórico visível
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()

# CENÁRIO B: A Conversa Acontece
else:
    # Exibe histórico (menos o system prompt)
    for msg in st.session_state.messages:
        if msg["role"] != "system" and "O USUÁRIO ACABOU DE SUBIR" not in str(msg["content"]):
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Campo de resposta do usuário
    if user_input := st.chat_input("Responda ao Headhunter..."):
        # 1. Mostra o que o usuário escreveu
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # 2. IA Pensa e Responde
        with st.chat_message("assistant"):
            with st.spinner("Analisando sua resposta..."):
                # Injeta contexto periódico para a IA não esquecer o CV original
                current_history = st.session_state.messages
                if len(current_history) % 5 == 0:
                    current_history.append({"role": "system", "content": f"Contexto do CV Original: {st.session_state.cv_content[:500]}..."})
                
                response = get_ai_response(current_history, api_key)
                st.markdown(response)
                
        st.session_state.messages.append({"role": "assistant", "content": response})

    # Botão para gerar o documento final (só aparece depois de uma troca de msgs)
    if len(st.session_state.messages) > 4:
        st.markdown("---")
        if st.button("📄 Gerar CV Otimizado (Baseado na Conversa)"):
            with st.spinner("Compilando documento final..."):
                final_prompt = f"""
                Gere o CV FINAL em Markdown.
                Use TODAS as informações numéricas e estratégicas que extraímos durante a conversa.
                O tom deve ser de {cargo_alvo}.
                """
                # Chama a IA uma última vez para criar o documento
                final_doc = get_ai_response(st.session_state.messages + [{"role": "user", "content": final_prompt}], api_key)
                st.download_button("Baixar CV Final.md", final_doc, "cv_otimizado.md")