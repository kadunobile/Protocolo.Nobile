import streamlit as st
import openai
import pdfplumber
import pandas as pd
from collections import Counter
import re

# --- 1. CONFIGURAÇÃO VISUAL & CSS ---
st.set_page_config(
    page_title="Universal Career Protocol",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo Limpo e Profissional
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #E6E6E6; }
    h1, h2, h3 { font-family: 'Segoe UI', sans-serif; font-weight: 600; }
    .stButton>button { 
        width: 100%; border-radius: 6px; height: 45px; 
        font-weight: bold; background-color: #2563EB; color: white; border: none;
    }
    .stButton>button:hover { background-color: #1D4ED8; }
    .reportview-container .main .block-container { padding-top: 2rem; }
    .stAlert { background-color: #1F2937; border: 1px solid #374151; color: #E5E7EB; }
</style>
""", unsafe_allow_html=True)

# --- 2. CLASSE DE INTELIGÊNCIA (O CÉREBRO DINÂMICO) ---
class CareerBrain:
    def __init__(self, api_key):
        self.client = openai.OpenAI(api_key=api_key) if api_key else None

    def get_persona(self, nivel):
        """Define a personalidade da IA baseada na senioridade do usuário."""
        if nivel == "Estágio / Junior / Trainee":
            return """
            ATUE COMO: Um Mentor de Carreira e Recrutador de Talentos Jovens.
            FOCO: Identificar potencial de aprendizado (learning agility), formação acadêmica, projetos voluntários e soft skills (comunicação, proatividade).
            TOM: Encorajador, educativo e focado em estruturação básica.
            CRITÉRIO ATS: Valorize palavras-chave da formação e ferramentas básicas.
            """
        elif nivel == "Pleno / Sênior / Especialista":
            return """
            ATUE COMO: Um Recrutador Técnico Sênior e Headhunter Especializado.
            FOCO: Domínio técnico (Hard Skills), consistência de carreira, projetos complexos entregues e resolução de problemas.
            TOM: Profissional, direto e focado em competência técnica.
            CRITÉRIO ATS: Exige densidade de palavras-chave técnicas e ferramentas específicas do cargo.
            """
        else:  # Executivo / C-Level
            return """
            ATUE COMO: Um Headhunter Executivo de Retained Search (Korn Ferry/Egon Zehnder).
            FOCO: Resultados de Negócio (ROI, EBITDA), Gestão de Pessoas, Estratégia, Governança e Visão de Longo Prazo.
            TOM: Exigente, sofisticado e focado em números. Rejeite listas de tarefas operacionais.
            CRITÉRIO ATS: Busca termos de gestão, liderança e impacto financeiro.
            """

    def analyze_full_profile(self, text, role, level):
        if not self.client:
            return "Erro: Sem API Key."
        
        persona = self.get_persona(level)
        
        prompt = f"""
        {persona}
        
        ANALISE ESTE CURRÍCULO PARA A VAGA DE: {role}
        NÍVEL ESPERADO: {level}
        
        TEXTO DO CV:
        {text[:3000]}
        
        RETORNE UMA ANÁLISE ESTRUTURADA EM MARKDOWN:
        1. **Diagnóstico Geral (Nota 0-100):** Dê uma nota realista para o nível {level}.
        2. **O Que Falta (GAP Analysis):** Liste 3 pontos críticos que impediriam a contratação.
        3. **Palavras-Chave Ausentes:** Liste 5 keywords essenciais para {role} que não foram encontradas ou estão fracas.
        4. **Sugestão de Resumo:** Reescreva o parágrafo "Sobre/Resumo" para ser perfeito para a vaga.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Ou gpt-4-turbo
                messages=[
                    {"role": "system", "content": "Você é um assistente de carreira expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Erro na IA: {e}"

    def rewrite_experience(self, bullet_point, role, level):
        if not self.client:
            return "Erro: Sem API Key."
        
        persona = self.get_persona(level)
        prompt = f"""
        {persona}
        TAREFA: Reescreva esta experiência do CV para torná-la mais atrativa para uma vaga de {role}.
        TEXTO ORIGINAL: "{bullet_point}"
        
        REGRA:
        - Se for Junior: Destaque o aprendizado e a colaboração.
        - Se for Sênior: Destaque a autonomia e a complexidade técnica.
        - Se for Executivo: Destaque o impacto financeiro/estratégico.
        
        SAÍDA: Apenas a frase reescrita, sem explicações.
        """
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        return response.choices[0].message.content

# --- 3. FUNÇÕES AUXILIARES (LOCAIS) ---
def extract_pdf_text(file):
    try:
        with pdfplumber.open(file) as pdf:
            return "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
    except Exception:
        return ""

def get_top_words(text, n=10):
    # Simples contagem de palavras para dar um dado "duro" ao usuário
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    stopwords = ['para', 'com', 'que', 'uma', 'como', 'pela', 'está', 'fazer', 'trabalho', 'experiência', 'profissional']
    filtered = [w for w in words if w not in stopwords]
    return pd.DataFrame(Counter(filtered).most_common(n), columns=['Palavra', 'Frequência'])

# --- 4. INTERFACE DO USUÁRIO ---

# Sidebar: Configuração
st.sidebar.title("🧬 Universal Protocol")
api_key = st.sidebar.text_input("OpenAI API Key", type="password")
st.sidebar.markdown("---")

st.sidebar.subheader("Calibragem da IA")
nivel_senioridade = st.sidebar.select_slider(
    "Qual o nível da vaga?",
    options=["Estágio / Junior / Trainee", "Pleno / Sênior / Especialista", "Executivo / C-Level"]
)
cargo_alvo = st.sidebar.text_input("Cargo Alvo", value="Gerente de Projetos")

# Main Area
st.title("Otimizador de Currículo Universal")
st.markdown(f"Configurado para nível: **{nivel_senioridade}** | Cargo: **{cargo_alvo}**")

# Estado da Sessão
if "cv_text" not in st.session_state:
    st.session_state.cv_text = ""
if "analise_feita" not in st.session_state:
    st.session_state.analise_feita = None

# Passo 1: Upload
uploaded_file = st.file_uploader("Carregue seu CV (PDF)", type="pdf")

if uploaded_file:
    st.session_state.cv_text = extract_pdf_text(uploaded_file)
    
    # Exibe métricas rápidas (Sem gastar IA)
    col1, col2 = st.columns([1, 2])
    with col1:
        st.info(f"✅ Leitura Concluída: {len(st.session_state.cv_text)} caracteres.")
    with col2:
        df_words = get_top_words(st.session_state.cv_text)
        with st.expander("Ver palavras mais repetidas (Análise Fria)"):
            st.dataframe(df_words, use_container_width=True)

    # Passo 2: Ação da IA
    if api_key:
        brain = CareerBrain(api_key)
        
        tab_analise, tab_editor, tab_entrevista = st.tabs(["📊 Diagnóstico Completo", "✏️ Editor Assistido", "🎙️ Simulador"])
        
        with tab_analise:
            if st.button("🚀 Rodar Análise Profunda (IA)"):
                with st.spinner("A IA está lendo cada linha do seu CV..."): 
                    analise = brain.analyze_full_profile(st.session_state.cv_text, cargo_alvo, nivel_senioridade)
                    st.session_state.analise_feita = analise
            
            if st.session_state.analise_feita:
                st.markdown(st.session_state.analise_feita)
        
        with tab_editor:
            st.subheader("Reescrita Cirúrgica")
            st.write("Copie um ponto do seu CV que você acha fraco. A IA vai reescrever baseada no seu nível.")
            texto_original = st.text_area("Cole a frase aqui:", height=100)
            if st.button("✨ Melhorar Frase"):
                if texto_original:
                    with st.spinner("Reescrevendo..."):
                        nova_frase = brain.rewrite_experience(texto_original, cargo_alvo, nivel_senioridade)
                        st.success("Sugestão:")
                        st.code(nova_frase, language="markdown")
        
        with tab_entrevista:
            st.subheader("Prepare-se para a Entrevista")
            if st.button("Gerar Pergunta Desafiadora"):
                prompt_entrevista = f"Crie uma pergunta de entrevista difícil para um candidato a {cargo_alvo} nível {nivel_senioridade}, baseada no fato de que o CV dele menciona: {st.session_state.cv_text[:500]}..."
                
                # Chamada direta simples para pergunta
                try:
                    q = brain.client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "user", "content": prompt_entrevista}]
                    ).choices[0].message.content
                    st.info(f"🧑‍💼 Recrutador: {q}")
                except Exception as e:
                    st.error(f"Erro: {e}")
    
    else:
        st.warning("⚠️ Insira a API Key na barra lateral para liberar as funções de IA.")

else:
    st.info("👆 Comece enviando seu arquivo PDF acima.")