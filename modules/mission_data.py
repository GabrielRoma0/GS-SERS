"""
mission_data.py
===============
Dados simulados dos módulos operacionais da missão espacial.

A missão possui 5 módulos principais:
  1. PROPULSÃO    — motores iônicos de manobra orbital
  2. COMUNICAÇÃO  — antenas e transmissores de dados
  3. SUPORTE VITAL— sistemas de ar, temperatura e pressão
  4. LABORATÓRIO  — equipamentos de pesquisa científica
  5. NAVEGAÇÃO    — computadores de bordo e sensores

Cada módulo tem parâmetros elétricos (rendimento, fator de potência),
temperatura operacional e status de comunicação simulados.

Os valores são inspirados nos exercícios reais do CP01 para manter
coerência com a disciplina.
"""

import random
import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ModuloEspacial:
    """Representa um módulo operacional da missão espacial."""
    nome: str
    p_util_kw: float          # Potência mecânica/útil que o módulo precisa entregar
    rendimento: float          # Eficiência do sistema (0 a 1)
    fator_potencia: float      # Qualidade da energia (0 a 1)
    temp_operacional: float    # Temperatura em °C
    temp_minima: float         # Limite mínimo seguro de temperatura
    temp_maxima: float         # Limite máximo seguro de temperatura
    comunicacao_ok: bool       # Status do link de comunicação
    ativo: bool = True         # Módulo ligado ou desligado
    tempo_operacao_h: float = 0.0  # Horas em operação
    historico_alertas: list = field(default_factory=list)

    # Series temporais para geracao de graficos
    hist_ciclos:      list = field(default_factory=list)
    hist_p_ativa:     list = field(default_factory=list)
    hist_temperatura: list = field(default_factory=list)
    hist_rendimento:  list = field(default_factory=list)
    hist_fator_pot:   list = field(default_factory=list)

    def registrar_historico(self, ciclo: int, p_ativa: float) -> None:
        """Salva os valores do ciclo atual nas series temporais."""
        self.hist_ciclos.append(ciclo)
        self.hist_p_ativa.append(p_ativa)
        self.hist_temperatura.append(self.temp_operacional)
        self.hist_rendimento.append(self.rendimento)
        self.hist_fator_pot.append(self.fator_potencia)

    def atualizar_simulacao(self):
        """
        Simula variações realistas nos parâmetros do módulo a cada ciclo.
        Usa ruído gaussiano para simular flutuações reais de hardware.
        """
        # Pequenas variações de temperatura (ruído de ±0.5°C)
        self.temp_operacional += random.gauss(0, 0.5)
        # Degradação muito lenta do rendimento ao longo do tempo
        self.rendimento = max(0.5, self.rendimento - random.uniform(0, 0.0002))
        # Variação pequena no fator de potência
        self.fator_potencia = min(1.0, max(0.5, self.fator_potencia + random.gauss(0, 0.005)))
        # Incrementa tempo de operação
        self.tempo_operacao_h += 1.0
        # Simula falha de comunicação rara (2% de chance por ciclo)
        self.comunicacao_ok = random.random() > 0.02


# ─── Definição dos módulos da missão ───────────────────────────────────────────

def criar_modulos_missao() -> list[ModuloEspacial]:
    """
    Instancia os 5 módulos da missão com parâmetros realistas.
    Os valores de P_util e rendimento são calibrados para serem
    coerentes com os exercícios do CP01.
    """
    return [
        ModuloEspacial(
            nome="PROPULSÃO",
            p_util_kw=8.0,      # Motor iônico: alta potência útil (ref: Questão 3 CP01 ≈ 8.62 kW)
            rendimento=0.88,
            fator_potencia=0.85,
            temp_operacional=72.0,
            temp_minima=10.0,
            temp_maxima=90.0,
            comunicacao_ok=True,
        ),
        ModuloEspacial(
            nome="COMUNICAÇÃO",
            p_util_kw=1.4,      # Transmissores: média potência (ref: Questão 1 CP01 ≈ 1.5 kW útil)
            rendimento=0.84,
            fator_potencia=0.82,
            temp_operacional=38.0,
            temp_minima=-5.0,
            temp_maxima=60.0,
            comunicacao_ok=True,
        ),
        ModuloEspacial(
            nome="SUPORTE VITAL",
            p_util_kw=2.4,      # Sistemas de vida: crítico (ref: Questão 2 CP01 ≈ bomba 2.716 kW)
            rendimento=0.91,
            fator_potencia=0.88,
            temp_operacional=22.0,
            temp_minima=15.0,
            temp_maxima=35.0,
            comunicacao_ok=True,
        ),
        ModuloEspacial(
            nome="LABORATÓRIO",
            p_util_kw=5.5,      # Equipamentos científicos (ref: Questão 4 CP01 ≈ Motor A/B)
            rendimento=0.86,
            fator_potencia=0.86,
            temp_operacional=24.0,
            temp_minima=10.0,
            temp_maxima=45.0,
            comunicacao_ok=True,
        ),
        ModuloEspacial(
            nome="NAVEGAÇÃO",
            p_util_kw=1.8,
            rendimento=0.92,
            fator_potencia=0.90,
            temp_operacional=30.0,
            temp_minima=0.0,
            temp_maxima=55.0,
            comunicacao_ok=True,
        ),
    ]
