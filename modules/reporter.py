"""
reporter.py
===========
Gera relatórios em arquivo .txt ao final de cada sessão de monitoramento.
Salva o histórico de alertas e o resumo energético da missão.
"""

from datetime import datetime
import os
from modules.energy_calc import (
    calcular_potencia_ativa,
    calcular_potencia_aparente,
    calcular_potencia_reativa,
    calcular_consumo_energia,
)


def gerar_relatorio(modulos: list, ciclos_executados: int, caminho: str = "reports/relatorio_missao.txt") -> None:
    """Salva um relatório completo da sessão de monitoramento."""
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linhas = []

    linhas.append("=" * 70)
    linhas.append("   RELATÓRIO DE MONITORAMENTO ENERGÉTICO — MISSÃO ORBITAL")
    linhas.append("=" * 70)
    linhas.append(f"  Gerado em    : {agora}")
    linhas.append(f"  Ciclos exec. : {ciclos_executados}")
    linhas.append("")

    total_alertas = sum(len(m.historico_alertas) for m in modulos)
    linhas.append(f"  Total de alertas registrados: {total_alertas}")
    linhas.append("")

    for m in modulos:
        p = calcular_potencia_ativa(m.p_util_kw, m.rendimento)
        s = calcular_potencia_aparente(p, m.fator_potencia)
        q = calcular_potencia_reativa(s, p)

        linhas.append(f"  MÓDULO: {m.nome}")
        linhas.append(f"  {'─'*50}")
        linhas.append(f"    P Ativa   : {p:.4f} kW")
        linhas.append(f"    S Aparente: {s:.4f} kVA")
        linhas.append(f"    Q Reativa : {q:.4f} kvar")
        linhas.append(f"    Rendimento: {m.rendimento*100:.1f}%")
        linhas.append(f"    Fator Pot.: {m.fator_potencia:.3f}")
        linhas.append(f"    Temperatura: {m.temp_operacional:.1f}°C")
        linhas.append(f"    Uptime: {m.tempo_operacao_h:.0f}h")

        if m.historico_alertas:
            linhas.append(f"    Alertas ({len(m.historico_alertas)}):")
            for a in m.historico_alertas[-5:]:  # últimos 5
                linhas.append(f"      [{a.timestamp}] {a.nivel.value}: {a.mensagem}")
        linhas.append("")

    linhas.append("=" * 70)
    linhas.append("  FIM DO RELATÓRIO")
    linhas.append("=" * 70)

    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))

    print(f"\n  ✓ Relatório salvo em: {caminho}")
