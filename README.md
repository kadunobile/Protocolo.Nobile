# 🎯 Nobile Career Protocol

**Aplicativo Python (Streamlit) de Estratégia de Carreira Executiva com Integração OpenAI**

## 📋 Visão Geral

O Nobile Career Protocol é uma plataforma avançada para análise e desenvolvimento de carreiras executivas, utilizando inteligência artificial GPT para fornecer insights estratégicos personalizados.

### ✨ Funcionalidades Principais

- **📄 Upload de PDF**: Carregue e analise currículos executivos
- **🔍 Diagnóstico Executivo Obrigatório**: Validação de perfil (Cargo/Salário R$20k+)
- **📊 Score ATS**: Cálculo detalhado de compatibilidade com sistemas de rastreamento
- **💼 Interrogatório de Métricas**: Sessão interativa de análise de KPIs e resultados
- **🎨 Dark Mode**: Interface moderna e profissional
- **🤖 Integração OpenAI**: Powered by GPT-4

## 🏗️ Arquitetura Modular

```
Protocolo.Nobile/
├── app.py              # UI Streamlit, Session State, Dark Mode, Sidebar
├── engine.py           # Lógica GPT e integrações OpenAI
├── prompts.py          # Templates de prompts centralizados
├── config.py           # Configurações e constantes
├── requirements.txt    # Dependências Python
├── .env.example        # Template de variáveis de ambiente
└── README.md          # Documentação
```

### 📦 Módulos

#### `app.py` - Interface do Usuário
- Configuração da página Streamlit
- Dark Mode CSS customizado
- Gerenciamento de Session State
- Sidebar com navegação de comandos
- Componentes interativos para cada funcionalidade

#### `engine.py` - Motor de Lógica
- Classe `CareerEngine` para integração OpenAI
- Métodos para diagnóstico executivo
- Cálculo de Score ATS
- Condução de interrogatório de métricas
- Validação de perfil executivo

#### `prompts.py` - Templates de Prompts
- Classe `PromptTemplates` com métodos estáticos
- Prompts para diagnóstico, ATS, métricas
- Modificadores de tom e formato
- Estrutura preparada para expansão

#### `config.py` - Configuração
- Constantes da aplicação
- Configurações OpenAI
- Chaves de Session State
- Comandos da sidebar

## 🚀 Instalação e Configuração

### Pré-requisitos

- Python 3.8 ou superior
- Conta OpenAI com API Key

### Passo a Passo

1. **Clone o repositório**
```bash
git clone https://github.com/kadunobile/Protocolo.Nobile.git
cd Protocolo.Nobile
```

2. **Instale as dependências**
```bash
pip install -r requirements.txt
```

3. **Configure as variáveis de ambiente (opcional)**
```bash
# Opção 1: Usar arquivo .env (recomendado para desenvolvimento)
cp .env.example .env

# Edite o arquivo .env e adicione sua chave OpenAI
# OPENAI_API_KEY=sk-sua-chave-aqui
```

**Nota**: Se você não configurar o arquivo `.env`, a aplicação solicitará a API Key via interface da sidebar durante a execução.

4. **Execute o aplicativo**
```bash
streamlit run app.py
```

5. **Acesse no navegador**
```
http://localhost:8501
```

## 📖 Como Usar

### 1️⃣ Upload de PDF
- Navegue para "📄 Upload PDF" na sidebar
- Carregue seu currículo executivo em formato PDF
- Visualize o conteúdo extraído
- Opcionalmente, extraia informações estruturadas

### 2️⃣ Diagnóstico Executivo (Obrigatório)
- Acesse "🔍 Diagnóstico Executivo"
- Preencha seu cargo atual
- Informe seu salário mensal (mínimo R$20.000)
- Gere o diagnóstico estratégico personalizado

### 3️⃣ Score ATS
- Com o PDF carregado, vá para "📊 Score ATS"
- Calcule o score de compatibilidade ATS
- Receba análise detalhada e recomendações

### 4️⃣ Interrogatório de Métricas
- Complete o diagnóstico primeiro
- Acesse "💼 Interrogatório de Métricas"
- Responda perguntas sobre KPIs e resultados
- Forneça métricas quantificáveis

## 🔧 Configuração Avançada

### Modelo GPT
Edite `config.py` para alterar o modelo:
```python
OPENAI_MODEL = "gpt-4"  # ou "gpt-3.5-turbo"
```

### Requisito de Salário
Ajuste o salário mínimo executivo:
```python
MIN_SALARY_REQUIREMENT = 20000  # R$ 20k+
```

## 🎨 Personalização

### Dark Mode
O tema dark está implementado via CSS no `app.py`. Personalize as cores editando o bloco `st.markdown()` com o `<style>`.

### Prompts
Adicione ou modifique prompts em `prompts.py`:
```python
@staticmethod
def seu_novo_prompt(params) -> str:
    return f"Seu prompt customizado com {params}"
```

## 📝 Expansão Futura

A arquitetura modular facilita expansões:

1. **Novos Prompts**: Adicione em `prompts.py`
2. **Nova Lógica**: Expanda métodos em `engine.py`
3. **Novas Features UI**: Adicione comandos em `config.py` e seções em `app.py`

### Estrutura Preparada Para:
- Análise de mercado comparativa
- Geração de planos de desenvolvimento
- Simulação de entrevistas
- Recomendação de networking
- Tracking de aplicações

## 🔐 Segurança

- **Nunca** commite o arquivo `.env` com suas chaves
- Use `.env.example` como template
- Mantenha sua `OPENAI_API_KEY` privada
- O `.gitignore` já está configurado para proteger dados sensíveis

## 🛠️ Tecnologias

- **Streamlit**: Framework de UI
- **OpenAI GPT-4**: Motor de IA
- **PyPDF2**: Processamento de PDF
- **Python-dotenv**: Gerenciamento de ambiente

## 📄 Licença

Este projeto está sob licença privada. Todos os direitos reservados.

## 👥 Contribuição

Este é um projeto privado. Para contribuir, entre em contato com o proprietário do repositório.

## 📞 Suporte

Para questões ou suporte, abra uma issue no repositório.

---

**Desenvolvido com ❤️ para executivos que buscam excelência em suas carreiras**