"""
Sentinel AI - Motor de Classificacao Multidimensional
Fase 3.2: Modelos de Machine Learning + combinacao com regras de negocio.

Este e o coracao do motor HIBRIDO do Sentinel AI: usa scikit-learn para
aprender padroes a partir dos 100 clientes sinteticos da Fase 1, e depois
combina essas estimativas com as regras de negocio explicitas definidas
em regras_negocio.py (Fase 3.1).

Fluxo geral:
    1. Treinar 3 modelos simples nos clientes sinteticos (que ja tem
       risco conhecido).
    2. Para um cliente novo (ex.: vindo do formulario), o modelo estima
       um risco inicial.
    3. As regras de negocio ajustam esse risco com base em respostas
       especificas do formulario adaptativo.
    4. Uma regra de seguranca final pode escalar o Nivel de Seguranca
       para "Critico", independentemente do que o modelo previu.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier

from database import (
    obter_dados_treino,
    listar_pendentes,
    obter_respostas_adaptativas,
    atualizar_classificacao,
)
from regras_negocio import preparar_features, calcular_ajustes_risco, FEATURES_MODELO
from data_generator import PERFIS

RANDOM_STATE = 42
LIMIAR_RISCO_CRITICO = 80  # a partir deste valor, o nivel de seguranca e sempre "Critico"


def treinar_modelos() -> dict:
    """
    Treina os 3 modelos do motor de classificacao usando os clientes
    sinteticos da Fase 1 -- os unicos que ja tem risco_aml, risco_credito
    e perfil_origem conhecidos, servindo de "professores" para o modelo.

    Devolve um dicionario com os 3 modelos treinados, prontos a usar.
    """
    df_treino = obter_dados_treino()

    if len(df_treino) < 10:
        raise ValueError(
            "Dados de treino insuficientes para o Motor de Classificacao. "
            "Confirma que correste 'python src/data_generator.py' antes de classificar clientes."
        )

    X = preparar_features(df_treino)
    y_aml = df_treino["risco_aml"]
    y_credito = df_treino["risco_credito"]
    y_perfil = df_treino["perfil_origem"]

    modelo_aml = RandomForestRegressor(n_estimators=100, random_state=RANDOM_STATE)
    modelo_aml.fit(X, y_aml)

    modelo_credito = RandomForestRegressor(n_estimators=100, random_state=RANDOM_STATE)
    modelo_credito.fit(X, y_credito)

    modelo_perfil = RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE)
    modelo_perfil.fit(X, y_perfil)

    return {
        "risco_aml": modelo_aml,
        "risco_credito": modelo_credito,
        "perfil": modelo_perfil,
    }


def obter_metadados_modelo(modelos: dict, df_treino: pd.DataFrame) -> dict:
    """
    Reune metadados de transparencia sobre os modelos treinados --
    algoritmo usado, tamanho do conjunto de treino e importancia de
    cada variavel (feature importance).

    Isto NAO afeta o calculo em nada -- serve apenas para o Perfil Unico
    Sentinel poder mostrar, de forma honesta, "que modelo de ML esta
    realmente a funcionar por tras do resultado" (Melhoria 1 -- reforcar
    a demonstracao de Machine Learning para investidores).
    """
    return {
        "algoritmo": "Random Forest (ensemble de arvores de decisao)",
        "n_arvores": modelos["risco_aml"].n_estimators,
        "n_clientes_treino": len(df_treino),
        "features": FEATURES_MODELO,
        "importancia_risco_aml": dict(zip(
            FEATURES_MODELO, modelos["risco_aml"].feature_importances_.round(3)
        )),
        "importancia_risco_credito": dict(zip(
            FEATURES_MODELO, modelos["risco_credito"].feature_importances_.round(3)
        )),
        "importancia_perfil": dict(zip(
            FEATURES_MODELO, modelos["perfil"].feature_importances_.round(3)
        )),
    }


def _limitar_0_100(valor: float) -> int:
    """Garante que um score de risco fica sempre entre 0 e 100 (inteiro)."""
    return int(np.clip(round(valor), 0, 100))


def classificar_cliente(dados_cliente: dict, respostas_adaptativas: dict, modelos: dict) -> dict:
    """
    Classifica UM cliente, combinando a estimativa do modelo de ML com
    as regras de negocio explicitas -- o passo central do motor hibrido.

    Parameters
    ----------
    dados_cliente : dict com pelo menos idade, saldo_medio, rentabilidade
        e segmento_comercial (as mesmas colunas usadas no treino).
    respostas_adaptativas : dict pergunta -> resposta, vindo do
        Formulario Digital Adaptativo.
    modelos : dicionario devolvido por treinar_modelos().

    Devolve um dicionario com risco_aml, risco_credito, nivel_seguranca,
    perfil_estimado, e uma explicacao em linguagem simples (util ja para
    a Fase 5 -- Explicabilidade / XAI).
    """
    linha = pd.DataFrame([dados_cliente])
    X = preparar_features(linha)

    risco_aml_modelo = modelos["risco_aml"].predict(X)[0]
    risco_credito_modelo = modelos["risco_credito"].predict(X)[0]
    perfil_estimado = modelos["perfil"].predict(X)[0]

    ajuste_aml, ajuste_credito = calcular_ajustes_risco(respostas_adaptativas)

    risco_aml_final = _limitar_0_100(risco_aml_modelo + ajuste_aml)
    risco_credito_final = _limitar_0_100(risco_credito_modelo + ajuste_credito)

    nivel_seguranca = PERFIS[perfil_estimado]["nivel_seguranca"]

    # Regra de seguranca final: um "veto humano" sobre o modelo. Mesmo que
    # o perfil estimado seja de baixo risco, um risco final muito alto
    # forca sempre o nivel de seguranca mais critico.
    escalado = False
    if risco_aml_final >= LIMIAR_RISCO_CRITICO or risco_credito_final >= LIMIAR_RISCO_CRITICO:
        if nivel_seguranca != "Critico":
            nivel_seguranca = "Critico"
            escalado = True

    explicacao = [
        f"O modelo estimou Risco AML={round(risco_aml_modelo)} e "
        f"Risco de Credito={round(risco_credito_modelo)}, com base em clientes sinteticos parecidos.",
        f"O perfil mais semelhante encontrado pelo modelo foi '{perfil_estimado}'.",
    ]
    if ajuste_aml or ajuste_credito:
        explicacao.append(
            f"As regras de negocio ajustaram o risco em +{ajuste_aml} (AML) e +{ajuste_credito} "
            f"(Credito), com base nas respostas do formulario adaptativo."
        )
    if escalado:
        explicacao.append(
            f"O Nivel de Seguranca foi escalado para 'Critico' por regra de seguranca "
            f"(risco final >= {LIMIAR_RISCO_CRITICO}), independentemente do perfil estimado."
        )

    return {
        "risco_aml": risco_aml_final,
        "risco_credito": risco_credito_final,
        "nivel_seguranca": nivel_seguranca,
        "perfil_estimado": perfil_estimado,
        "explicacao": explicacao,
    }


def classificar_pendentes() -> list:
    """
    Encontra todos os clientes com nivel_seguranca = 'Pendente' (ou seja,
    registados via formulario mas ainda nao classificados), classifica-os
    um a um e atualiza a base de dados.

    Devolve uma lista de resultados (um dicionario por cliente
    classificado) -- util para mostrar feedback na interface (Fase 3.3).
    """
    pendentes = listar_pendentes()

    if pendentes.empty:
        return []

    modelos = treinar_modelos()
    resultados = []

    for _, cliente in pendentes.iterrows():
        id_cliente = int(cliente["id_cliente"])
        respostas = obter_respostas_adaptativas(id_cliente)

        dados_cliente = {
            "idade": cliente["idade"],
            "saldo_medio": cliente["saldo_medio"],
            "rentabilidade": cliente["rentabilidade"],
            "segmento_comercial": cliente["segmento_comercial"],
        }

        resultado = classificar_cliente(dados_cliente, respostas, modelos)

        atualizar_classificacao(
            id_cliente=id_cliente,
            risco_aml=resultado["risco_aml"],
            risco_credito=resultado["risco_credito"],
            nivel_seguranca=resultado["nivel_seguranca"],
        )

        resultados.append({
            "id_cliente": id_cliente,
            "nome": cliente["nome"],
            **resultado,
        })

    return resultados
