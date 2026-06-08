# Sistema de Monitoramento Energético — Missão Orbital

Projeto desenvolvido para a disciplina **Soluções em Energias Renováveis e Sustentáveis**  
Curso: Ciência da Computação — 1º Ano | FIAP  
Desafio: Global Solution 2026 — Soluções em Energias Renováveis e Sustentáveis

---

## Integrantes

| Nome completo | RM |
|---------------|----|
|  Gabriel Botelho Romão             | 570589 |
|  Thor Ferreira Camargo             | 569543 |

---

## Descrição

Este projeto implementa um sistema de monitoramento inteligente de energia aplicado a uma missão espacial experimental simulada. O sistema interpreta dados operacionais de cinco módulos da nave, calcula grandezas elétricas em tempo real, gera alertas automáticos diante de condições críticas e exibe um dashboard organizado no terminal.

A solução aplica diretamente os conceitos estudados na disciplina: Potência Ativa, Potência Aparente, Potência Reativa, Rendimento e Fator de Potência.

---

## Módulos Monitorados

| Módulo        | Função                                      |
|---------------|---------------------------------------------|
| PROPULSAO     | Motores ionicos de manobra orbital          |
| COMUNICACAO   | Antenas e transmissores de dados            |
| SUPORTE VITAL | Sistemas de ar, temperatura e pressao       |
| LABORATORIO   | Equipamentos de pesquisa cientifica         |
| NAVEGACAO     | Computadores de bordo e sensores            |

---

## Funcionalidades

- Monitoramento continuo em ciclos com atualizacao em tempo real no terminal
- Calculo automatico de P, S, Q e consumo energetico por modulo a cada ciclo
- Geracao de alertas em tres niveis: AVISO, CRITICO e FALHA
- Respostas automatizadas para cada tipo de condicao critica detectada
- Balanco energetico total da missao com indicador de capacidade dos paineis solares
- Relatorio em arquivo `.txt` gerado automaticamente ao encerrar o sistema
- Modo de simulacao de crise para demonstracao de alertas criticos

---

## Conceitos Aplicados

```
P = P_util / rendimento          (Potencia Ativa em kW)
S = P / fator_de_potencia        (Potencia Aparente em kVA)
Q = raiz(S^2 - P^2)              (Potencia Reativa em kvar)
E = P * t                        (Consumo de energia em kWh)
```

Na missao espacial, esses conceitos se traduzem da seguinte forma:

- **Potencia Ativa (P):** energia real que cada modulo consome dos paineis solares
- **Potencia Aparente (S):** capacidade minima que os paineis precisam fornecer
- **Potencia Reativa (Q):** energia "desperdicada" em campos eletromagneticos, sem realizar trabalho
- **Fator de Potencia:** indica o quanto da energia fornecida e aproveitada (ideal = 1.0)
- **Rendimento:** eficiencia do equipamento (ideal = 1.0 = 100%)

---

## Estrutura do Projeto

```
space_energy_monitor/
│
├── main.py                  # Arquivo principal — inicia o sistema
│
├── modules/
│   ├── energy_calc.py       # Calculos de P, S, Q e consumo
│   ├── mission_data.py      # Definicao e simulacao dos modulos espaciais
│   ├── alert_system.py      # Geracao de alertas e decisoes automaticas
│   ├── display.py           # Visualizacao do dashboard no terminal
│   └── reporter.py          # Geracao de relatorio em arquivo
│
└── reports/
    └── relatorio_missao.txt # Gerado automaticamente ao encerrar
```

---

## Como Executar

## Pré-requisitos

- Python 3.10 ou superior
- pip3

Verifique sua versão:
```bash
python3 --version
```

## Instalação

Clone o repositório:
```bash
git clone https://github.com/GabrielRoma0/GS-SERS.git
cd GS-SERS/space_energy_monitor
```

Instale a dependência necessária:
```bash
pip3 install matplotlib --break-system-packages
```

## Execução

Monitoramento contínuo (encerra com Ctrl+C):
```bash
python3 main.py
```

Modo demonstração — roda 10 ciclos e encerra sozinho:
```bash
python3 main.py --demo
```

Modo crise — força condições críticas para demonstrar os alertas:
```bash
python3 main.py --simular-crise
```

Modo sem IA — caso não tenha conexão com a internet:
```bash
python3 main.py --demo --sem-ia
```

Ao encerrar, os arquivos abaixo são gerados automaticamente em `reports/`:
- `relatorio_missao.txt` — resumo completo da sessão
- `graficos_missao.png` — evolução temporal de cada módulo
- `balanco_final.png` — distribuição do consumo energético

## Niveis de Alerta

| Nivel   | Condicao                                         | Resposta Automatica                              |
|---------|--------------------------------------------------|--------------------------------------------------|
| AVISO   | Temperatura acima de 85% do limite               | Aumenta ventilacao e monitora proximos ciclos    |
| AVISO   | Rendimento abaixo de 80%                         | Agenda manutencao preventiva                     |
| AVISO   | Fator de Potencia abaixo de 0.85                 | Verifica carga reativa e ajusta compensacao      |
| CRITICO | Temperatura acima de 95% do limite               | Ativa dissipadores e reduz carga em 30%          |
| CRITICO | Rendimento abaixo de 70%                         | Sinaliza manutencao de emergencia                |
| CRITICO | Fator de Potencia abaixo de 0.75                 | Ativa banco de capacitores de correcao           |
| FALHA   | Perda de sinal de comunicacao                    | Alterna para antena reserva e tenta reconexao    |

---

## Exemplo de Saida

```
SISTEMA DE MONITORAMENTO ENERGETICO — MISSAO ORBITAL
Ciclo de Monitoramento : #0003
Status Geral da Missao : MONITORANDO
Alertas Ativos         : 1

[ PROPULSAO ]  Comunicacao: ONLINE  |  Uptime: 3h
  P_util (potencia entregue)     8.0000 kW   base do calculo
  P_ativa (consumida da fonte)   9.0948 kW   P = P_util / rendimento
  S_aparente (carga total)      10.5367 kVA  S = P / FP
  Q_reativa (desperdicio)        5.3204 kvar Q = raiz(S^2 - P^2)
  Consumo estimado 8h           72.7584 kWh  E = P x t

BALANCO ENERGETICO TOTAL DA MISSAO
  P Total (Ativa)    :  21.75 kW
  S Total (Aparente) :  25.19 kVA  <- capacidade minima dos paineis solares
  Consumo em 24h     :  522.12 kWh <- energia minima a gerar por dia
```

---

## Links

- Repositorio GitHub: https://github.com/GabrielRoma0/GS-SERS
- Video YouTube: https://www.youtube.com/watch?v=uiKPPgEhx7c
