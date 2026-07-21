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
    conn = sqlite3.connect(DB_PATH, timeout=10)
    # Se outra ligacao estiver a escrever no mesmo instante (ex.: dois
    # utilizadores a abrir a app ao mesmo tempo no Streamlit Cloud),
    # espera ate 5s em vez de falhar logo com "database is locked".
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


def _criar_e_popular_tabela_clientes(conn: sqlite3.Connection) -> None:
    """
    Garante que a tabela 'clientes' existe E tem dados -- de forma segura
    mesmo que duas sessoes (ex.: dois separadores do browser, ou um
    health-check do Streamlit Cloud a correr ao mesmo tempo que o
    utilizador real) cheguem aqui exatamente ao mesmo tempo no primeiro
    arranque.

    Duas protecoes contra a corrida:
      1. 'CREATE TABLE IF NOT EXISTS' em vez de 'CREATE TABLE' -- nunca
         falha so porque outra ligacao ja criou a tabela entretanto.
      2. So populamos com os 100 clientes sinteticos se a tabela estiver
         mesmo vazia (COUNT == 0) -- e mesmo assim, se outra ligacao
         'ganhar a corrida' e inserir primeiro, apanhamos o erro de
         chave duplicada e ignoramo-lo (o resultado final e o mesmo:
         a tabela fica com os clientes, nao importa qual ligacao os
         inseriu).
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
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

    total_atual = conn.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
    if total_atual > 0:
        return

    # Import local: so precisamos do gerador de dados sinteticos neste
    # caso raro (primeira vez que a app corre numa base de dados nova).
    from data_generator import gerar_dataset

    df = gerar_dataset(clientes_por_perfil=20)
    try:
        df.to_sql("clientes", conn, if_exists="append", index=False)
        conn.commit()
        print(f"[Sentinel AI] Tabela 'clientes' criada e populada com {len(df)} clientes sinteticos.")
    except sqlite3.IntegrityError:
        # Outra ligacao ja inseriu os mesmos clientes entretanto -- nao
        # ha nada de errado, so significa que perdemos a corrida.
        conn.rollback()


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
        try:
            conn.execute("ALTER TABLE clientes ADD COLUMN sentinel_index REAL")
            conn.commit()
        except sqlite3.OperationalError as erro:
            # Outra ligacao concorrente ja adicionou a coluna entre o
            # PRAGMA acima e este ALTER TABLE -- nao ha nada de errado.
            if "duplicate column" not in str(erro).lower():
                raise


def inicializar_schema() -> None:
    """
    Ponto UNICO e explicito de migracao/inicializacao do schema da base
    de dados. Deve ser chamada uma vez, no arranque do app.py -- antes
    de qualquer outra funcao deste modulo ser usada.

    Cada etapa esta protegida com o seu proprio try/except: em teoria,
    'CREATE TABLE IF NOT EXISTS' e afins ja deveriam ser seguros sozinhos,
    mas na pratica o SQLite pode devolver erros transitorios quando
    varias sessoes do Streamlit Cloud tentam inicializar a base de dados
    exatamente ao mesmo tempo (ex.: um health-check automatico e um
    investidor a abrir a app no telemovel, no mesmo segundo). Preferimos
    registar um aviso na consola a deixar a app inteira mostrar uma
    pagina de erro por causa de uma corrida que se resolve sozinha.
    """
    conn = get_connection()

    try:
        _criar_e_popular_tabela_clientes(conn)
    except Exception as erro:  # noqa: BLE001 -- intencional: nunca deixar isto derrubar a app
        print(f"[Sentinel AI] Aviso ao inicializar 'clientes' (ignorado, provavel corrida): {erro}")

    try:
        _criar_tabela_respostas_adaptativas(conn)
    except Exception as erro:  # noqa: BLE001
        print(f"[Sentinel AI] Aviso ao inicializar 'respostas_adaptativas' (ignorado): {erro}")

    try:
        _garantir_coluna_sentinel_index(conn)
    except Exception as erro:  # noqa: BLE001
        print(f"[Sentinel AI] Aviso ao garantir coluna 'sentinel_index' (ignorado): {erro}")

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
    try:
        cursor = conn.execute("SELECT COUNT(*) FROM clientes")
        total = cursor.fetchone()[0]
    except sqlite3.OperationalError:
        # Ainda nao havia tabela no instante exato desta leitura (corrida
        # rara no primeiro arranque) -- garante o schema aqui mesmo e
        # tenta novamente, em vez de deixar a pagina inteira crashar.
        conn.close()
        inicializar_schema()
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
