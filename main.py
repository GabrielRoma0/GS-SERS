"""
main.py
=======
Sistema de Monitoramento Energetico — Missao Orbital Experimental
Disciplina: Solucoes em Energias Renovaveis e Sustentaveis
Curso: Ciencia da Computacao — 1 Ano | FIAP

Execucao:
    python main.py                  → monitoramento continuo (Ctrl+C para parar)
    python main.py --demo           → roda 10 ciclos automaticamente e encerra
    python main.py --simular-crise  → forca condicoes criticas para demonstracao

Estrutura do Projeto:
    main.py                     <- voce esta aqui
    modules/
        energy_calc.py          <- calculos de P, S, Q (formulas do CP01)
        mission_data.py         <- definicao dos modulos espaciais + historico
        alert_system.py         <- geracao de alertas e decisoes automaticas
        ai_analyst.py           <- diagnostico com IA (API Anthropic)
        display.py              <- visualizacao no terminal
        grafico.py              <- graficos de historico e balanco (matplotlib)
        reporter.py             <- relatorio em arquivo .txt
    reports/                    <- graficos e relatorio gerados automaticamente
"""

import time
import sys
import os

from modules.mission_data  import criar_modulos_missao, ModuloEspacial
from modules.alert_system  import analisar_modulo_alertas, NivelAlerta
from modules.display       import cabecalho_missao, painel_modulo, resumo_energetico, rodape, COR
from modules.reporter      import gerar_relatorio
from modules.ai_analyst    import analisar_situacao_critica, exibir_analise_ia
from modules.grafico       import gerar_graficos_historico, gerar_grafico_balanco
from modules.energy_calc   import calcular_potencia_ativa


# ─── Configuracoes ─────────────────────────────────────────────────────────────

INTERVALO_CICLO_SEGUNDOS = 3
CICLOS_DEMO              = 10   # mais ciclos = graficos mais ricos


def simular_crise(modulos: list[ModuloEspacial]) -> None:
    """Forca condicoes criticas para demonstracao."""
    print(f"\n{COR['CRITICO']}  SIMULANDO CONDICOES CRITICAS PARA DEMONSTRACAO...{COR['RESET']}\n")
    time.sleep(1)
    modulos[0].temp_operacional = modulos[0].temp_maxima * 0.97  # Propulsao superaquecida
    modulos[2].rendimento       = 0.68    # Suporte Vital degradado (ref CP01 Q2)
    modulos[3].fator_potencia   = 0.72    # Laboratorio com FP critico
    modulos[4].comunicacao_ok   = False   # Navegacao sem sinal


def executar_ciclo(modulos: list[ModuloEspacial], numero_ciclo: int, usar_ia: bool) -> list:
    """
    Executa um ciclo completo:
    1. Atualiza simulacao
    2. Calcula grandezas eletricas e registra historico
    3. Analisa alertas
    4. Aciona IA para alertas criticos
    5. Exibe dashboard
    """
    todos_alertas     = []
    alertas_por_mod   = {}
    analises_ia       = {}

    for modulo in modulos:
        if not modulo.ativo:
            continue

        modulo.atualizar_simulacao()

        # Calcula P_ativa e registra na serie temporal
        p_ativa = calcular_potencia_ativa(modulo.p_util_kw, modulo.rendimento)
        modulo.registrar_historico(numero_ciclo, p_ativa)

        # Verifica alertas
        alertas = analisar_modulo_alertas(modulo)
        todos_alertas.extend(alertas)
        alertas_por_mod[modulo.nome] = alertas

        # Aciona IA apenas para alertas CRITICOS ou FALHA
        if usar_ia:
            tem_critico = any(a.nivel in (NivelAlerta.CRITICO, NivelAlerta.FALHA) for a in alertas)
            if tem_critico:
                analise = analisar_situacao_critica(modulo, alertas)
                if analise:
                    analises_ia[modulo.nome] = analise

    # Exibe o dashboard
    os.system("clear" if os.name != "nt" else "cls")
    cabecalho_missao(numero_ciclo, todos_alertas)

    for modulo in modulos:
        if modulo.ativo:
            painel_modulo(modulo, alertas_por_mod.get(modulo.nome, []))
            # Bloco de diagnostico IA logo abaixo do modulo, se houver
            if modulo.nome in analises_ia:
                exibir_analise_ia(modulo.nome, analises_ia[modulo.nome])

    resumo_energetico(modulos)
    rodape(numero_ciclo)

    return todos_alertas


def montar_historico(modulos: list[ModuloEspacial]) -> dict:
    """Converte os dados de historico dos modulos para o formato do grafico."""
    return {
        m.nome: {
            "ciclos":      m.hist_ciclos,
            "p_ativa":     m.hist_p_ativa,
            "temperatura": m.hist_temperatura,
            "rendimento":  m.hist_rendimento,
            "fator_pot":   m.hist_fator_pot,
        }
        for m in modulos if m.hist_ciclos
    }


def main():
    modo_demo  = "--demo"          in sys.argv
    modo_crise = "--simular-crise" in sys.argv
    usar_ia    = "--sem-ia"        not in sys.argv  # IA ativa por padrao

    print(f"\n{COR['NEGRITO']}  Inicializando Sistema de Monitoramento Energetico...{COR['RESET']}")
    print(f"  IA ({'ativa' if usar_ia else 'desativada'}) | Graficos (ativos)\n")
    time.sleep(1)

    modulos = criar_modulos_missao()

    if modo_crise:
        simular_crise(modulos)

    ciclo = 0
    try:
        while True:
            ciclo += 1
            executar_ciclo(modulos, ciclo, usar_ia)

            if modo_demo and ciclo >= CICLOS_DEMO:
                print(f"\n  {COR['VERDE']}Modo demonstracao concluido ({CICLOS_DEMO} ciclos).{COR['RESET']}\n")
                break

            time.sleep(INTERVALO_CICLO_SEGUNDOS)

    except KeyboardInterrupt:
        print("\n\n  Monitoramento encerrado pelo operador.")

    finally:
        print(f"\n  {COR['NEGRITO']}Gerando relatorio e graficos...{COR['RESET']}")

        # Relatorio em texto
        gerar_relatorio(modulos, ciclos_executados=ciclo)

        # Graficos de historico temporal
        historico = montar_historico(modulos)
        if historico:
            caminho_hist = gerar_graficos_historico(historico)
            if caminho_hist:
                print(f"  Graficos de historico salvos em: {caminho_hist}")

        # Grafico de balanco final
        caminho_bal = gerar_grafico_balanco(modulos)
        if caminho_bal:
            print(f"  Balanco energetico salvo em:      {caminho_bal}")

        print(f"\n  {COR['VERDE']}Missao encerrada. Ate o proximo lancamento!{COR['RESET']}\n")


if __name__ == "__main__":
    main()
