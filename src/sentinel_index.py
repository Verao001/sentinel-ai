"""
Sentinel AI - Calculo do Sentinel Index
Fase 4: Uma unica pontuacao (0-100) que resume a "saude" multidimensional
de um cliente, combinando Risco AML, Risco de Credito e Rentabilidade,
com pesos configuraveis pelo utilizador.

Logica central: quanto MENOR o risco e MAIOR a rentabilidade, MAIOR o
Sentinel Index. 100 = melhor cliente possivel, 0 = pior caso possivel.
"""

PESOS_PADRAO = {
    "risco_aml": 35,
    "risco_credito": 25,
    "rentabilidade": 40,
}


def normalizar_pesos(pesos: dict) -> dict:
    """
    Garante que os pesos somam sempre 100%, mesmo que o utilizador tenha
    movido os sliders para um total diferente (ex.: 90 ou 130). Isto
    evita que o Sentinel Index saia de uma escala 0-100 por engano.
    """
    soma = sum(pesos.values())
    if soma == 0:
        return PESOS_PADRAO.copy()
    return {chave: (valor / soma) * 100 for chave, valor in pesos.items()}


def normalizar_rentabilidade(rentabilidade: float, minimo: float, maximo: float) -> float:
    """
    Converte a rentabilidade (que pode ir de perto de 0 ate mais de 1
    milhao) para uma escala 0-100, comparavel com os scores de risco.

    Tecnica: normalizacao min-max. Compara o cliente com o "pior" e o
    "melhor" cliente do grupo em analise.
    """
    if maximo == minimo:
        return 50.0  # protecao: evita divisao por zero com 1 so cliente
    valor = (rentabilidade - minimo) / (maximo - minimo) * 100
    return max(0.0, min(100.0, valor))


def calcular_sentinel_index(
    risco_aml: float,
    risco_credito: float,
    rentabilidade: float,
    rentabilidade_min: float,
    rentabilidade_max: float,
    pesos: dict = None,
) -> float:
    """
    Calcula o Sentinel Index de UM cliente.

    Passos:
      1. Inverte os riscos (100 - risco) porque risco alto = mau sinal,
         mas o indice deve subir quando o cliente e melhor.
      2. Normaliza a rentabilidade para 0-100.
      3. Faz a media ponderada dos 3 valores, usando os pesos dados.
    """
    pesos = normalizar_pesos(pesos or PESOS_PADRAO)

    seguranca_aml = 100 - risco_aml
    seguranca_credito = 100 - risco_credito
    rentabilidade_normalizada = normalizar_rentabilidade(
        rentabilidade, rentabilidade_min, rentabilidade_max
    )

    indice = (
        pesos["risco_aml"] / 100 * seguranca_aml
        + pesos["risco_credito"] / 100 * seguranca_credito
        + pesos["rentabilidade"] / 100 * rentabilidade_normalizada
    )

    return round(max(0.0, min(100.0, indice)), 1)


# ---------------------------------------------------------------------------
# Categorias legiveis do indice (uteis para a narrativa da demonstracao)
# ---------------------------------------------------------------------------

CATEGORIAS_INDEX = [
    (80, "Excelente"),
    (60, "Bom"),
    (40, "Regular"),
    (0, "Atencao"),
]


def classificar_index(indice: float) -> str:
    """Traduz o valor numerico do Sentinel Index numa categoria legivel."""
    for limite, categoria in CATEGORIAS_INDEX:
        if indice >= limite:
            return categoria
    return "Atencao"


def calcular_sentinel_index_todos(df, pesos: dict = None):
    """
    Calcula o Sentinel Index para todos os clientes de um DataFrame de
    uma so vez, usando o minimo e o maximo de rentabilidade DESSE MESMO
    grupo de clientes como referencia de normalizacao.

    Devolve uma Series (uma coluna) com o indice de cada cliente, na
    mesma ordem das linhas do DataFrame recebido.
    """
    rentabilidade_min = df["rentabilidade"].min()
    rentabilidade_max = df["rentabilidade"].max()

    return df.apply(
        lambda linha: calcular_sentinel_index(
            risco_aml=linha["risco_aml"],
            risco_credito=linha["risco_credito"],
            rentabilidade=linha["rentabilidade"],
            rentabilidade_min=rentabilidade_min,
            rentabilidade_max=rentabilidade_max,
            pesos=pesos,
        ),
        axis=1,
    )
