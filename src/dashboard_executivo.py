"""
Sentinel AI - Dashboard Executivo + Narrativa de Apresentacao
Fase 7: Depois de mostrarmos o Sentinel a funcionar cliente a cliente
(Fases 2-6), esta fase da um passo atras e mostra a "visao de CEO":
graficos agregados sobre TODA a carteira de clientes.

Duas partes:
1. Dashboard Executivo -- KPIs e graficos agregados (Plotly), reaproveitando
   sempre os mesmos dados ja calculados nas fases anteriores (nunca
   recalculamos nada aqui, apenas agregamos o que ja existe).
2. Guiao de Apresentacao -- um roteiro de fala pronto a usar, ligando
   cada seccao do prototipo a uma frase de impacto para investidores.
"""

import plotly.express as px
import plotly.graph_objects as go

from tema import CORES_NIVEL_SEGURANCA, COR_MARCA, COR_TEAL, aplicar_tema_plotly

NIVEIS_ISOLAMENTO_ATIVO = {"Alto", "Critico"}


def calcular_kpis(df) -> dict:
    """
    Resume a carteira inteira em 6 numeros -- os primeiros que um
    executivo quer ver antes de entrar em qualquer detalhe.

    Os dois ultimos (valor_protegido e pct_isolamento_ativo) foram
    adicionados no polimento pre-apresentacao: traduzem o Isolamento
    Inteligente (Fase 6) num impacto de negocio tangivel, em vez de
    ficar apenas como uma demonstracao tecnica isolada.
    """
    total_clientes = len(df)
    pct_critico = (
        (df["nivel_seguranca"] == "Critico").sum() / total_clientes * 100
        if total_clientes else 0.0
    )
    sentinel_index_medio = df["sentinel_index"].mean() if total_clientes else 0.0
    rentabilidade_total = df["rentabilidade"].sum() if total_clientes else 0.0

    em_isolamento = df["nivel_seguranca"].isin(NIVEIS_ISOLAMENTO_ATIVO)
    valor_protegido = df.loc[em_isolamento, "saldo_medio"].sum()
    pct_isolamento_ativo = (em_isolamento.sum() / total_clientes * 100) if total_clientes else 0.0

    return {
        "total_clientes": total_clientes,
        "pct_critico": round(pct_critico, 1),
        "sentinel_index_medio": round(sentinel_index_medio, 1) if sentinel_index_medio == sentinel_index_medio else 0.0,
        "rentabilidade_total": round(rentabilidade_total, 0),
        "valor_protegido": round(valor_protegido, 0),
        "pct_isolamento_ativo": round(pct_isolamento_ativo, 1),
    }


def grafico_distribuicao_niveis(df) -> go.Figure:
    """
    Grafico de pizza: quantos clientes existem em cada Nivel de Seguranca.
    E o primeiro relance que um executivo tem sobre "quao arriscada" e a
    carteira no seu conjunto.
    """
    contagem = df["nivel_seguranca"].value_counts().reset_index()
    contagem.columns = ["nivel_seguranca", "quantidade"]

    fig = px.pie(
        contagem,
        names="nivel_seguranca",
        values="quantidade",
        color="nivel_seguranca",
        color_discrete_map=CORES_NIVEL_SEGURANCA,
        hole=0.45,
    )
    fig.update_traces(
        textinfo="percent+label", textfont_size=13,
        marker=dict(line=dict(color="#0A0A10", width=2)),
    )
    fig.update_layout(
        title=dict(text="Distribuição por Nível de Segurança", font=dict(size=15, color=COR_MARCA), x=0.02),
        margin=dict(l=10, r=10, t=50, b=10), height=320,
        legend_title_text="Nível de Segurança",
    )
    return aplicar_tema_plotly(fig)


def grafico_index_por_segmento(df) -> go.Figure:
    """
    Barras: Sentinel Index medio por Segmento Comercial. Responde a
    pergunta de negocio "que segmento da carteira e, em media, mais
    saudavel?" -- util para decisoes comerciais, nao so de risco.
    """
    medias = (
        df.groupby("segmento_comercial")["sentinel_index"]
        .mean()
        .round(1)
        .sort_values(ascending=True)
        .reset_index()
    )

    fig = go.Figure(go.Bar(
        x=medias["sentinel_index"],
        y=medias["segmento_comercial"],
        orientation="h",
        marker=dict(
            color=medias["sentinel_index"],
            colorscale=[[0, COR_TEAL], [0.55, COR_MARCA], [1, "#FFF3D0"]],
            line=dict(color="#0A0A10", width=1),
        ),
        text=medias["sentinel_index"],
        textposition="auto",
        textfont=dict(color="#0A0A10", size=12),
    ))
    fig.update_layout(
        title=dict(text="Sentinel Index Médio por Segmento", font=dict(size=15, color=COR_MARCA), x=0.02),
        xaxis_title="Sentinel Index médio",
        yaxis_title="Segmento Comercial",
        xaxis_range=[0, 100],
        margin=dict(l=10, r=10, t=50, b=10),
        height=320,
    )
    return aplicar_tema_plotly(fig)


