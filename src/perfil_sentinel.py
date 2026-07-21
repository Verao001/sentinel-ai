"""
Sentinel AI - Perfil Unico Sentinel + Dashboard Visual + XAI basico
Fase 5: Junta tudo o que ja construimos (dados, classificacao, Sentinel
Index) num unico "cartao de identidade" visual por cliente.

Duas ideias centrais desta fase:

1. Perfil Unico -- em vez de tabelas soltas, o utilizador escolhe UM
   cliente e ve tudo sobre ele num so ecra: dados pessoais, os 3 riscos,
   o Sentinel Index, e um grafico radar que "desenha" o perfil.

2. XAI basico (Explainable AI) -- nao escondemos a formula do Sentinel
   Index dentro de uma caixa preta. Mostramos, em pontos, o quanto cada
   dimensao (AML, Credito, Rentabilidade) contribuiu para o resultado
   final. Isto e "explicabilidade por decomposicao" -- uma tecnica simples,
   mas poderosa para ganhar confianca de um banco ou de um investidor.
"""

import plotly.graph_objects as go

from sentinel_index import normalizar_pesos, normalizar_rentabilidade, PESOS_PADRAO
from tema import COR_MARCA, COR_MARCA_CLARA, COR_TEAL, COR_AVISO, aplicar_tema_plotly


def calcular_contribuicoes(cliente, df_referencia, pesos: dict = None) -> dict:
    """
    Decompoe o Sentinel Index de UM cliente nos pontos que cada dimensao
    (AML, Credito, Rentabilidade) efetivamente contribuiu para o total.

    Isto usa exatamente a mesma formula de sentinel_index.py -- nunca a
    duplicamos, apenas expomos os passos intermedios que a formula ja
    calcula "por dentro", para os podermos mostrar ao utilizador.
    """
    pesos = normalizar_pesos(pesos or PESOS_PADRAO)

    seguranca_aml = 100 - cliente["risco_aml"]
    seguranca_credito = 100 - cliente["risco_credito"]
    rentabilidade_normalizada = normalizar_rentabilidade(
        cliente["rentabilidade"],
        df_referencia["rentabilidade"].min(),
        df_referencia["rentabilidade"].max(),
    )

    contribuicao_aml = pesos["risco_aml"] / 100 * seguranca_aml
    contribuicao_credito = pesos["risco_credito"] / 100 * seguranca_credito
    contribuicao_rentabilidade = pesos["rentabilidade"] / 100 * rentabilidade_normalizada

    return {
        "Seguranca AML": round(contribuicao_aml, 1),
        "Seguranca Credito": round(contribuicao_credito, 1),
        "Rentabilidade": round(contribuicao_rentabilidade, 1),
        "_valores_0_100": {
            "Seguranca AML": round(seguranca_aml, 1),
            "Seguranca Credito": round(seguranca_credito, 1),
            "Rentabilidade": round(rentabilidade_normalizada, 1),
        },
    }


def gerar_grafico_radar(contribuicoes: dict) -> go.Figure:
    """
    Desenha o "formato" do cliente num grafico radar (tambem chamado
    grafico de aranha). E o grafico mais usado em bancos para comparar
    varias dimensoes de risco de uma so vez, de forma visual.
    """
    valores = contribuicoes["_valores_0_100"]
    categorias = list(valores.keys())
    pontuacoes = list(valores.values())

    # Fecha o poligono repetindo o primeiro ponto no fim.
    categorias_fechado = categorias + [categorias[0]]
    pontuacoes_fechado = pontuacoes + [pontuacoes[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=pontuacoes_fechado,
        theta=categorias_fechado,
        fill="toself",
        name="Perfil do cliente",
        line=dict(color=COR_MARCA, width=3),
        fillcolor="rgba(255, 221, 119, 0.20)",
        marker=dict(size=9, color=COR_MARCA_CLARA, line=dict(color=COR_MARCA, width=1)),
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, range=[0, 100],
                gridcolor="rgba(255,255,255,0.10)", tickfont=dict(size=11, color="#A9A8B8"),
                linecolor="rgba(255,255,255,0.1)",
            ),
            angularaxis=dict(tickfont=dict(size=13, color="#F5F1E8"), gridcolor="rgba(255,255,255,0.10)"),
            bgcolor="rgba(0,0,0,0)",
        ),
        showlegend=False,
        margin=dict(l=60, r=60, t=40, b=40),
        height=460,
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return aplicar_tema_plotly(fig)


def gerar_grafico_contribuicoes(contribuicoes: dict) -> go.Figure:
    """
    Grafico de barras horizontal: quantos PONTOS do Sentinel Index final
    vieram de cada dimensao. E aqui que a "caixa preta" se abre -- o
    utilizador ve exatamente de onde veio o numero final.
    """
    dados = {k: v for k, v in contribuicoes.items() if not k.startswith("_")}
    categorias = list(dados.keys())
    valores = list(dados.values())

    fig = go.Figure(go.Bar(
        x=valores,
        y=categorias,
        orientation="h",
        marker=dict(
            color=[COR_TEAL, COR_MARCA, COR_AVISO],
            line=dict(color="#0A0A10", width=1),
            opacity=0.95,
        ),
        text=[f"{v:.1f} pts" for v in valores],
        textposition="auto",
        textfont=dict(color="#0A0A10", size=13, family="Inter"),
    ))
    fig.update_layout(
        xaxis_title="Pontos contribuidos para o Sentinel Index",
        margin=dict(l=10, r=10, t=10, b=10),
        height=270,
        bargap=0.35,
    )
    return aplicar_tema_plotly(fig)


def gerar_explicacao_textual(cliente, contribuicoes: dict) -> list:
    """
    Traduz os numeros em frases claras e profissionais -- a mesma logica
    de "XAI basico" ja usada no Motor de Classificacao (Fase 3), agora
    aplicada ao Sentinel Index em si.
    """
    dados = {k: v for k, v in contribuicoes.items() if not k.startswith("_")}
    dimensao_principal = max(dados, key=dados.get)
    dimensao_fraca = min(dados, key=dados.get)
    total = sum(dados.values())

    pct_principal = round(dados[dimensao_principal] / total * 100) if total else 0
    pct_fraca = round(dados[dimensao_fraca] / total * 100) if total else 0

    frases = [
        f"O Sentinel Index de **{cliente['nome']}** é de **{cliente['sentinel_index']:.1f}/100**, "
        f"calculado a partir de 3 dimensões ponderadas: Risco AML, Risco de Crédito e Rentabilidade.",
        f"A dimensão **{dimensao_principal}** foi a que mais contribuiu para este resultado "
        f"({dados[dimensao_principal]:.1f} pontos, cerca de {pct_principal}% do índice final).",
        f"A dimensão **{dimensao_fraca}** foi a mais fraca ({dados[dimensao_fraca]:.1f} pontos, "
        f"~{pct_fraca}%) -- é onde uma intervenção comercial ou de risco teria maior impacto "
        f"na evolução deste cliente.",
    ]
    return frases
