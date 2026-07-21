"""
Sentinel AI - Camada de Acesso a Dados (Database Layer)
Fase 2: Funcoes de leitura e escrita na base de dados SQLite.

Este modulo e a UNICA parte do sistema que fala diretamente com o SQLite.
Todas as outras partes (formulario, dashboard, motor de classificacao, etc.)
devem passar por aqui. Isto chama-se "separacao de responsabilidades":
a logica de negocio nunca deve misturar-se com o acesso a dados.

Correcao pos-deploy (Streamlit Cloud): a base de dados e agora
"auto-suficiente" -- se a tabela 'clientes' nao existir (ex.: repositorio
clonado de novo, sem o ficheiro .db), a propria inicializar_schema()
cria a tabela E gera os 100 clientes sinteticos automaticamente. A app
deixa de depender de alguem ter corrido data_generator.py a mao, ou de
o ficheiro .db estar (ou nao) no GitHub.
"""

import os
import sqlite3
from pathlib import Path

import pandas as pd

# Caminho ABSOLUTO, calculado a partir da localizacao deste ficheiro --
# funciona sempre da mesma forma, seja qual for a pasta a partir de onde
# o Streamlit foi arrancado (isto era uma fonte de bugs: um caminho
# relativo como "database/sentinel.db" depende do diretorio de trabalho
# atual, que pode ser diferente entre o teu PC e o Streamlit Cloud).
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "sentinel.db"


def get_connection() -> sqlite3.Connection:
    """Abre uma ligacao a base de dados Sentinel, criando a pasta se preciso."""
    os.makedirs(DB_PATH.parent, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def _tabela_existe(conn: sqlite3.Connection, nome_tabela: str) -> bool:
    """Verifica se uma tabela existe na base de dados, consultando o catalogo do SQLite."""
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (nome_tabela,),
    )
    return cursor.fetchone() is not None


def _criar_e_popular_tabela_clientes(conn: sqlite3.Connection) -> None:
    """
    Garante que a tabela 'clientes' existe E tem dados.

    ISTO ERA O QUE FALTAVA: a versao anterior de inicializar_schema()
    nunca criava esta tabela -- assumia que o sentinel.db, ja com a
    tabela pronta, tinha sido copiado para o servidor. Em Streamlit
    Cloud isso falha sempre que o .db nao esta no repositorio Git (por
    exemplo, por estar no .gitignore).

    Se a tabela nao existir, criamo-la com o schema correto E
    populamo-la de imediato com os 100 clientes sinteticos -- a mesma
    lógica de data_generator.py, chamada aqui para que a app nunca
    fique "de pe, mas vazia e partida".
    """
    if _tabela_existe(conn, "clientes"):
        return

    # Import local (nao no topo do ficheiro): so precisamos do gerador
    # de dados sinteticos neste caso raro (primeira vez que a app corre
    # numa base de dados nova), nao em todos os pedidos normais.
    from data_generator import gerar_dataset

    conn.execute("""
        CREATE TABLE clientes (
            id_cliente INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            idade INTEGER,
            profissao TEXT,
            segmento_comercial TEXT,
            saldo_medio REAL,
            risco_aml INTEGER,
            risco_credito INTEGER,
            rentabilidade REAL,
            nivel_seguranca TEXT,
            perfil_origem TEXT,
            sentinel_index REAL
        )
    """)
    conn.commit()

    df = gerar_dataset(clientes_por_perfil=20)
    df.to_sql("clientes", conn, if_exists="append", index=False)
    conn.commit()
    print(f"[Sentinel AI] Tabela 'clientes' criada e populada com {len(df)} clientes sinteticos.")


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


def _garantir_coluna_sentinel_index(conn: sqlite3.Connection) -> None:
    """
    Garante que a coluna 'sentinel_index' existe na tabela clientes.

    Nota: a partir desta correcao, a tabela 'clientes' e sempre criada
    ja com esta coluna (ver _criar_e_popular_tabela_clientes), por isso
    esta funcao so entra em accao em bases de dados antigas, criadas
    antes desta correcao.
    """
    colunas_existentes = [
        linha[1] for linha in conn.execute("PRAGMA table_info(clientes)").fetchall()
    ]
    if "sentinel_index" not in colunas_existentes:
        conn.execute("ALTER TABLE clientes ADD COLUMN sentinel_index REAL")
        conn.commit()


def inicializar_schema() -> None:
    """
    Ponto UNICO e explicito de migracao/inicializacao do schema da base
    de dados. Deve ser chamada uma vez, no arranque do app.py -- antes
    de qualquer outra funcao deste modulo ser usada.

    Ordem importa: primeiro garantimos que 'clientes' existe (e tem
    dados), so depois tratamos da tabela de respostas e da coluna extra
    -- ambas dependem de 'clientes' ja existir.
    """
    conn = get_connection()
    _criar_e_popular_tabela_clientes(conn)
    _criar_tabela_respostas_adaptativas(conn)
    _garantir_coluna_sentinel_index(conn)
    conn.close()


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
