import streamlit as st
import openai
import pdfplumber
import json

# --- 1. CONFIGURAÇÃO VISUAL (DASHBOARD) ---
st.set_page_config(page_title="Nobile Audit Report", page_icon="📊", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    .metric-container {
        background-color: #1E1E1E; border: 1px solid #333; padding: 20px; 
        border-radius: 8px; text-align: center; margin-bottom: 20px;
    }
    .metric-value { font-size: 2.5em; font-weight: bold; color: #4CAF50; }
    .metric-label { font-size: 1em; color: #AAA; }
    .alert-box {
        padding: 15px; border-radius: 5px; margin: 10px 0; border-left: 5px solid;
    }
    .alert-red { background-color: #2e0b0b; border-color: #ff4b4b; }
    .alert-green { background-color: #0e2e1b; border-color: #4CAF50; }
    h1, h2, h3 { font-family: 'Arial', sans-serif; color: #E0E0E0; }
    .stButton>button { width: 100%; border-radius: 5px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 2. LÓGICA DE ANÁLISE (Backend) ---
class AuditEngine:
    def __init__(self):
        if 'report_data' not in st.session_state: st.session_state.report_data = None
        if 'cv_text' not in st.session_state: st.session_state.cv_text = None

    def extract_text(self, file):
        try:
            with pdfplumber.open(file) as pdf:
                return "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
        except: return None

    def generate_report(self, cv_text, target_role, target_salary, api_key):
        if not api_key: return None
        client = openai.OpenAI(api_key=api_key)
        
        # Prompt Analítico (Gera JSON puro)
        prompt = f"""
        ATUE COMO: Auditor de RH e Especialista em ATS.
        CONTEXTO:
        - CV Texto: {cv_text[:3000]}
        - Cargo Alvo: {target_role}
        - Pretensão Salarial: {target_salary}
        
        TAREFA (Retorne JSON):
        1. **ATS_Score**: Calcule a % de palavras-chave do cargo presentes no CV (0-100).
        2. **Senioridade_Percebida**: O texto soa como Junior, Pleno, Senior ou Executivo?
        3. **Analise_Salarial**: O texto sustenta o salário de {target_salary}? (Sim/Não e motivo curto).
        4. **Keywords_Missing**: Liste 5 palavras-chave críticas que faltam.
        5. **Gaps**: Liste 3 erros técnicos no CV.
        
        FORMATO JSON OBRIGATÓRIO:
        {{
            "ats_score": 0,
            "senioridade_detectada": "...",
            "analise_salarial": {{ "compativel": true, "motivo": "..." }},
            "keywords_missing": ["k1", "k2", "k3", "k4", "k5"],
            "gaps": ["gap1", "gap2", "gap3"]
        }}
        """
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.2
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            st.error(f"Erro na análise: {e}")
            return None

    def rewrite_section(self, section_text, instruction, api_key):
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é um redator de currículos de elite."},
                {"role": "user", "content": f"Texto Original: {section_text}\nInstrução: {instruction}\nReescreva em Bullet Points executivos."}
            ]
        )
        return response.choices[0].message.content

# --- 3. INTERFACE (FRONTEND) ---
engine = AuditEngine()

with st.sidebar:
    st.title("📊 Auditoria Nobile")
    api_key = st.text_input("OpenAI API Key", type="password")
    st.divider()
    target_role = st.text_input("Cargo Alvo", value="Diretor Comercial")
    target_salary = st.text_input("Salário Alvo", value="R$ 25.000,00")
    
    if st.button("🔄 Resetar Tudo"):
        st.session_state.report_data = None
        st.session_state.cv_text = None
        st.rerun()

st.title(f"Relatório de Viabilidade: {target_role}")

# FASE 1: UPLOAD E GERAÇÃO DO REPORT
if not st.session_state.report_data:
    uploaded_file = st.file_uploader("Carregar CV (PDF) para Auditoria", type="pdf")
    
    if uploaded_file and api_key:
        if st.button("🔍 GERAR RELATÓRIO TÉCNICO"):
            with st.spinner("Auditando ATS, Senioridade e Salário..."):
                text = engine.extract_text(uploaded_file)
                st.session_state.cv_text = text
                
                report = engine.generate_report(text, target_role, target_salary, api_key)
                if report:
                    st.session_state.report_data = report
                    st.rerun()

# FASE 2: O DASHBOARD (SEU REPORT)
else:
    data = st.session_state.report_data
    
    # 2.1 - Métricas de Topo
    c1, c2, c3 = st.columns(3)
    
    with c1:
        # ATS Score
        score = data.get('ats_score', 0)
        color = "#4CAF50" if score > 70 else "#FF5252"
        st.markdown(f"""
        <div class="metric-container" style="border-color: {color};">
            <div class="metric-value" style="color: {color};">{score}%</div>
            <div class="metric-label">Score ATS Técnico</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        # Análise Salarial
        salario_data = data.get('analise_salarial', {})
        salario_ok = salario_data.get('compativel', False)
        senioridade = data.get('senioridade_detectada', 'N/A')
        icon = "✅" if salario_ok else "⚠️"
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value" style="font-size: 1.5em; color: white;">{icon} {senioridade}</div>
            <div class="metric-label">Senioridade Percebida</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        # Palavras Chave
        missing_kws = data.get('keywords_missing', [])
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value" style="font-size: 1.5em; color: #58A6FF;">{len(missing_kws)}</div>
            <div class="metric-label">Keywords Faltantes</div>
        </div>
        """, unsafe_allow_html=True)

    # 2.2 - Detalhamento (O Report Escrito)
    col_a, col_b = st.columns([2, 1])
    
    with col_a:
        st.subheader("📋 Diagnóstico Salarial")
        motivo = salario_data.get('motivo', 'Sem dados')
        if salario_ok:
            st.success(f"**Compatível:** {motivo}")
        else:
            st.error(f"**Risco:** {motivo}")
            
        st.subheader("🔧 Gaps Técnicos Identificados")
        gaps = data.get('gaps', [])
        for gap in gaps:
            st.warning(f"• {gap}")

    with col_b:
        st.subheader("🔑 Keywords Ausentes")
        for kw in missing_kws:
            st.code(kw, language="text")

    st.divider()

    # FASE 3: FERRAMENTAS DE OTIMIZAÇÃO (A Solução)
    st.header("🛠️ Menu de Otimização")
    st.caption("Use as ferramentas abaixo para corrigir os problemas apontados no relatório.")
    
    tab1, tab2 = st.tabs(["Otimizar Experiência (Salário)", "Otimizar Keywords (ATS)"])
    
    with tab1:
        st.write(f"**Problema:** Seu texto atual não justifica o salário de {target_salary}")
        user_exp = st.text_area("Cole aqui a experiência que deseja blindar:", height=150)
        roi_input = st.text_input("Qual foi o resultado numérico (ROI/KPI) dessa experiência?")
        
        if st.button("Reescrever para Nível Executivo"):
            if user_exp and roi_input:
                with st.spinner("Reescrevendo..."):
                    instruction = f"O usuário quer ganhar {target_salary}. Reescreva focando em ROI: {roi_input}. Cargo: {target_role}."
                    new_text = engine.rewrite_section(user_exp, instruction, api_key)
                    st.markdown("### Versão Executiva:")
                    st.code(new_text)

    with tab2:
        st.write("**Problema:** Faltam palavras-chave para o robô.")
        st.write(f"Keywords Alvo: {', '.join(missing_kws)}")
        resumo_atual = st.text_area("Cole seu Resumo/Sobre atual:", height=100)
        
        if st.button("Injetar Keywords no Resumo"):
            if resumo_atual:
                with st.spinner("Otimizando SEO..."):
                    instruction = f"Mantenha a essência, mas insira organicamente estas palavras: {', '.join(missing_kws)}."
                    new_summary = engine.rewrite_section(resumo_atual, instruction, api_key)
                    st.markdown("### Resumo Otimizado (ATS Ready):")
                    st.code(new_summary)
