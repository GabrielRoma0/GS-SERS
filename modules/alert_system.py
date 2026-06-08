"""
alert_system.py
===============
Sistema de alertas e tomada de decisão automatizada.

Níveis de alerta:
  INFO    -> situação normal, apenas informativo
  AVISO   -> parâmetro se aproximando do limite, atenção necessária
  CRITICO -> limite ultrapassado, ação imediata requerida
  FALHA   -> módulo em falha, resposta automatizada ativada

Tomada de decisão:
  O sistema responde automaticamente a condições críticas,
  simulando um controlador de bordo autônomo.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class NivelAlerta(Enum):
    INFO    = "INFO"
    AVISO   = "AVISO"
    CRITICO = "CRITICO"
    FALHA   = "FALHA"


# Cores ANSI para o terminal
COR = {
    "INFO":     "\033[96m",    # Ciano
    "AVISO":    "\033[93m",    # Amarelo
    "CRITICO":  "\033[91m",    # Vermelho
    "FALHA":    "\033[95m",    # Magenta
    "RESET":    "\033[0m",
    "VERDE":    "\033[92m",
    "BRANCO":   "\033[97m",
    "CINZA":    "\033[90m",
    "NEGRITO":  "\033[1m",
}


@dataclass
class Alerta:
    modulo: str
    nivel: NivelAlerta
    mensagem: str
    valor_atual: float
    limite: float
    timestamp: str = ""
    resposta_automatica: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().strftime("%H:%M:%S")


def verificar_temperatura(modulo) -> list[Alerta]:
    """
    Verifica temperatura e gera alertas em cascata:
    - >85% do limite -> AVISO
    - >95% do limite -> CRÍTICO
    - Abaixo do mínimo -> CRÍTICO
    """
    alertas = []
    t = modulo.temp_operacional
    t_max = modulo.temp_maxima
    t_min = modulo.temp_minima

    # Limiar de aviso: 85% da faixa máxima
    limiar_aviso   = t_min + (t_max - t_min) * 0.85
    limiar_critico = t_min + (t_max - t_min) * 0.95

    if t > limiar_critico:
        alertas.append(Alerta(
            modulo=modulo.nome,
            nivel=NivelAlerta.CRITICO,
            mensagem=f"Temperatura CRÍTICA: {t:.1f}°C (máx: {t_max}°C)",
            valor_atual=t,
            limite=t_max,
            resposta_automatica="-> Ativando dissipadores de calor e reduzindo carga operacional em 30%"
        ))
    elif t > limiar_aviso:
        alertas.append(Alerta(
            modulo=modulo.nome,
            nivel=NivelAlerta.AVISO,
            mensagem=f"Temperatura elevada: {t:.1f}°C (limiar: {limiar_aviso:.1f}°C)",
            valor_atual=t,
            limite=limiar_aviso,
            resposta_automatica="-> Aumentando ventilação e monitorando próximos ciclos"
        ))
    elif t < t_min:
        alertas.append(Alerta(
            modulo=modulo.nome,
            nivel=NivelAlerta.CRITICO,
            mensagem=f"Temperatura ABAIXO DO MÍNIMO: {t:.1f}°C (mín: {t_min}°C)",
            valor_atual=t,
            limite=t_min,
            resposta_automatica="-> Ativando aquecedores de emergência"
        ))

    return alertas


def verificar_rendimento(modulo) -> list[Alerta]:
    """
    Rendimento abaixo de 80% indica degradação preocupante.
    Abaixo de 70% é crítico
    """
    alertas = []
    n = modulo.rendimento

    if n < 0.70:
        alertas.append(Alerta(
            modulo=modulo.nome,
            nivel=NivelAlerta.CRITICO,
            mensagem=f"Rendimento CRITICO: {n*100:.1f}% (mín seguro: 70%)",
            valor_atual=n,
            limite=0.70,
            resposta_automatica="-> Módulo sinalizado para manutenção de emergência, redundância ativada"
        ))
    elif n < 0.80:
        alertas.append(Alerta(
            modulo=modulo.nome,
            nivel=NivelAlerta.AVISO,
            mensagem=f"Rendimento reduzido: {n*100:.1f}% (ideal: ≥80%)",
            valor_atual=n,
            limite=0.80,
            resposta_automatica="-> Agendando manutenção preventiva"
        ))

    return alertas


def verificar_fator_potencia(modulo) -> list[Alerta]:
    """
    Fator de potência baixo = painéis solares sobrecarregados desnecessariamente.
    Conceito direto do CP01: baixo FP aumenta S (potência aparente) sem ganho útil.
    """
    alertas = []
    fp = modulo.fator_potencia

    if fp < 0.75:
        alertas.append(Alerta(
            modulo=modulo.nome,
            nivel=NivelAlerta.CRITICO,
            mensagem=f"Fator de Potência CRITICO: {fp:.3f} (mín: 0.75)",
            valor_atual=fp,
            limite=0.75,
            resposta_automatica="-> Ativando banco de capacitores de correção de FP"
        ))
    elif fp < 0.85:
        alertas.append(Alerta(
            modulo=modulo.nome,
            nivel=NivelAlerta.AVISO,
            mensagem=f"Fator de Potência baixo: {fp:.3f} (recomendado: ≥0.85)",
            valor_atual=fp,
            limite=0.85,
            resposta_automatica="-> Verificando carga reativa e ajustando compensação"
        ))

    return alertas


def verificar_comunicacao(modulo) -> list[Alerta]:
    if not modulo.comunicacao_ok:
        return [Alerta(
            modulo=modulo.nome,
            nivel=NivelAlerta.FALHA,
            mensagem="PERDA DE SINAL — link de comunicação interrompido",
            valor_atual=0,
            limite=1,
            resposta_automatica="-> Alternando para antena reserva e tentando reconexão automática"
        )]
    return []


def analisar_modulo_alertas(modulo) -> list[Alerta]:
    """
    Ponto de entrada principal: analisa um módulo completo
    e retorna todos os alertas detectados.
    """
    todos_alertas = []
    todos_alertas.extend(verificar_temperatura(modulo))
    todos_alertas.extend(verificar_rendimento(modulo))
    todos_alertas.extend(verificar_fator_potencia(modulo))
    todos_alertas.extend(verificar_comunicacao(modulo))

    # Registra no histórico do módulo
    for alerta in todos_alertas:
        modulo.historico_alertas.append(alerta)

    return todos_alertas


def status_geral_missao(todos_alertas: list[Alerta]) -> tuple[str, str]:
    """
    Retorna o status geral da missão baseado no pior alerta ativo.
    """
    if any(a.nivel == NivelAlerta.FALHA for a in todos_alertas):
        return "FALHA CRÍTICA", COR["CRITICO"]
    if any(a.nivel == NivelAlerta.CRITICO for a in todos_alertas):
        return "ATENÇÃO MÁXIMA", COR["CRITICO"]
    if any(a.nivel == NivelAlerta.AVISO for a in todos_alertas):
        return "MONITORANDO", COR["AVISO"]
    return "NOMINAL", COR["VERDE"]
