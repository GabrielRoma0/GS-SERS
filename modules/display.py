"""
display.py
==========
Módulo de visualização dos dados da missão no terminal.

Apresenta dashboards com barras de progresso ASCII, tabelas formatadas
e relatórios de alertas coloridos — tudo legível diretamente no terminal.
"""

from modules.alert_system import COR, NivelAlerta, status_geral_missao
from modules.energy_calc import (
    calcular_potencia_ativa,
    calcular_potencia_aparente,
    calcular_potencia_reativa,
    calcular_consumo_energia,
)


def barra_progresso(valor: float, maximo: float, tamanho: int = 20, invertido: bool = False) -> str:
    """
    Gera uma barra de progresso ASCII.
    invertido=True -> vermelho quando alto (ex: temperatura)
    """
    pct = min(valor / maximo, 1.0)
    preenchido = int(pct * tamanho)
    barra = "█" * preenchido + "░" * (tamanho - preenchido)

    if invertido:
        if pct > 0.90:
            cor = COR["CRÍTICO"]
        elif pct > 0.75:
            cor = COR["AVISO"]
        else:
            cor = COR["VERDE"]
    else:
        if pct < 0.60:
            cor = COR["CRÍTICO"]
        elif pct < 0.80:
            cor = COR["AVISO"]
        else:
            cor = COR["VERDE"]

    return f"{cor}[{barra}]{COR['RESET']} {pct*100:.0f}%"


def cabecalho_missao(ciclo: int, todos_alertas: list) -> None:
    status, cor_status = status_geral_missao(todos_alertas)
    largura = 70

    print(f"\n{COR['NEGRITO']}{'═'*largura}{COR['RESET']}")
    print(f"{COR['NEGRITO']}{'SISTEMA DE MONITORAMENTO ENERGÉTICO — MISSÃO ORBITAL':^{largura}}{COR['RESET']}")
    print(f"{'═'*largura}")
    print(f"  Ciclo de Monitoramento : {COR['BRANCO']}#{ciclo:04d}{COR['RESET']}")
    print(f"  Status Geral da Missão : {cor_status}{COR['NEGRITO']}{status}{COR['RESET']}")
    print(f"  Alertas Ativos         : {len(todos_alertas)}")
    print(f"{'─'*largura}")


def painel_modulo(modulo, alertas_modulo: list) -> None:
    """
    Exibe um painel completo de um módulo com:
    - Parâmetros elétricos calculados (P, S, Q)
    - Barras de temperatura e rendimento
    - Status de comunicação
    """
    p = calcular_potencia_ativa(modulo.p_util_kw, modulo.rendimento)
    s = calcular_potencia_aparente(p, modulo.fator_potencia)
    q = calcular_potencia_reativa(s, p)
    consumo_8h = calcular_consumo_energia(p, 8)

    # Determina cor do módulo baseado nos alertas
    tem_critico = any(a.nivel.value in ["CRÍTICO", "FALHA"] for a in alertas_modulo)
    tem_aviso   = any(a.nivel.value == "AVISO" for a in alertas_modulo)
    cor_mod = COR["CRÍTICO"] if tem_critico else (COR["AVISO"] if tem_aviso else COR["VERDE"])

    status_com = f"{COR['VERDE']}● ONLINE{COR['RESET']}" if modulo.comunicacao_ok else f"{COR['CRÍTICO']}✗ FALHA{COR['RESET']}"

    print(f"\n  {cor_mod}{COR['NEGRITO']}[ {modulo.nome} ]{COR['RESET']}  Comunicação: {status_com}  |  Uptime: {modulo.tempo_operacao_h:.0f}h")
    print(f"  {'─'*64}")

    # Grandezas elétricas
    print(f"  {'Grandeza Elétrica':<28} {'Valor':>12}   {'Nota'}")
    print(f"  {'·'*64}")
    print(f"  {'P_útil (potência entregue)':<28} {modulo.p_util_kw:>9.4f} kW   base do cálculo")
    print(f"  {'P_ativa (consumida da fonte)':<28} {p:>9.4f} kW   P = P_util / η")
    print(f"  {'S_aparente (carga total)':<28} {s:>9.4f} kVA  S = P / FP")
    print(f"  {'Q_reativa (desperdício)':<28} {q:>9.4f} kvar Q = √(S²−P²)")
    print(f"  {'Consumo estimado 8h':<28} {consumo_8h:>9.4f} kWh  E = P × t")
    print(f"  {'·'*64}")

    # Indicadores visuais
    b_temp = barra_progresso(modulo.temp_operacional, modulo.temp_maxima, invertido=True)
    b_rend = barra_progresso(modulo.rendimento, 1.0)
    b_fp   = barra_progresso(modulo.fator_potencia, 1.0)

    print(f"  Temperatura  {modulo.temp_operacional:>6.1f}°C  {b_temp}")
    print(f"  Rendimento   {modulo.rendimento*100:>6.1f}%   {b_rend}")
    print(f"  Fator Pot.   {modulo.fator_potencia:>6.3f}    {b_fp}")

    # Alertas do módulo
    if alertas_modulo:
        print(f"\n  {COR['NEGRITO']}Alertas:{COR['RESET']}")
        for alerta in alertas_modulo:
            cor = COR.get(alerta.nivel.value, COR["RESET"])
            print(f"    {cor}⚠ [{alerta.nivel.value}] {alerta.mensagem}{COR['RESET']}")
            print(f"    {COR['CINZA']}{alerta.resposta_automatica}{COR['RESET']}")


def resumo_energetico(modulos: list) -> None:
    """
    Exibe um resumo consolidado do consumo energético total da missão.
    Útil para avaliar se os painéis solares são suficientes.
    """
    total_p = 0.0
    total_s = 0.0
    total_q = 0.0

    for m in modulos:
        if m.ativo:
            p = calcular_potencia_ativa(m.p_util_kw, m.rendimento)
            s = calcular_potencia_aparente(p, m.fator_potencia)
            q = calcular_potencia_reativa(s, p)
            total_p += p
            total_s += s
            total_q += q

    fp_geral = (total_p / total_s) if total_s > 0 else 0

    print(f"\n  {'─'*64}")
    print(f"  {COR['NEGRITO']}BALANÇO ENERGÉTICO TOTAL DA MISSÃO{COR['RESET']}")
    print(f"  {'─'*64}")
    print(f"  P Total (Ativa)    : {total_p:>8.4f} kW")
    print(f"  S Total (Aparente) : {total_s:>8.4f} kVA  <- capacidade mínima dos painéis solares")
    print(f"  Q Total (Reativa)  : {total_q:>8.4f} kvar")
    print(f"  FP Geral da Missão : {fp_geral:>8.4f}   {' BOM' if fp_geral >= 0.85 else '⚠ BAIXO — painéis sobrecarregados!'}")
    print(f"  Consumo em 24h     : {total_p*24:>8.2f} kWh  <- energia mínima a gerar/dia")


def rodape(ciclo: int) -> None:
    print(f"\n{'═'*70}")
    print(f"  {COR['CINZA']}Pressione Ctrl+C para encerrar o monitoramento | Ciclo #{ciclo:04d}{COR['RESET']}")
    print(f"{'═'*70}\n")
