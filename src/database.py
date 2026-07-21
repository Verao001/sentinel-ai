"""
Sentinel AI - Camada de Acesso a Dados (Database Layer)
Fase 2: Funcoes de leitura e escrita na base de dados SQLite.

Este modulo e a UNICA parte do sistema que fala diretamente com o SQLite.
Todas as outras partes (formulario, dashboard, motor de classificacao, etc.)
devem passar por aqui. Isto chama-se "separacao de responsabilidades":
a logica de negocio nunca deve misturar-se com o acesso a dados.
"""

import sqlite3
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "sentinel.db"


import sqlite3
import os

# Caminho simples e confiável para Streamlit Cloud
DB_PATH = "database/sentinel.db"

def get_connection() -> sqlite3.Connection:
    """Abre uma ligação à base de dados Sentinel."""
    # Garante que a pasta existe
    os.makedirs("database", exist_ok=True)
    return sqlite3.connect(DB_PATH)


def _criar_tabela_respostas_adaptativas(conn: sqlite3.Connection) -> None:
    """
    Cria a tabela que guarda as respostas do formulario adaptativo.

    Porque uma tabela separada e nao colunas soltas na tabela 'clientes'?
    Porque cada segmento comercial tem perguntas DIFERENTES. Se
    tentassemos guardar tudo na mesma tabela, terminariamos com dezenas
    de colunas vazias (NULL) para a maioria dos clientes. Uma tabela
    "pergunta / resposta" e flexivel e escala para novos segmentos sem
    alterar a estrutura da base de dados.
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS respostas_adaptativas (
            id_resposta INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente INTEGER NOT NULL,
            pergunta TEXT NOT NULL,
            resposta TEXT NOT NULL,
            FOREIGN KEY (id_cliente) REFERENCES clientes (id_cliente)
        )
    """)
    conn.commit()


def obter_proximo_id(conn: sqlite3.Connection) -> int:
    """Calcula o proximo id_cliente disponivel (MAX + 1)."""
    cursor = conn.execute("SELECT MAX(id_cliente) FROM clientes")
    resultado = cursor.fetchone()[0]
    return (resultado or 0) + 1


def inserir_cliente(dados_cliente: dict) -> int:
    """
    Insere um novo cliente vindo do Formulario Digital Adaptativo.

    Nota: risco_aml, risco_credito e nivel_seguranca ficam pendentes
    porque ainda nao foram calculados -- isso e trabalho do Motor de
    Classificacao Multidimensional (Fase 3).
    """
    conn = get_connection()
    _criar_tabela_respostas_adaptativas(conn)

    novo_id = obter_proximo_id(conn)

    conn.execute("""
        INSERT INTO clientes (
            id_cliente, nome, idade, profissao, segmento_comercial,
            saldo_medio, risco_aml, risco_credito, rentabilidade,
            nivel_seguranca, perfil_origem
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        novo_id,
        dados_cliente["nome"],
        dados_cliente["idade"],
        dados_cliente["profissao"],
        dados_cliente["segmento_comercial"],
        dados_cliente["saldo_medio"],
        None,  # risco_aml -- calculado na Fase 3
        None,  # risco_credito -- calculado na Fase 3
        dados_cliente["rentabilidade"],
        "Pendente",  # nivel_seguranca -- calculado na Fase 3
        "Formulario Manual",
    ))

    conn.commit()
    conn.close()
    return novo_id


def inserir_respostas_adaptativas(id_cliente: int, respostas: dict) -> None:
    """Guarda as respostas especificas do segmento escolhido no formulario."""
    conn = get_connection()
    _criar_tabela_respostas_adaptativas(conn)

    for pergunta, resposta in respostas.items():
        conn.execute("""
            INSERT INTO respostas_adaptativas (id_cliente, pergunta, resposta)
            VALUES (?, ?, ?)
        """, (id_cliente, pergunta, str(resposta)))

    conn.commit()
    conn.close()


def listar_clientes(limite: int = 10) -> pd.DataFrame:
    """Devolve os ultimos N clientes inseridos (mais recentes primeiro)."""
    conn = get_connection()
    df = pd.read_sql_query(f"""
        SELECT * FROM clientes
        ORDER BY id_cliente DESC
        LIMIT {limite}
    """, conn)
    conn.close()
    return df


def contar_clientes() -> int:
    """Conta quantos clientes existem atualmente na base de dados."""
    conn = get_connection()
    cursor = conn.execute("SELECT COUNT(*) FROM clientes")
    total = cursor.fetchone()[0]
    conn.close()
    return total


# ---------------------------------------------------------------------------
# Funcoes adicionadas na Fase 3: apoio ao Motor de Classificacao
# ---------------------------------------------------------------------------

def obter_dados_treino() -> pd.DataFrame:
    """
    Devolve os clientes que servem de "professores" para o modelo de ML:
    os 100 clientes sinteticos da Fase 1, que ja tem risco_aml,
    risco_credito e perfil_origem conhecidos. Clientes vindos do
    formulario manual NUNCA entram no treino -- ainda nao tem risco
    conhecido (estao "Pendente"), por isso nao podem ensinar nada ao
    modelo.
    """
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT * FROM clientes
        WHERE perfil_origem != 'Formulario Manual'
          AND risco_aml IS NOT NULL
          AND risco_credito IS NOT NULL
    """, conn)
    conn.close()
    return df