def grafico_dispersao_risco(df) -> go.Figure:
    """
    Dispersao Risco AML vs Risco de Credito, colorida por Nivel de
    Seguranca. Este grafico "desenha" visualmente os clusters de risco
    da carteira -- muito eficaz numa demo, porque os pontos vermelhos
    (Critico) aparecem claramente isolados no canto de maior risco.
    """
    fig = px.scatter(
        df,
        x="risco_aml",
        y="risco_credito",
        color="nivel_seguranca",
        color_discrete_map=CORES_NIVEL_SEGURANCA,
        hover_name="nome",
        hover_data={"segmento_comercial": True, "risco_aml": True, "risco_credito": True},
        labels={"risco_aml": "Risco AML", "risco_credito": "Risco de Crédito"},
    )
    fig.update_traces(marker=dict(size=11, line=dict(width=1, color="#0A0A10"), opacity=0.92))
    fig.update_layout(
        title=dict(text="Mapa de Risco da Carteira (AML vs Crédito)", font=dict(size=15, color=COR_MARCA), x=0.02),
        margin=dict(l=10, r=10, t=50, b=10), height=380,
        legend_title_text="Nível de Segurança",
    )
    return aplicar_tema_plotly(fig)


def tabela_extremos(df, n: int = 5):
    """
    Devolve (top_n, bottom_n) -- os melhores e os piores clientes por
    Sentinel Index. Util para o executivo ver de imediato quem sao os
    clientes-modelo e quem precisa de atencao.
    """
    colunas = ["nome", "segmento_comercial", "nivel_seguranca", "sentinel_index"]
    ordenado = df.sort_values("sentinel_index", ascending=False)
    top_n = ordenado.head(n)[colunas]
    bottom_n = ordenado.tail(n)[colunas].sort_values("sentinel_index")
    return top_n, bottom_n


# ---------------------------------------------------------------------------
# Guiao de Apresentacao -- narrativa pronta a usar, ligada a cada fase
# ---------------------------------------------------------------------------

GUIAO_APRESENTACAO = [
    ("1. Abertura (30s)",
     "O Sentinel AI trata cada cliente como um ser multidimensional -- nao "
     "um numero isolado. Vou mostrar-vos isso ao vivo, com 103 clientes reais "
     "gerados de forma realista."),
    ("2. Formulário Adaptativo (30s)",
     "Reparem: o formulário muda consoante o segmento do cliente. Um Private "
     "Banking recebe perguntas diferentes de um cliente Digital -- porque o "
     "risco relevante também é diferente."),
    ("3. Motor de Classificação (45s)",
     "Com um clique, o Sentinel combina Machine Learning com regras de "
     "negócio explícitas para classificar o cliente -- e explica sempre "
     "como chegou àquele resultado."),
    ("4. Sentinel Index (45s)",
     "Uma única pontuação de 0 a 100 resume três dimensões -- e os pesos "
     "são configuráveis. Se mudarmos a prioridade para risco AML em vez de "
     "rentabilidade, reparem como o ranking muda na hora."),
    ("5. Perfil Único + XAI (30s)",
     "Cada cliente tem um cartão de identidade visual -- com um gráfico "
     "radar e uma explicação em português simples de porque o índice saiu "
     "aquele valor."),
    ("6. Isolamento Inteligente (60s -- o clímax)",
     "Este é o cliente crítico. Vejam: o gestor comercial só vê nome e "
     "profissão -- o resto está protegido. O compliance vê tudo. Isto "
     "acontece automaticamente, sem ninguém configurar uma única permissão."),
    ("7. Dashboard Executivo (30s)",
     "E aqui está a visão de topo: a saúde de toda a carteira, num relance. "
     "Isto é o que um banco veria todas as manhãs."),
    ("Fecho",
     "Não construímos uma plataforma bancária completa -- construímos a "
     "prova de que esta forma de pensar sobre dados de clientes funciona, "
     "escala, e é possível de implementar."),
]
