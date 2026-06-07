"""
grafico.py
==========
Módulo de visualização gráfica com matplotlib.

Gera dois arquivos de imagem ao encerrar o monitoramento:
  1. graficos_missao.png  — painel com 5 gráficos de histórico por módulo
  2. balanco_final.png    — gráfico de barras do balanço energético final

Por que gráficos?
  Visualizar a evolução temporal de P, temperatura e FP ao longo dos ciclos
  permite identificar tendências de degradação que o dashboard instantâneo
  não revela — por exemplo, rendimento caindo consistentemente ao longo do
  tempo indica desgaste, mesmo que cada leitura isolada pareça aceitável.
"""

import os

try:
    import matplotlib
    matplotlib.use("Agg")   # backend sem janela — compatível com qualquer ambiente
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    MATPLOTLIB_OK = True
except ImportError:
    MATPLOTLIB_OK = False


# Paleta de cores por módulo (consistente em todos os gráficos)
CORES_MODULOS = {
    "PROPULSÃO":    "#e05c5c",
    "COMUNICAÇÃO":  "#5c9be0",
    "SUPORTE VITAL":"#5ce08a",
    "LABORATÓRIO":  "#e0b85c",
    "NAVEGAÇÃO":    "#b05ce0",
}

COR_LIMITE = "#ff4444"
COR_AVISO  = "#ffaa00"
COR_FUNDO  = "#1a1a2e"
COR_GRADE  = "#2a2a4a"
COR_TEXTO  = "#e0e0e0"


def _aplicar_estilo(ax, titulo: str) -> None:
    """Aplica estilo escuro consistente a um eixo."""
    ax.set_facecolor(COR_FUNDO)
    ax.set_title(titulo, color=COR_TEXTO, fontsize=9, pad=6)
    ax.tick_params(colors=COR_TEXTO, labelsize=7)
    ax.grid(True, color=COR_GRADE, linewidth=0.5, linestyle="--")
    for spine in ax.spines.values():
        spine.set_edgecolor(COR_GRADE)


def gerar_graficos_historico(historico: dict, pasta_saida: str = "reports") -> str | None:
    """
    Gera um painel com gráficos de evolução temporal para cada módulo.

    historico: {
        "PROPULSÃO": {
            "ciclos":       [1, 2, 3, ...],
            "p_ativa":      [9.1, 9.2, ...],
            "temperatura":  [72.0, 72.3, ...],
            "rendimento":   [0.88, 0.879, ...],
            "fator_pot":    [0.85, 0.848, ...],
        },
        ...
    }
    """
    if not MATPLOTLIB_OK:
        return None

    nomes = list(historico.keys())
    n = len(nomes)
    if n == 0:
        return None

    fig, eixos = plt.subplots(n, 4, figsize=(16, 3 * n))
    fig.patch.set_facecolor(COR_FUNDO)
    fig.suptitle(
        "Historico de Monitoramento — Missao Orbital",
        color=COR_TEXTO, fontsize=13, fontweight="bold", y=1.01
    )

    colunas = ["p_ativa", "temperatura", "rendimento", "fator_pot"]
    titulos_col = ["Potencia Ativa (kW)", "Temperatura (°C)", "Rendimento (%)", "Fator de Potencia"]

    for i, nome in enumerate(nomes):
        dados = historico[nome]
        ciclos = dados["ciclos"]
        cor = CORES_MODULOS.get(nome, "#ffffff")

        for j, (col, titulo_col) in enumerate(zip(colunas, titulos_col)):
            ax = eixos[i][j] if n > 1 else eixos[j]
            valores = dados[col]

            # Converte rendimento para percentual
            if col == "rendimento":
                valores = [v * 100 for v in valores]

            ax.plot(ciclos, valores, color=cor, linewidth=1.8, marker="o",
                    markersize=3, alpha=0.9)

            # Linha de limite crítico
            if col == "rendimento":
                ax.axhline(y=70, color=COR_LIMITE, linewidth=1, linestyle="--", alpha=0.7, label="Critico")
                ax.axhline(y=80, color=COR_AVISO,  linewidth=1, linestyle=":", alpha=0.7, label="Aviso")
            elif col == "fator_pot":
                ax.axhline(y=0.75, color=COR_LIMITE, linewidth=1, linestyle="--", alpha=0.7)
                ax.axhline(y=0.85, color=COR_AVISO,  linewidth=1, linestyle=":", alpha=0.7)

            _aplicar_estilo(ax, f"{nome} — {titulo_col}" if j == 0 else titulo_col)

    plt.tight_layout()
    os.makedirs(pasta_saida, exist_ok=True)
    caminho = os.path.join(pasta_saida, "graficos_missao.png")
    plt.savefig(caminho, dpi=120, bbox_inches="tight", facecolor=COR_FUNDO)
    plt.close()
    return caminho