def listar_pendentes() -> pd.DataFrame:
    """Devolve os clientes ainda por classificar (nivel_seguranca = 'Pendente')."""
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT * FROM clientes
        WHERE nivel_seguranca = 'Pendente'
    """, conn)
    conn.close()
    return df


def obter_respostas_adaptativas(id_cliente: int) -> dict:
    """Devolve as respostas do formulario adaptativo de um cliente, como dicionario."""
    conn = get_connection()
    _criar_tabela_respostas_adaptativas(conn)
    cursor = conn.execute("""
        SELECT pergunta, resposta FROM respostas_adaptativas
        WHERE id_cliente = ?
    """, (id_cliente,))
    respostas = {pergunta: resposta for pergunta, resposta in cursor.fetchall()}
    conn.close()
    return respostas


def atualizar_classificacao(id_cliente: int, risco_aml: int, risco_credito: int, nivel_seguranca: str) -> None:
    """
    Atualiza os campos de risco de um cliente depois de classificado
    pelo Motor de Classificacao Multidimensional (Fase 3).
    """
    conn = get_connection()
    conn.execute("""
        UPDATE clientes
        SET risco_aml = ?, risco_credito = ?, nivel_seguranca = ?
        WHERE id_cliente = ?
    """, (risco_aml, risco_credito, nivel_seguranca, id_cliente))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Funcoes adicionadas na Fase 4: apoio ao Sentinel Index
# ---------------------------------------------------------------------------

def _garantir_coluna_sentinel_index(conn: sqlite3.Connection) -> None:
    """
    Garante que a coluna 'sentinel_index' existe na tabela clientes.

    IMPORTANTE (licao da Fase 2): esta funcao e deliberadamente PRIVADA
    e so e chamada por inicializar_schema(), que por sua vez so corre
    quando o app.py a chama explicitamente no arranque. Nunca corre
    escondida so por importares este modulo -- isso e o que causou
    o problema anterior com outro assistente.
    """
    colunas_existentes = [
        linha[1] for linha in conn.execute("PRAGMA table_info(clientes)").fetchall()
    ]
    if "sentinel_index" not in colunas_existentes:
        conn.execute("ALTER TABLE clientes ADD COLUMN sentinel_index REAL")
        conn.commit()


def inicializar_schema() -> None:
    """
    Ponto UNICO e explicito de migracao do schema da base de dados.

    Deve ser chamada uma vez, no arranque do app.py -- nunca a
    escondidas dentro de outra funcao "por seguranca". Se no futuro
    precisares de adicionar mais colunas ou tabelas, adiciona-as aqui,
    de forma visivel e documentada.
    """
    conn = get_connection()
    _criar_tabela_respostas_adaptativas(conn)
    _garantir_coluna_sentinel_index(conn)
    conn.close()


def listar_classificados() -> pd.DataFrame:
    """
    Devolve os clientes ja classificados pelo Motor de Classificacao
    (nivel_seguranca != 'Pendente') -- inclui tanto os 100 clientes
    sinteticos como qualquer cliente do formulario ja classificado.
    """
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT * FROM clientes
        WHERE nivel_seguranca != 'Pendente'
    """, conn)
    conn.close()
    return df


def obter_cliente_por_id(id_cliente: int) -> pd.Series | None:
    """
    Devolve os dados de UM cliente especifico (usado pela Fase 5 -- Perfil
    Unico Sentinel). Devolve None se o id nao existir, para que quem chama
    possa tratar esse caso sem rebentar a aplicacao.
    """
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT * FROM clientes WHERE id_cliente = ?
    """, conn, params=(id_cliente,))
    conn.close()
    if df.empty:
        return None
    return df.iloc[0]


def atualizar_sentinel_index(id_cliente: int, valor: float) -> None:
    """Grava o Sentinel Index calculado para um cliente especifico."""
    conn = get_connection()
    conn.execute("""
        UPDATE clientes
        SET sentinel_index = ?
        WHERE id_cliente = ?
    """, (valor, id_cliente))
    conn.commit()
    conn.close()
