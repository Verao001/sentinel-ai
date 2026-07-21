"""
Sentinel AI - Gerador de Dados Sinteticos
Fase 1: Criacao de perfis de clientes sinteticos e contrastantes.

Este modulo gera dados ficticios (mas realistas) de clientes bancarios,
cobrindo 5 perfis muito diferentes entre si. Estes dados servem de
"materia-prima" para todas as fases seguintes do Sentinel AI
(classificacao multidimensional, Sentinel Index, isolamento de dados, etc).
"""

import sqlite3
import random
from dataclasses import dataclass, asdict
from pathlib import Path

import pandas as pd
from faker import Faker

# ---------------------------------------------------------------------------
# Configuracao geral
# ---------------------------------------------------------------------------

fake = Faker("pt_PT")  # Nomes, idades e dados pessoais em estilo portugues
random.seed(42)        # Torna os dados reproduziveis (mesmo resultado sempre)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_DIR = BASE_DIR / "database"

DATA_DIR.mkdir(exist_ok=True)
DB_DIR.mkdir(exist_ok=True)

CSV_PATH = DATA_DIR / "clientes_sinteticos.csv"
DB_PATH = DB_DIR / "sentinel.db"


# ---------------------------------------------------------------------------
# Estrutura de um Cliente Sentinel
# ---------------------------------------------------------------------------

@dataclass
class ClienteSentinel:
    id_cliente: int
    nome: str
    idade: int
    profissao: str
    segmento_comercial: str
    saldo_medio: float
    risco_aml: int          # 0-100 (quanto maior, mais suspeito)
    risco_credito: int      # 0-100 (quanto maior, mais arriscado)
    rentabilidade: float    # receita anual estimada gerada pelo cliente
    nivel_seguranca: str    # Baixo / Medio / Alto / Critico
    perfil_origem: str      # nome do perfil sintetico que originou o registo


# ---------------------------------------------------------------------------
# Definicao dos 5 perfis contrastantes
# ---------------------------------------------------------------------------
# Cada perfil combina VARIAS dimensoes ao mesmo tempo, de forma coerente.
# E essa combinacao multidimensional que o Sentinel AI vai aprender a
# reconhecer nas fases seguintes.

PERFIS = {
    "Premium Baixo Risco": dict(
        segmento_comercial="Private Banking",
        saldo_range=(500_000, 5_000_000),
        risco_aml_range=(0, 15),
        risco_credito_range=(0, 20),
        rentabilidade_range=(50_000, 300_000),
        nivel_seguranca="Baixo",
        profissoes=["Empresario", "Medico", "Advogado", "Diretor Executivo"],
    ),
    "Massa Media Estavel": dict(
        segmento_comercial="Retalho",
        saldo_range=(5_000, 80_000),
        risco_aml_range=(5, 30),
        risco_credito_range=(20, 45),
        rentabilidade_range=(1_000, 8_000),
        nivel_seguranca="Medio",
        profissoes=["Professor", "Enfermeiro", "Funcionario Publico", "Comerciante"],
    ),
    "Alto Risco AML": dict(
        segmento_comercial="Corporate",
        saldo_range=(100_000, 2_000_000),
        risco_aml_range=(70, 100),
        risco_credito_range=(30, 60),
        rentabilidade_range=(10_000, 150_000),
        nivel_seguranca="Critico",
        profissoes=["Importador/Exportador", "Consultor Offshore", "Cambio Informal"],
    ),
    "Jovem Novo Cliente": dict(
        segmento_comercial="Digital",
        saldo_range=(0, 3_000),
        risco_aml_range=(0, 20),
        risco_credito_range=(50, 80),
        rentabilidade_range=(0, 500),
        nivel_seguranca="Medio",
        profissoes=["Estudante", "Estagiario", "Freelancer"],
    ),
    "Institucional Alto Valor": dict(
        segmento_comercial="Corporate / Institucional",
        saldo_range=(2_000_000, 20_000_000),
        risco_aml_range=(10, 40),
        risco_credito_range=(5, 25),
        rentabilidade_range=(200_000, 1_500_000),
        nivel_seguranca="Alto",
        profissoes=["Fundo de Investimento", "Seguradora", "Multinacional"],
    ),
}


def _gerar_cliente(id_cliente: int, nome_perfil: str, config: dict) -> ClienteSentinel:
    """Gera um unico cliente sintetico a partir da configuracao de um perfil."""
    return ClienteSentinel(
        id_cliente=id_cliente,
        nome=fake.name(),
        idade=random.randint(19, 75),
        profissao=random.choice(config["profissoes"]),
        segmento_comercial=config["segmento_comercial"],
        saldo_medio=round(random.uniform(*config["saldo_range"]), 2),
        risco_aml=random.randint(*config["risco_aml_range"]),
        risco_credito=random.randint(*config["risco_credito_range"]),
        rentabilidade=round(random.uniform(*config["rentabilidade_range"]), 2),
        nivel_seguranca=config["nivel_seguranca"],
        perfil_origem=nome_perfil,
    )


def gerar_dataset(clientes_por_perfil: int = 20) -> pd.DataFrame:
    """
    Gera o dataset completo combinando os 5 perfis contrastantes.

    Parameters
    ----------
    clientes_por_perfil : quantos clientes sinteticos criar por perfil.
        20 clientes x 5 perfis = 100 clientes no total -- suficiente para
        demonstracoes e para treinar o modelo simples da Fase 3.
    """
    clientes = []
    id_atual = 1

    for nome_perfil, config in PERFIS.items():
        for _ in range(clientes_por_perfil):
            cliente = _gerar_cliente(id_atual, nome_perfil, config)
            clientes.append(asdict(cliente))
            id_atual += 1

    df = pd.DataFrame(clientes)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)  # embaralha
    return df


def salvar_csv(df: pd.DataFrame) -> None:
    df.to_csv(CSV_PATH, index=False, encoding="utf-8")
    print(f"[OK] CSV guardado em: {CSV_PATH}")


def salvar_sqlite(df: pd.DataFrame) -> None:
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("clientes", conn, if_exists="replace", index=False)
    conn.close()
    print(f"[OK] Base de dados SQLite guardada em: {DB_PATH}")


def main():
    print("A gerar dados sinteticos do Sentinel AI...")
    df = gerar_dataset(clientes_por_perfil=20)
    salvar_csv(df)
    salvar_sqlite(df)
    print("\nResumo por perfil:")
    print(df["perfil_origem"].value_counts())
    print(f"\nTotal de clientes gerados: {len(df)}")


if __name__ == "__main__":
    main()
