"""
Gerenciamento de fases usando Finite State Machine (FSM) para o Nobile Career Strategy.
Substitui o sistema frágil de detecção por keywords por transições estruturadas.
"""

from enum import Enum
from typing import List, Dict, Any


class Phase(Enum):
    """Enum para representar as fases da aplicação"""
    UPLOAD = "UPLOAD"
    DIAGNOSTICO = "DIAGNOSTICO"
    DIAGNOSTICO_EM_ANDAMENTO = "DIAGNOSTICO_EM_ANDAMENTO"
    MENU = "MENU"
    EXECUCAO = "EXECUCAO"


class PhaseManager:
    """
    Gerencia as transições de fase da aplicação usando uma máquina de estados.
    
    Transições válidas:
    - UPLOAD → DIAGNOSTICO (quando CV é carregado)
    - DIAGNOSTICO → DIAGNOSTICO_EM_ANDAMENTO (quando perguntas P1-P4 são iniciadas)
    - DIAGNOSTICO_EM_ANDAMENTO → MENU (quando respostas P1-P4 são completadas)
    - MENU → EXECUCAO (quando usuário escolhe ação)
    - EXECUCAO → MENU (quando usuário retorna ao menu)
    """
    
    def __init__(self, initial_phase: Phase = Phase.UPLOAD):
        """
        Inicializa o gerenciador de fases.
        
        Args:
            initial_phase: Fase inicial (padrão: UPLOAD)
        """
        self.current_phase = initial_phase
        self._transition_log = []
        
    def can_transition_to(self, target_phase: Phase) -> bool:
        """
        Verifica se a transição para a fase alvo é válida.
        
        Args:
            target_phase: Fase de destino
            
        Returns:
            bool: True se a transição é válida, False caso contrário
        """
        valid_transitions = {
            Phase.UPLOAD: [Phase.DIAGNOSTICO],
            Phase.DIAGNOSTICO: [Phase.DIAGNOSTICO_EM_ANDAMENTO],
            Phase.DIAGNOSTICO_EM_ANDAMENTO: [Phase.MENU],
            Phase.MENU: [Phase.EXECUCAO],
            Phase.EXECUCAO: [Phase.MENU]
        }
        
        return target_phase in valid_transitions.get(self.current_phase, [])
    
    def transition_to(self, target_phase: Phase, reason: str = "") -> bool:
        """
        Realiza a transição para a fase alvo se for válida.
        
        Args:
            target_phase: Fase de destino
            reason: Motivo da transição (para log)
            
        Returns:
            bool: True se a transição foi realizada, False caso contrário
        """
        if self.can_transition_to(target_phase):
            old_phase = self.current_phase
            self.current_phase = target_phase
            self._transition_log.append({
                "from": old_phase.value,
                "to": target_phase.value,
                "reason": reason
            })
            return True
        return False
    
    def should_transition_from_upload(self, cv_content: Any) -> bool:
        """
        Verifica se deve transitar de UPLOAD para DIAGNOSTICO.
        
        Args:
            cv_content: Conteúdo do CV carregado
            
        Returns:
            bool: True se o CV foi carregado e a transição é válida
        """
        return (self.current_phase == Phase.UPLOAD and 
                cv_content is not None)
    
    def should_transition_to_diagnostico_em_andamento(self, messages: List[Dict]) -> bool:
        """
        Verifica se deve transitar de DIAGNOSTICO para DIAGNOSTICO_EM_ANDAMENTO.
        
        Critério: A IA enviou pelo menos 1 mensagem após o trigger inicial,
        indicando que o processo de diagnóstico foi iniciado.
        
        Args:
            messages: Lista de mensagens do chat
            
        Returns:
            bool: True se a transição é válida
        """
        if self.current_phase != Phase.DIAGNOSTICO:
            return False
        
        # Conta mensagens da IA (excluindo system e triggers técnicos)
        ai_messages = [
            msg for msg in messages 
            if msg["role"] == "assistant"
        ]
        
        # Se a IA já enviou pelo menos 1 mensagem, o diagnóstico está em andamento
        return len(ai_messages) >= 1
    
    def should_transition_to_menu(self, messages: List[Dict]) -> bool:
        """
        Verifica se deve transitar de DIAGNOSTICO_EM_ANDAMENTO para MENU.
        
        Critério: Houve troca suficiente de mensagens (indicando que as 4 perguntas
        foram feitas e respondidas). Usamos contagem mínima de mensagens como proxy.
        
        Args:
            messages: Lista de mensagens do chat
            
        Returns:
            bool: True se a transição é válida
        """
        if self.current_phase != Phase.DIAGNOSTICO_EM_ANDAMENTO:
            return False
        
        # Conta pares de mensagens user-assistant (excluindo system e triggers)
        user_messages = [
            msg for msg in messages 
            if msg["role"] == "user" and "O USUÁRIO SUBIU" not in str(msg["content"])
        ]
        
        assistant_messages = [
            msg for msg in messages 
            if msg["role"] == "assistant"
        ]
        
        # Esperamos pelo menos 4 respostas do usuário e 4 da IA
        # (P1, P2, P3, P4 + respostas)
        return len(user_messages) >= 4 and len(assistant_messages) >= 4
    
    def should_transition_to_execucao(self, last_user_message: str) -> bool:
        """
        Verifica se deve transitar de MENU para EXECUCAO.
        
        Critério: Usuário acionou um comando específico.
        
        Args:
            last_user_message: Última mensagem do usuário
            
        Returns:
            bool: True se a transição é válida
        """
        if self.current_phase != Phase.MENU:
            return False
        
        # Verifica se há trigger de execução na mensagem
        execution_triggers = ["ACIONOU:", "/otimizador", "ETAPA"]
        return any(trigger in last_user_message for trigger in execution_triggers)
    
    def update_phase(self, cv_content: Any = None, messages: List[Dict] = None) -> Phase:
        """
        Atualiza automaticamente a fase baseado no estado atual da aplicação.
        
        Args:
            cv_content: Conteúdo do CV (opcional)
            messages: Lista de mensagens do chat (opcional)
            
        Returns:
            Phase: Fase atual após a atualização
        """
        messages = messages or []
        
        # Verifica transições na ordem apropriada
        if self.should_transition_from_upload(cv_content):
            self.transition_to(Phase.DIAGNOSTICO, "CV carregado")
        
        elif self.should_transition_to_diagnostico_em_andamento(messages):
            self.transition_to(Phase.DIAGNOSTICO_EM_ANDAMENTO, "Diagnóstico iniciado")
        
        elif self.should_transition_to_menu(messages):
            self.transition_to(Phase.MENU, "Diagnóstico completo - menu disponível")
        
        # Transições para EXECUCAO são tratadas explicitamente no app
        # quando o usuário clica em um botão de comando
        
        return self.current_phase
    
    def get_phase_value(self) -> str:
        """
        Retorna o valor string da fase atual.
        
        Returns:
            str: Valor da fase atual
        """
        return self.current_phase.value
    
    def get_transition_log(self) -> List[Dict]:
        """
        Retorna o log de transições realizadas.
        
        Returns:
            List[Dict]: Lista de transições com from, to e reason
        """
        return self._transition_log.copy()
