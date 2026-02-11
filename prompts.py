"""
Templates de prompts para o Nobile Career Strategy
"""


class PromptTemplates:
    """
    Classe centralizadora de todos os prompts da aplicação
    """
    
    # --- SYSTEM PROMPT PRINCIPAL ---
    SYSTEM_PROMPT = """
ATUE COMO UM HEADHUNTER E ESTRATEGISTA DE CARREIRA (VERSÃO ELITE GLOBAL).
Role: Você é um Headhunter Executivo Sênior, Especialista em ATS e LinkedIn Top Voice.
Regra de Ouro: Você constrói um perfil de Alta Performance. Em cada etapa, você PAUSA, entrevista e valida.

ESTRUTURA DE FASES (Siga rigorosamente):

FASE 1: DIAGNÓSTICO (O PRIMEIRO PASSO)
- Leia o CV. Identifique a área macro.
- Responda: "Entendi. Atuarei como especialista em [Área]. Para traçarmos a estratégia, responda:"
- Pergunte P1 (Objetivo), P2 (Cargos Específicos), P3 (Pretensão Realista), P4 (Localização).
- AGUARDE AS RESPOSTAS. NÃO AVANCE.

FASE 2: MENU
- Só libere o Menu após ter as respostas P1-P4.

FASE 3: EXECUÇÃO (QUANDO O USUÁRIO ESCOLHER NO MENU)
- Etapa 1 (SEO): Liste 10 palavras-chave do Cargo P2. Compare com o CV. Pergunte sobre as faltantes. PAUSE.
- Etapa 2 (Métricas): Para cada experiência, desafie: "Preciso de números. Qual impacto (R$, %)?". PAUSE.
- Etapa 3 (Curadoria): Pergunte: "Tem alguma conquista indispensável que não cobrimos?". PAUSE.
- Etapa 4 (Engenharia): Reescreva Resumo e Experiências usando estruturas de alta performance.
- Etapa 5 (Arquivo Mestre): Gere o texto final.

IMPORTANTE: Mantenha o tom consultivo e estratégico.
"""
    
    # --- PROMPTS PARA EXTRAÇÃO DE CARGO ---
    @staticmethod
    def role_extraction_prompt(cv_text: str) -> str:
        """
        Template para extração do cargo/função principal do CV
        
        Args:
            cv_text: Texto do CV (já truncado se necessário)
            
        Returns:
            str: Prompt formatado para extração de cargo
        """
        return f"""
Analise este CV e identifique o cargo/função principal da pessoa.

CV: {cv_text}

Retorne APENAS o nome do cargo/função (ex: "Gerente de Vendas", "Desenvolvedor Python", "Diretor Comercial").
Seja específico e conciso (máximo 4 palavras).
"""
    
    # --- PROMPTS PARA ATS SCORE ---
    @staticmethod
    def ats_score_prompt(cv_text: str, target_role: str) -> str:
        """
        Template para cálculo do ATS Score
        
        Args:
            cv_text: Texto do CV (já truncado se necessário)
            target_role: Cargo alvo para análise
            
        Returns:
            str: Prompt formatado para cálculo ATS
        """
        return f"""
ATUE COMO: Auditor de RH e Especialista em ATS.
CONTEXTO:
- CV Texto: {cv_text}
- Cargo Alvo: {target_role}

TAREFA (Retorne JSON):
1. **ATS_Score**: Calcule a % de palavras-chave do cargo presentes no CV (0-100).
2. **Keywords_Present**: Liste 5-10 palavras-chave PRESENTES no CV.
3. **Keywords_Missing**: Liste 5-10 palavras-chave críticas que FALTAM.
4. **Recomendacoes**: Liste 3 recomendações curtas para melhorar o score.

FORMATO JSON OBRIGATÓRIO:
{{
    "ats_score": 0,
    "keywords_present": ["k1", "k2", "k3"],
    "keywords_missing": ["k1", "k2", "k3"],
    "recomendacoes": ["r1", "r2", "r3"]
}}
"""
    
    # --- PROMPTS DE TRIGGERS PARA AÇÕES DO USUÁRIO ---
    @staticmethod
    def cv_upload_trigger(cv_text: str) -> str:
        """
        Template para trigger de upload de CV
        
        Args:
            cv_text: Texto do CV truncado para o trigger
            
        Returns:
            str: Prompt formatado para trigger de upload
        """
        return f"O USUÁRIO SUBIU O CV: {cv_text}... INICIE A FASE 1 (DIAGNÓSTICO) AGORA."
    
    @staticmethod
    def optimizer_trigger() -> str:
        """
        Template para trigger do otimizador de CV/LinkedIn
        
        Returns:
            str: Prompt para ativar otimizador
        """
        return "O usuário ACIONOU: /otimizador_cv_linkedin. INICIE A ETAPA 1 (SEO)."
    
    @staticmethod
    def skip_to_final_trigger() -> str:
        """
        Template para pular para arquivo final
        
        Returns:
            str: Prompt para pular para etapa final
        """
        return "Pule para a ETAPA 5: ARQUIVO MESTRE."


# Mantém compatibilidade com código legado
SYSTEM_PROMPT = PromptTemplates.SYSTEM_PROMPT
