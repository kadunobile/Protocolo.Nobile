"""
Nobile Career Protocol - Main Streamlit Application
Executive Career Strategy App with Dark Mode and OpenAI Integration
"""
import streamlit as st
from PyPDF2 import PdfReader
import config
from engine import CareerEngine

# Page Configuration
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Mode CSS
st.markdown("""
    <style>
    /* Dark Mode Theme */
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #262730;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #fafafa;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #1f77b4;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    
    .stButton>button:hover {
        background-color: #145a8a;
        border: none;
    }
    
    /* Text Input */
    .stTextInput>div>div>input {
        background-color: #262730;
        color: #fafafa;
    }
    
    /* File Uploader */
    [data-testid="stFileUploader"] {
        background-color: #262730;
        border-radius: 5px;
        padding: 1rem;
    }
    
    /* Success/Error/Warning boxes */
    .stSuccess, .stError, .stWarning, .stInfo {
        background-color: #262730;
        border-radius: 5px;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #262730;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Session State
def init_session_state():
    """Initialize all session state variables"""
    for key in config.SESSION_KEYS.values():
        if key not in st.session_state:
            if key == config.SESSION_KEYS["conversation_history"]:
                st.session_state[key] = []
            else:
                st.session_state[key] = None

# Initialize engine and session state
init_session_state()

try:
    engine = CareerEngine()
    engine_available = True
except ValueError as e:
    engine_available = False
    st.error(f"⚠️ {str(e)}")

# Main Title
st.title(f"{config.APP_ICON} {config.APP_TITLE}")
st.markdown("### Estratégia de Carreira Executiva com IA")
st.markdown("---")

# Sidebar Navigation
with st.sidebar:
    st.header("🎯 Comandos")
    st.markdown("---")
    
    # Command Selection
    selected_command = st.radio(
        "Selecione uma função:",
        options=list(config.SIDEBAR_COMMANDS.keys()),
        format_func=lambda x: config.SIDEBAR_COMMANDS[x],
        key="command_selector"
    )
    
    st.markdown("---")
    
    # Status Information
    st.subheader("📊 Status")
    
    # PDF Upload Status
    pdf_status = "✅" if st.session_state[config.SESSION_KEYS["pdf_uploaded"]] else "⏳"
    st.text(f"{pdf_status} PDF Carregado")
    
    # Diagnosis Status
    diagnosis_status = "✅" if st.session_state[config.SESSION_KEYS["diagnosis_complete"]] else "⏳"
    st.text(f"{diagnosis_status} Diagnóstico")
    
    # ATS Score Status
    ats_status = "✅" if st.session_state[config.SESSION_KEYS["ats_score"]] else "⏳"
    st.text(f"{ats_status} Score ATS")
    
    st.markdown("---")
    
    # Reset button
    if st.button("🔄 Resetar Sessão"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Main Content Area based on selected command
if not engine_available:
    st.warning("⚠️ Configure a OPENAI_API_KEY no arquivo .env para usar o aplicativo.")
    st.info("1. Copie o arquivo .env.example para .env\n2. Adicione sua chave da OpenAI\n3. Reinicie o aplicativo")

elif selected_command == "upload_pdf":
    st.header("📄 Upload do Currículo")
    st.markdown("Faça upload do seu currículo em formato PDF para análise.")
    
    uploaded_file = st.file_uploader(
        "Escolha um arquivo PDF",
        type="pdf",
        help="Carregue seu currículo executivo em PDF"
    )
    
    if uploaded_file is not None:
        try:
            # Read PDF
            pdf_reader = PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            st.session_state[config.SESSION_KEYS["pdf_content"]] = text
            st.session_state[config.SESSION_KEYS["pdf_uploaded"]] = True
            
            st.success("✅ PDF carregado com sucesso!")
            
            # Show preview
            with st.expander("👁️ Visualizar conteúdo extraído"):
                st.text_area("Texto extraído:", text, height=300)
            
            # Extract structured info
            if st.button("🔍 Extrair Informações Estruturadas"):
                with st.spinner("Processando..."):
                    structured_info = engine.extract_pdf_info(text)
                    st.markdown("### 📋 Informações Estruturadas")
                    st.markdown(structured_info)
                    
        except Exception as e:
            st.error(f"❌ Erro ao processar PDF: {str(e)}")

elif selected_command == "diagnosis":
    st.header("🔍 Diagnóstico Executivo")
    st.markdown("**Obrigatório:** Complete o diagnóstico para acessar outras funcionalidades.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        position = st.text_input(
            "Cargo Atual",
            value=st.session_state[config.SESSION_KEYS["current_position"]] or "",
            placeholder="Ex: CEO, CFO, Diretor Executivo"
        )
    
    with col2:
        salary = st.number_input(
            "Salário Mensal (R$)",
            min_value=0.0,
            value=float(st.session_state[config.SESSION_KEYS["current_salary"]] or 0.0),
            step=1000.0,
            format="%.2f"
        )
    
    if st.button("🚀 Gerar Diagnóstico"):
        if not position or salary <= 0:
            st.error("❌ Por favor, preencha todos os campos.")
        else:
            # Validate executive profile
            validation = engine.validate_executive_profile(position, salary)
            
            if not validation["is_valid"]:
                st.error(f"❌ {validation['message']}")
                st.info(f"💡 Este protocolo é destinado a executivos com salário acima de R$ {config.MIN_SALARY_REQUIREMENT:,.2f}")
            else:
                st.success(f"✅ {validation['message']}")
                
                with st.spinner("Gerando diagnóstico executivo..."):
                    diagnosis = engine.generate_diagnosis(position, salary)
                    
                    # Save to session state
                    st.session_state[config.SESSION_KEYS["current_position"]] = position
                    st.session_state[config.SESSION_KEYS["current_salary"]] = salary
                    st.session_state[config.SESSION_KEYS["diagnosis_complete"]] = diagnosis
                    
                    # Display diagnosis
                    st.markdown("### 📊 Diagnóstico Executivo")
                    st.markdown(diagnosis)
    
    # Show existing diagnosis if available
    if st.session_state[config.SESSION_KEYS["diagnosis_complete"]]:
        st.markdown("---")
        st.markdown("### 📊 Diagnóstico Atual")
        st.info(f"**Cargo:** {st.session_state[config.SESSION_KEYS['current_position']]}")
        st.info(f"**Salário:** R$ {st.session_state[config.SESSION_KEYS['current_salary']]:,.2f}")
        with st.expander("Ver diagnóstico completo"):
            st.markdown(st.session_state[config.SESSION_KEYS["diagnosis_complete"]])

elif selected_command == "ats_score":
    st.header("📊 Calculadora de Score ATS")
    st.markdown("Analise seu currículo e obtenha um score ATS profissional.")
    
    if st.session_state[config.SESSION_KEYS["pdf_uploaded"]] is not True:
        st.warning("⚠️ Por favor, faça upload do seu PDF primeiro.")
    else:
        if st.button("📈 Calcular Score ATS"):
            with st.spinner("Analisando currículo..."):
                result = engine.calculate_ats_score(
                    st.session_state[config.SESSION_KEYS["pdf_content"]]
                )
                
                st.session_state[config.SESSION_KEYS["ats_score"]] = result
                
                st.markdown("### 🎯 Resultado da Análise ATS")
                st.markdown(result["analysis"])
        
        # Show existing score if available
        if st.session_state[config.SESSION_KEYS["ats_score"]]:
            st.markdown("---")
            st.markdown("### 📊 Score ATS Atual")
            with st.expander("Ver análise completa"):
                st.markdown(st.session_state[config.SESSION_KEYS["ats_score"]]["analysis"])

elif selected_command == "metrics_interrogation":
    st.header("💼 Interrogatório de Métricas")
    st.markdown("Sessão interativa de perguntas sobre suas métricas e resultados executivos.")
    
    if not st.session_state[config.SESSION_KEYS["diagnosis_complete"]]:
        st.warning("⚠️ Por favor, complete o diagnóstico executivo primeiro.")
    else:
        position = st.session_state[config.SESSION_KEYS["current_position"]]
        
        st.info(f"💼 **Cargo em análise:** {position}")
        
        # Display conversation history
        if st.session_state[config.SESSION_KEYS["conversation_history"]]:
            st.markdown("### 💬 Histórico da Conversa")
            for msg in st.session_state[config.SESSION_KEYS["conversation_history"]]:
                if msg["role"] == "assistant":
                    st.markdown(f"**🤖 Interrogador:** {msg['content']}")
                elif msg["role"] == "user":
                    st.markdown(f"**👤 Você:** {msg['content']}")
            st.markdown("---")
        
        # Start or continue interrogation
        if not st.session_state[config.SESSION_KEYS["conversation_history"]]:
            if st.button("🎯 Iniciar Interrogatório"):
                with st.spinner("Preparando primeira pergunta..."):
                    first_question = engine.conduct_metrics_interrogation(
                        position=position,
                        context="Início da sessão de interrogatório de métricas",
                        conversation_history=None
                    )
                    
                    st.session_state[config.SESSION_KEYS["conversation_history"]].append({
                        "role": "assistant",
                        "content": first_question
                    })
                    st.rerun()
        else:
            # Show latest question
            latest_msg = st.session_state[config.SESSION_KEYS["conversation_history"]][-1]
            if latest_msg["role"] == "assistant":
                st.markdown("### 🤖 Pergunta Atual:")
                st.info(latest_msg["content"])
            
            # User response
            user_response = st.text_area(
                "Sua resposta:",
                placeholder="Digite sua resposta com métricas e resultados quantificáveis...",
                height=150
            )
            
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("📤 Enviar Resposta"):
                    if user_response:
                        # Add user response to history
                        st.session_state[config.SESSION_KEYS["conversation_history"]].append({
                            "role": "user",
                            "content": user_response
                        })
                        
                        # Get next question
                        with st.spinner("Processando resposta..."):
                            next_question = engine.conduct_metrics_interrogation(
                                position=position,
                                context="Continuação do interrogatório",
                                conversation_history=st.session_state[config.SESSION_KEYS["conversation_history"]]
                            )
                            
                            st.session_state[config.SESSION_KEYS["conversation_history"]].append({
                                "role": "assistant",
                                "content": next_question
                            })
                            st.rerun()
            
            with col2:
                if st.button("🔄 Reiniciar Interrogatório"):
                    st.session_state[config.SESSION_KEYS["conversation_history"]] = []
                    st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>🎯 Nobile Career Protocol | Powered by OpenAI GPT</p>
    </div>
    """,
    unsafe_allow_html=True
)
