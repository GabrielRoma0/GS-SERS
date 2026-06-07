"""
energy_calc.py
==============
Módulo de cálculos elétricos para o sistema de monitoramento espacial.

Conceitos de Consumo e Demanda:
  P = P_util / rendimento      → Potência Ativa (kW)
  S = P / fator_de_potência    → Potência Aparente (kVA)
  Q = √(S² - P²)               → Potência Reativa (kvar)

Por que isso importa na missão espacial?
  - Potência Ativa (P): energia realmente consumida pelo módulo para funcionar
  - Potência Aparente (S): carga total exigida dos painéis solares
  - Potência Reativa (Q): energia "desperdiçada" em campos eletromagnéticos
  - Fator de Potência: quanto do total é aproveitado (ideal = 1.0)
  - Rendimento: eficiência do equipamento (ideal = 1.0 = 100%)
"""

import math


def calcular_potencia_ativa(p_util: float, rendimento: float) -> float:
    """
    P = P_util / rendimento
    """
    if rendimento <= 0 or rendimento > 1:
        raise ValueError(f"Rendimento inválido: {rendimento}. Deve ser entre 0 e 1.")
    return round(p_util / rendimento, 4)


def calcular_potencia_aparente(p_ativa: float, fator_potencia: float) -> float:
    """
    S = P / FP
    """
    if fator_potencia <= 0 or fator_potencia > 1:
        raise ValueError(f"Fator de potência inválido: {fator_potencia}. Deve ser entre 0 e 1.")
    return round(p_ativa / fator_potencia, 4)


def calcular_potencia_reativa(s: float, p: float) -> float:
    """
    Q = √(S² - P²)
    """
    val = (s ** 2) - (p ** 2)
    if val < 0:
        return 0.0
    return round(math.sqrt(val), 4)


def calcular_eficiencia_energetica(p_ativa: float, s_aparente: float) -> float:
    """
    FP = P / S  (deve ser próximo de 1.0 para boa eficiência)
    """
    if s_aparente == 0:
        return 0.0
    return round(p_ativa / s_aparente, 4)


def calcular_consumo_energia(p_ativa_kw: float, horas: float) -> float:
    """
    E = P × t
    """
    return round(p_ativa_kw * horas, 4)


def analisar_modulo(nome: str, p_util: float, rendimento: float, fator_potencia: float) -> dict:
    """
    Análise completa de um módulo: calcula todas as grandezas elétricas
    e retorna um dicionário com os resultados e diagnóstico.
    """
    p = calcular_potencia_ativa(p_util, rendimento)
    s = calcular_potencia_aparente(p, fator_potencia)
    q = calcular_potencia_reativa(s, p)

    return {
        "nome": nome,
        "p_util_kw": p_util,
        "rendimento": rendimento,
        "fator_potencia": fator_potencia,
        "P_ativa_kW": p,
        "S_aparente_kVA": s,
        "Q_reativa_kvar": q,
    }
