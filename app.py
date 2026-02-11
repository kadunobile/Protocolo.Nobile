import streamlit as st
import openai
import pdfplumber
import json
import time

# --- 1. CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Nobile CV Auditor", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .step-card { 
        background-color: #161b22; border: 1px solid #30363d; 
        padding: 20px; border-radius: 10px; margin-bottom: 20px; 
    }
    .highlight { color: #58a6ff; font-weight: bold; }
    .success { color: #238636; }
    .warning { color: #d29922; }
    h1, h2, h3 { font-family: 'Segoe UI', sans-serif; }
</style>
""", unsafe_allow_html=True)

# --- 2. CLASSE DE CONTROLE DE FLUXO ---
class CVFlow:
    def __init__(self):
        if "step" not in st.session_state: st.session_state.step = 0
        if "cv_text" not in st.session_state: st.session_state.cv_text = ""
        if "history" not in st.session_state: st.session_state.history = []
        if "final_cv_parts" not in st.session_state: st.session_state.final_cv_parts = {}

    @staticmethod
    def extract_text(file):
        with pdfplumber.open(file) as pdf:
            return "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])

    @staticmethod
    def call_gpt(messages, api_key, model="gpt-4"):
        if not api_key: return "⚠️ API Key não encontrada."
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.4
        )
        return response.choices[0].message.content

# --- 3. PROMPTS DO SISTEMA (A LÓGICA PASSO A PASSO) ---
def get_analysis_prompt(cv_text, cargo):
    return f"""
    ATUE COMO: Headhunter Executivo Especialista em ATS.
    CONTEXTO: O usuário quer um CV para: {cargo}.
    CV ORIGINAL: {cv_text[:3000]}
    
    SUA TAREFA AGORA (PASSO 1):
    Analise o CV e identifique as 3 experiências profissionais mais recentes.
    Retorne APENAS um JSON (sem markdown) com esta estrutura exata:
    {{
        "experiencias": ["Empresa A - Cargo A", "Empresa B - Cargo B", "Empresa C - Cargo C"],
        "resumo_atual": "O resumo que está no CV",
        "falhas_gerais": ["Falha 1", "Falha 2"]
    }}
    """

def get_critique_prompt(experiencia_texto, cargo):
    return f"""
    Você está auditando a experiência: "{experiencia_texto}" para a vaga de {cargo}.
    
    PROBLEMA: O texto está fraco, operacional e sem números.
    
    AÇÃO:
    1. Liste 3 palavras-chave de ATS que FALTAM neste trecho.
    2. Faça UMA pergunta direta para extrair um indicador numérico (ROI, KPI, %, R$) que prove sucesso nesta função.
    3. Não reescreva ainda. Apenas critique e pergunte.
    """

def get_rewrite_prompt(experiencia_antiga, resposta_usuario, cargo):
    return f"""
    CONTEXTO: Vaga {cargo}.
    TEXTO ORIGINAL: {experiencia_antiga}
    INPUT DO USUÁRIO (O DADO NOVO): {resposta_usuario}
    
    TAREFA:
    Reescreva este bloco de experiência em Bullet Points de Alta Performance (Google XYZ Formula).
    Use verbos de ação fortes. Inclua as palavras-chave. Integre o número que o usuário passou.
    """

# --- 4. INTERFACE ---
flow = CVFlow()

with st.sidebar:
    st.title("🛡️ The Gauntlet")
    api_key = st.text_input("OpenAI API Key", type="password")
    cargo_target = st.text_input("Cargo Alvo", value="Gerente de Projetos")
    if st.button("Reiniciar Auditoria"):
        st.session_state.step = 0
        st.session_state.history = []
        st.rerun()

st.title("Auditoria de Carreira: Validação Passo a Passo")

# --- MÁQUINA DE ESTADOS ---

# ESTADO 0: UPLOAD
if st.session_state.step == 0:
    st.info("Passo 1: Diagnóstico Inicial")
    uploaded_file = st.file_uploader("Suba o CV 'Ruim' (PDF)", type="pdf")
    
    if uploaded_file and api_key:
        with st.spinner("Mapeando estrutura do CV..."):
            text = flow.extract_text(uploaded_file)
            st.session_state.cv_text = text
            
            # Chama a IA para estruturar o CV em blocos
            analysis_json = flow.call_gpt([
                {"role": "system", "content": "Você é um parser JSON."},
                {"role": "user", "content": get_analysis_prompt(text, cargo_target)}
            ], api_key)
            
            try:
                # Limpeza básica para garantir JSON válido
                analysis_json = analysis_json.replace("```json", "").replace("```", "")
                data = json.loads(analysis_json)
                st.session_state.structure = data
                st.session_state.step = 1 # Avança para o próximo passo
                st.rerun()
            except:
                st.error("Ocorreu um erro ao ler o CV. Tente novamente.")

# ESTADO 1: RESUMO EXECUTIVO
elif st.session_state.step == 1:
    st.markdown("### 📝 Passo 2: Otimizando o Resumo")
    st.warning("Diagnóstico da IA: " + str(st.session_state.structure['falhas_gerais']))
    
    if "msg_resumo" not in st.session_state:
        prompt = f"Critique este resumo para a vaga de {cargo_target}: {st.session_state.structure['resumo_atual']}. O que falta? Pergunte o diferencial do candidato."
        st.session_state.msg_resumo = flow.call_gpt([{"role": "user", "content": prompt}], api_key)
    
    with st.chat_message("assistant"):
        st.write(st.session_state.msg_resumo)
        
    resposta = st.chat_input("Responda à IA sobre seu resumo...")
    if resposta:
        with st.spinner("Reescrevendo resumo..."):
            novo_resumo = flow.call_gpt([
                {"role": "user", "content": f"Resumo Antigo: {st.session_state.structure['resumo_atual']}. Input: {resposta}. Reescreva o resumo em 1 parágrafo matador."}
            ], api_key)
            st.session_state.final_cv_parts['resumo'] = novo_resumo
            st.session_state.step = 2
            st.rerun()

# ESTADO 2, 3, 4...: LOOP DAS EXPERIÊNCIAS
elif st.session_state.step >= 2 and st.session_state.step < 2 + len(st.session_state.structure['experiencias']):
    idx = st.session_state.step - 2
    exp_atual = st.session_state.structure['experiencias'][idx]
    
    st.markdown(f"### 💼 Passo {st.session_state.step + 1}: Validando Experiência {idx + 1}")
    st.info(f"Foco: **{exp_atual}**")
    
    # Gera a crítica apenas uma vez por step
    step_key = f"critica_exp_{idx}"
    if step_key not in st.session_state:
        st.session_state[step_key] = flow.call_gpt([{"role": "user", "content": get_critique_prompt(exp_atual, cargo_target)}], api_key)
    
    with st.chat_message("assistant"):
        st.markdown(st.session_state[step_key])
        
    resposta_exp = st.chat_input(f"Responda sobre {exp_atual}...")
    
    if resposta_exp:
        with st.spinner(f"Otimizando Experiência {idx+1}..."):
            nova_exp = flow.call_gpt([{"role": "user", "content": get_rewrite_prompt(exp_atual, resposta_exp, cargo_target)}], api_key)
            st.session_state.final_cv_parts[f'exp_{idx}'] = nova_exp
            st.success("✅ Experiência Otimizada!")
            st.markdown(nova_exp)
            time.sleep(2) # Pausa dramática para leitura
            st.session_state.step += 1
            st.rerun()

# ESTADO FINAL: GERAÇÃO
else:
    st.balloons()
    st.title("💎 Seu CV de Elite está Pronto")
    
    full_cv = f"""
    # {cargo_target} - CV Otimizado
    
    ## RESUMO PROFISSIONAL
    {st.session_state.final_cv_parts.get('resumo', '')}
    
    ## EXPERIÊNCIA PROFISSIONAL
    """
    
    for i in range(len(st.session_state.structure['experiencias'])):
        full_cv += f"\n\n{st.session_state.final_cv_parts.get(f'exp_{i}', '')}"
        
    st.markdown(full_cv)
    st.download_button("Baixar CV Final.md", full_cv, "cv_final_nobile.md")