def gerar_grafico_balanco(modulos: list, pasta_saida: str = "reports") -> str | None:
    """
    Gera gráfico de barras comparando P, S e Q de cada módulo.
    Visualiza claramente quais módulos mais consomem e desperdiçam energia.
    """
    if not MATPLOTLIB_OK:
        return None

    from modules.energy_calc import (
        calcular_potencia_ativa,
        calcular_potencia_aparente,
        calcular_potencia_reativa,
    )

    nomes, p_vals, s_vals, q_vals = [], [], [], []
    for m in modulos:
        p = calcular_potencia_ativa(m.p_util_kw, m.rendimento)
        s = calcular_potencia_aparente(p, m.fator_potencia)
        q = calcular_potencia_reativa(s, p)
        nomes.append(m.nome)
        p_vals.append(p)
        s_vals.append(s)
        q_vals.append(q)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    fig.patch.set_facecolor(COR_FUNDO)
    fig.suptitle(
        "Balanco Energetico Final — Missao Orbital",
        color=COR_TEXTO, fontsize=13, fontweight="bold"
    )

    x = range(len(nomes))
    largura = 0.25

    # --- Gráfico 1: P, S, Q por módulo ---
    bars_p = ax1.bar([i - largura for i in x], p_vals, largura, label="P Ativa (kW)",    color="#5c9be0", alpha=0.9)
    bars_s = ax1.bar([i           for i in x], s_vals, largura, label="S Aparente (kVA)", color="#e0b85c", alpha=0.9)
    bars_q = ax1.bar([i + largura for i in x], q_vals, largura, label="Q Reativa (kvar)", color="#e05c5c", alpha=0.9)

    ax1.set_xticks(list(x))
    ax1.set_xticklabels([n.replace(" ", "\n") for n in nomes], color=COR_TEXTO, fontsize=8)
    ax1.legend(facecolor=COR_GRADE, labelcolor=COR_TEXTO, fontsize=8)
    _aplicar_estilo(ax1, "Grandezas Eletricas por Modulo")
    ax1.set_ylabel("kW / kVA / kvar", color=COR_TEXTO, fontsize=8)

    # Adiciona valores em cima das barras
    for bar in list(bars_p) + list(bars_s) + list(bars_q):
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2, h + 0.05,
                 f"{h:.1f}", ha="center", va="bottom", color=COR_TEXTO, fontsize=6)

    # --- Gráfico 2: Pizza de distribuição de P_ativa ---
    cores_pizza = [CORES_MODULOS.get(n, "#aaaaaa") for n in nomes]
    wedges, texts, autotexts = ax2.pie(
        p_vals,
        labels=nomes,
        autopct="%1.1f%%",
        colors=cores_pizza,
        startangle=140,
        textprops={"color": COR_TEXTO, "fontsize": 8},
        wedgeprops={"edgecolor": COR_FUNDO, "linewidth": 1.5}
    )
    for at in autotexts:
        at.set_color(COR_FUNDO)
        at.set_fontweight("bold")
        at.set_fontsize(8)
    ax2.set_facecolor(COR_FUNDO)
    ax2.set_title("Distribuicao do Consumo de P Ativa", color=COR_TEXTO, fontsize=9, pad=10)

    plt.tight_layout()
    os.makedirs(pasta_saida, exist_ok=True)
    caminho = os.path.join(pasta_saida, "balanco_final.png")
    plt.savefig(caminho, dpi=120, bbox_inches="tight", facecolor=COR_FUNDO)
    plt.close()
    return caminho
