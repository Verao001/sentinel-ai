"""
Sentinel AI - Tema Visual Central
Fase 8 (Polimento para apresentacao): cores e emojis usados em VARIAS
seccoes da interface (Motor de Classificacao, Perfil Unico, Isolamento,
Dashboard), centralizados aqui para nunca ficarem inconsistentes entre
seccoes -- antes desta mudanca, a mesma paleta estava duplicada em 3
sitios diferentes do app.py e do dashboard_executivo.py.
"""

# Paleta profissional: verde/amarelo/laranja/vermelho -- a mesma
# linguagem visual usada em relatorios de risco bancario reais.
CORES_NIVEL_SEGURANCA = {
    "Baixo": "#10AC84",
    "Medio": "#F6C90E",
    "Alto": "#F39C12",
    "Critico": "#E74C3C",
}

EMOJI_NIVEL_SEGURANCA = {
    "Baixo": "🟢",
    "Medio": "🟡",
    "Alto": "🟠",
    "Critico": "🔴",
}

# Cor de destaque da marca Sentinel, usada nos graficos e nos cabecalhos.
COR_MARCA = "#2E86DE"
COR_MARCA_ESCURA = "#1B4F72"


def emoji_nivel(nivel_seguranca: str) -> str:
    """Devolve o emoji correspondente a um Nivel de Seguranca (com fallback seguro)."""
    return EMOJI_NIVEL_SEGURANCA.get(nivel_seguranca, "⚪")


def cor_nivel(nivel_seguranca: str) -> str:
    """Devolve a cor hexadecimal correspondente a um Nivel de Seguranca (com fallback seguro)."""
    return CORES_NIVEL_SEGURANCA.get(nivel_seguranca, "#95A5A6")
