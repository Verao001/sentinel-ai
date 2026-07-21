from dataclasses import dataclass
from faker import Faker
import pandas as pd
import sqlite3
import random
import os

fake = Faker('pt_PT')
random.seed(42)

@dataclass
class ClienteSentinel:
    id_cliente: int
    nome: str
    idade: int
    segmento_comercial: str
    saldo: float
    transacoes_internacionais: int
    risco_aml: str
    risco_credito: str
    rentabilidade: str
    nivel_seguranca: str
    profissao: str

PERFIS = {
    "Premium Baixo Risco": {
        "idade": (35, 65),
        "saldo": (50000, 500000),
        "transacoes_int": (0, 5),
        "risco_aml": "Baixo",
        "risco_credito": "Baixo",
        "rentabilidade": "Alta",
        "nivel_seguranca": "Premium"
    },
    "Massa Média Estável": {
        "idade": (25, 55),
        "saldo": (5000, 50000),
        "transacoes_int": (0, 8),
        "risco_aml": "Baixo",
        "risco_credito": "Médio",
        "rentabilidade": "Média",
        "nivel_seguranca": "Base"
    },
    "Alto Risco AML": {
        "idade": (30, 60),
        "saldo": (10000, 150000),
        "transacoes_int": (15, 80),
        "risco_aml": "Alto",
        "risco_credito": "Alto",
        "rentabilidade": "Média",
        "nivel_seguranca": "Premium"
    },
    "Jovem Novo Cliente": {
        "idade": (18, 28),
        "saldo": (100, 8000),
        "transacoes_int": (0, 3),
        "risco_aml": "Médio",
        "risco_credito": "Alto",
        "rentabilidade": "Baixa",
        "nivel_seguranca": "Base"
    },
    "Institucional Alto Valor": {
        "idade": (40, 70),
        "saldo": (200000, 5000000),
        "transacoes_int": (10, 60),
        "risco_aml": "Médio",
        "risco_credito": "Baixo",
        "rentabilidade": "Alta",
        "nivel_seguranca": "Premium"
    }
}

def gerar_dataset(n_por_perfil=20):
    clientes = []
    for i, (perfil, config) in enumerate(PERFIS.items(), 1):
        for _ in range(n_por_perfil):
            cliente = ClienteSentinel(
                id_cliente=len(clientes) + 1,
                nome=fake.name(),
                idade=random.randint(*config["idade"]),
                segmento_comercial=perfil if perfil != "Institucional Alto Valor" else "Corporate",
                saldo=round(random.uniform(*config["saldo"]), 2),
                transacoes_internacionais=random.randint(*config["transacoes_int"]),
                risco_aml=config["risco_aml"],
                risco_credito=config["risco_credito"],
                rentabilidade=config["rentabilidade"],
                nivel_seguranca=config["nivel_seguranca"],
                profissao=fake.job()
            )
            clientes.append(cliente)
    
    df = pd.DataFrame([vars(c) for c in clientes])
    return df.sample(frac=1).reset_index(drop=True)

def salvar_dados(df):
    os.makedirs('../data', exist_ok=True)
    os.makedirs('../database', exist_ok=True)
    
    df.to_csv('../data/clientes_sinteticos.csv', index=False, encoding='utf-8')
    
    conn = sqlite3.connect('../database/sentinel.db')
    df.to_sql('clientes', conn, if_exists='replace', index=False)
    conn.close()

if __name__ == "__main__":
    print("Gerando dados sintéticos...")
    df = gerar_dataset(20)
    salvar_dados(df)
    print(f"[OK] {len(df)} clientes gerados com sucesso!")
    print("[OK] CSV salvo em: data/clientes_sinteticos.csv")
    print("[OK] Banco salvo em: database/sentinel.db")
