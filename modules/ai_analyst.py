"""
ai_analyst.py
=============
Módulo de Inteligência Artificial para análise de alertas críticos.

Utiliza a API da Anthropic (Claude) para gerar diagnósticos em linguagem
natural quando condições críticas são detectadas na missão.

Por que isso é IA e não apenas regras?
  - O sistema de alertas usa if/else com limiares fixos (lógica determinística)
  - Este módulo envia o contexto completo para um modelo de linguagem (LLM)
    que raciocina sobre os dados e gera uma análise contextualizada
  - O LLM pode identificar padrões combinados (ex: temperatura alta + rendimento
    baixo + FP degradado = indício de falha iminente de rolamento) que regras
    fixas não capturam facilmente

Referência: Inteligência Artificial Introdutória — análise preditiva com LLM
"""

import urllib.request
import urllib.error
import json
from modules.alert_system import NivelAlerta, COR


def _chamar_api_claude(prompt: str) -> str:
    """
    Faz a chamada à API da Anthropic e retorna o texto da resposta.
    Usa apenas urllib (biblioteca padrão) — sem dependências externas.
    """
    url = "https://api.anthropic.com/v1/messages"
    payload = {
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 400,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "system": (
            "Você é um engenheiro de sistemas espaciais especializado em energia. "
            "Analise os dados fornecidos de forma técnica, direta e objetiva. "
            "Responda sempre em português. "
            "Use no máximo 5 linhas. Seja preciso e prático — aponte a causa provável "
            "e a ação recomendada com base nos valores numéricos fornecidos. "
            "Não use markdown, não use asteriscos, não use bullets."
        )
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("anthropic-version", "2023-06-01")
    # A chave é injetada automaticamente pelo ambiente — não precisa configurar nada

    with urllib.request.urlopen(req, timeout=15) as resp:
        resultado = json.loads(resp.read().decode("utf-8"))
        return resultado["content"][0]["text"].strip()


def analisar_situacao_critica(modulo, alertas: list) -> str | None:
    """
    Aciona a IA apenas quando há alertas CRÍTICOS ou FALHA.
    Monta um prompt rico com todos os dados do módulo e retorna
    a análise gerada pelo modelo.

    Retorna None se não houver situação crítica ou se a API falhar.
    """
    alertas_graves = [
        a for a in alertas
        if a.nivel in (NivelAlerta.CRITICO, NivelAlerta.FALHA)
    ]

    if not alertas_graves:
        return None

    # Monta descrição dos alertas
    desc_alertas = "\n".join(
        f"  - [{a.nivel.value}] {a.mensagem}" for a in alertas_graves
    )

    prompt = f"""Módulo espacial: {modulo.nome}
Dados operacionais atuais:
  - Potência útil: {modulo.p_util_kw} kW
  - Rendimento: {modulo.rendimento * 100:.1f}%
  - Fator de Potência: {modulo.fator_potencia:.3f}
  - Temperatura: {modulo.temp_operacional:.1f}°C (limites: {modulo.temp_minima}°C a {modulo.temp_maxima}°C)
  - Tempo em operação: {modulo.tempo_operacao_h:.0f} horas
  - Comunicação: {"OK" if modulo.comunicacao_ok else "FALHA"}

Alertas detectados:
{desc_alertas}

Com base nesses dados, forneça um diagnóstico técnico: qual é a causa provável \
dos problemas e qual ação imediata deve ser tomada pela equipe de controle da missão?"""

    try:
        return _chamar_api_claude(prompt)
    except urllib.error.URLError:
        return None
    except Exception:
        return None


def exibir_analise_ia(modulo_nome: str, analise: str) -> None:
    """Exibe o bloco de análise da IA formatado no terminal."""
    largura = 64
    print(f"\n  {COR['NEGRITO']}[ DIAGNOSTICO IA — {modulo_nome} ]{COR['RESET']}")
    print(f"  {'─' * largura}")

    # Quebra o texto em linhas de no máximo 62 caracteres
    palavras = analise.split()
    linha_atual = "  "
    for palavra in palavras:
        if len(linha_atual) + len(palavra) + 1 > 64:
            print(linha_atual)
            linha_atual = "  " + palavra + " "
        else:
            linha_atual += palavra + " "
    if linha_atual.strip():
        print(linha_atual)

    print(f"  {'─' * largura}")
