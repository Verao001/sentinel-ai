"""
Sentinel AI - Regras de Negocio e Preparacao de Dados
Fase 3.1: A parte "explicavel" do Motor de Classificacao Multidimensional.

Este modulo contem duas coisas que, propositadamente, NAO dependem de
Machine Learning:

1. Codificacao de categorias em numeros (necessaria porque os modelos de
   scikit-learn so trabalham com numeros, nunca com texto).
2. Regras de negocio explicitas: conhecimento humano sobre o que aumenta
   o risco de um cliente, escrito de forma clara e legivel.

Ao manter isto separado do modelo de ML (que vem na Fase 3.2), qualquer
pessoa -- mesmo sem saber nada de scikit-learn -- consegue ler e ajustar
estas regras.
"""

from formulario import (
    PERGUNTA_PRIVATE_BANKING,
    PERGUNTA_RETALHO,
    PERGUNTA_CORPORATE,
    PERGUNTA_DIGITAL,
)

# ---------------------------------------------------------------------------
# Codificacao de Segmento Comercial -> numero
# ---------------------------------------------------------------------------
# Os modelos de ML precisam de numeros. Em vez de deixar o scikit-learn
# "adivinhar" a codificacao (o que pode mudar entre execucoes), definimos
# nos mesmos um mapeamento fixo e prevas ivel.

SEGMENTOS_ENCODING = {
    "Private Banking": 0,
    "Retalho": 1,
    "Corporate": 2,
    "Digital": 3,
    "Corporate / Institucional": 4,
}


def codificar_segmento(segmento: str) -> int:
    """
    Converte o nome do segmento comercial num numero para o modelo.

    Devolve -1 para segmentos desconhecidos (protecao contra dados
    inesperados -- boa pratica de robustez).
    """
    return SEGMENTOS_ENCODING.get(segmento, -1)


# ---------------------------------------------------------------------------
# Regras de negocio: ajustes ao Risco AML
# ---------------------------------------------------------------------------
# Cada entrada diz: "para esta pergunta, esta resposta especifica, soma
# estes pontos ao risco AML estimado pelo modelo". Os pontos vao de 0 a 100
# e sao a MESMA escala usada nos dados sinteticos da Fase 1.

REGRAS_AJUSTE_AML = {
    PERGUNTA_PRIVATE_BANKING: {
        "Sim": 15,   # ter contas no estrangeiro e um sinal classico de AML
        "Nao": 0,
    },
    PERGUNTA_CORPORATE: {
        "Frequentemente": 25,   # bandeira vermelha forte
        "Ocasionalmente": 10,
        "Nao": 0,
    },
}


# ---------------------------------------------------------------------------
# Regras de negocio: ajustes ao Risco de Credito
# ---------------------------------------------------------------------------

REGRAS_AJUSTE_CREDITO = {
    PERGUNTA_DIGITAL: {
        "Nao": 15,   # identidade nao verificada = mais incerteza = mais risco
        "Sim": 0,
    },
}


def _ajuste_por_anos_de_relacao(anos: int) -> int:
    """
    Regra de negocio para o segmento Retalho: quanto MENOS tempo de
    relacao com o banco, MAIOR o risco de credito (menos historico
    para avaliar o comportamento do cliente).

    Exemplos:
      0 anos  -> +20 pontos de risco
      10 anos -> +10 pontos de risco
      20+ anos -> +0 pontos de risco
    """
    pontos = 20 - int(anos)
    return max(0, pontos)


def calcular_ajustes_risco(respostas_adaptativas: dict) -> tuple[int, int]:
    """
    Aplica todas as regras de negocio as respostas adaptativas de um
    cliente e devolve (ajuste_risco_aml, ajuste_risco_credito).

    Estes ajustes sao SOMADOS a estimativa do modelo de ML (Fase 3.2),
    nunca a substituem -- por isso o motor e "hibrido".
    """
    ajuste_aml = 0
    ajuste_credito = 0

    for pergunta, resposta in respostas_adaptativas.items():
        if pergunta == PERGUNTA_RETALHO:
            # Caso especial: a resposta e um numero (anos), nao uma
            # categoria, por isso usa uma funcao em vez de um dicionario.
            ajuste_credito += _ajuste_por_anos_de_relacao(resposta)
            continue

        if pergunta in REGRAS_AJUSTE_AML:
            ajuste_aml += REGRAS_AJUSTE_AML[pergunta].get(str(resposta), 0)

        if pergunta in REGRAS_AJUSTE_CREDITO:
            ajuste_credito += REGRAS_AJUSTE_CREDITO[pergunta].get(str(resposta), 0)

    return ajuste_aml, ajuste_credito


# ---------------------------------------------------------------------------
# Preparacao das features (variaveis de entrada) para o modelo de ML
# ---------------------------------------------------------------------------

FEATURES_MODELO = ["idade", "saldo_medio", "rentabilidade", "segmento_encoded"]


def preparar_features(df):
    """
    Recebe um DataFrame de clientes (colunas: idade, saldo_medio,
    rentabilidade, segmento_comercial) e devolve um novo DataFrame
    apenas com as colunas numericas que o modelo vai usar.

    E importante que este calculo seja SEMPRE identico entre o treino
    do modelo e a previsao de um cliente novo -- por isso vive numa
    unica funcao reutilizada nos dois casos.
    """
    df = df.copy()
    df["segmento_encoded"] = df["segmento_comercial"].apply(codificar_segmento)
    return df[FEATURES_MODELO]
