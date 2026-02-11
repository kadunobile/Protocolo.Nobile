# 🚀 Quick Start Guide - Nobile Career Protocol

## Instalação Rápida (5 minutos)

### 1. Pré-requisitos
```bash
# Verifique se tem Python 3.8+
python --version

# Clone o repositório (se ainda não fez)
git clone https://github.com/kadunobile/Protocolo.Nobile.git
cd Protocolo.Nobile
```

### 2. Instale as Dependências
```bash
pip install -r requirements.txt
```

### 3. Configure a API Key da OpenAI
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env e adicione sua chave
# OPENAI_API_KEY=sk-sua-chave-aqui
```

### 4. Execute o Aplicativo
```bash
streamlit run app.py
```

### 5. Acesse no Navegador
Abra: http://localhost:8501

---

## 📋 Fluxo de Uso

### Ordem Recomendada:

1. **📄 Upload PDF** (Opcional, mas recomendado)
   - Faça upload do currículo executivo
   - Visualize o conteúdo extraído

2. **🔍 Diagnóstico Executivo** (OBRIGATÓRIO)
   - Preencha: Cargo Atual
   - Preencha: Salário Mensal (mínimo R$ 20.000)
   - Clique: "Gerar Diagnóstico"
   - Aguarde a análise estratégica

3. **📊 Score ATS** (Requer PDF)
   - Clique: "Calcular Score ATS"
   - Receba análise detalhada do currículo
   - Veja recomendações de melhoria

4. **💼 Interrogatório de Métricas** (Requer Diagnóstico)
   - Clique: "Iniciar Interrogatório"
   - Responda perguntas sobre KPIs
   - Forneça métricas quantificáveis
   - Continue o diálogo interativo

---

## 🎯 Dicas de Uso

### Para Melhores Resultados:

**No Diagnóstico:**
- Seja específico no cargo (ex: "CFO", "CEO", "Diretor Executivo de TI")
- Informe o salário real (sistema valida mínimo de R$ 20.000)

**No Score ATS:**
- Use um PDF bem formatado
- Inclua palavras-chave relevantes no currículo
- Tenha conquistas quantificadas

**No Interrogatório de Métricas:**
- Seja específico nos números
- Use percentuais e valores concretos
- Exemplos: "Aumentei receita em 35%", "Reduzi custos em R$ 2M"

---

## 🔧 Personalização

### Alterar o Modelo GPT:
Edite `config.py`:
```python
OPENAI_MODEL = "gpt-4"  # ou "gpt-3.5-turbo"
# Consulte a documentação da OpenAI para modelos disponíveis
```

### Ajustar Requisito de Salário:
Edite `config.py`:
```python
MIN_SALARY_REQUIREMENT = 30000  # Para R$ 30k
```

### Adicionar Novos Prompts:
Edite `prompts.py`:
```python
@staticmethod
def seu_novo_prompt(params) -> str:
    return f"Seu prompt aqui com {params}"
```

---

## ❓ Problemas Comuns

### "OPENAI_API_KEY not found"
- ✅ Verifique se criou o arquivo `.env`
- ✅ Verifique se adicionou a chave correta
- ✅ Reinicie o aplicativo

### "Salário abaixo do mínimo executivo"
- ✅ O sistema requer salário mínimo de R$ 20.000
- ✅ Ajuste em `config.py` se necessário

### PDF não carrega
- ✅ Certifique-se que é um PDF válido
- ✅ Tente um PDF mais simples primeiro
- ✅ Máximo 200MB por arquivo

---

## 🎨 Estrutura do Código

```
Protocolo.Nobile/
├── app.py              # Interface Streamlit (comece aqui)
├── engine.py           # Lógica GPT (modifique para mudar comportamento)
├── prompts.py          # Templates (customize os prompts)
├── config.py           # Configurações (ajuste constantes)
├── requirements.txt    # Dependências Python
└── .env               # Suas chaves (NÃO commitar!)
```

---

## 📞 Suporte

- Documentação completa: Veja `README.md`
- Issues: Use o GitHub Issues
- Código limpo e modular para fácil manutenção

---

**Desenvolvido com ❤️ | Powered by OpenAI GPT-4**
