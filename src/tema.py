"""
Sentinel AI - Tema Visual Central (Dark Mode Premium)
Cores, emojis, CSS e componentes HTML reutilizados em VARIAS seccoes da
interface (Motor de Classificacao, Perfil Unico, Isolamento, Dashboard),
centralizados aqui para nunca ficarem inconsistentes entre seccoes.

RECONSTRUCAO: esta versao restaura todas as funcoes/constantes que o
app.py, dashboard_executivo.py e perfil_sentinel.py ja esperavam
encontrar aqui (ver assinaturas exatas usadas em cada chamada), depois
de uma versao anterior incompleta ter causado ImportError no arranque.
"""

# ---------------------------------------------------------------------------
# Paleta de cores
# ---------------------------------------------------------------------------
COR_FUNDO = "#0A0A10"
COR_FUNDO_CARTAO = "#14141C"
COR_TEXTO = "#F5F5F5"
COR_TEXTO_SECUNDARIO = "#B0B0B8"

COR_MARCA = "#FFCC00"          # dourado principal (botoes, destaques)
COR_MARCA_CLARA = "#FFDD77"    # dourado claro (preenchimentos, glow suave)
COR_MARCA_ESCURA = "#FFD700"

COR_TEAL = "#2DD4BF"           # acento secundario (graficos)
COR_AVISO = "#FFA630"          # amber/laranja de aviso
COR_SUCESSO = "#00E676"        # verde neon
COR_PERIGO = "#FF1744"         # vermelho neon

CORES_NIVEL_SEGURANCA = {
    "Baixo": COR_SUCESSO,
    "Medio": "#FFEA00",
    "Alto": "#FF9100",
    "Critico": COR_PERIGO,
}

EMOJI_NIVEL_SEGURANCA = {
    "Baixo": "🟢",
    "Medio": "🟡",
    "Alto": "🟠",
    "Critico": "🔴",
}


def emoji_nivel(nivel_seguranca: str) -> str:
    """Devolve o emoji correspondente a um Nivel de Seguranca (com fallback seguro)."""
    return EMOJI_NIVEL_SEGURANCA.get(nivel_seguranca, "⚪")


def cor_nivel(nivel_seguranca: str) -> str:
    """Devolve a cor hexadecimal correspondente a um Nivel de Seguranca (com fallback seguro)."""
    return CORES_NIVEL_SEGURANCA.get(nivel_seguranca, "#95A5A6")


# ---------------------------------------------------------------------------
# CSS global (injetado uma unica vez, no arranque do app.py)
# ---------------------------------------------------------------------------

def css_tema() -> str:
    """
    Devolve o bloco <style> completo do tema Dark Mode Premium: fundo
    com gradiente animado e glow dourado, cartoes com sombra luminosa,
    botoes com efeito de hover luminoso.
    """
    return f"""
    <style>
    .stApp {{
        background:
            radial-gradient(circle at 15% 20%, rgba(255, 204, 0, 0.10) 0%, transparent 45%),
            radial-gradient(circle at 85% 15%, rgba(255, 170, 0, 0.08) 0%, transparent 40%),
            radial-gradient(circle at 50% 90%, rgba(255, 215, 0, 0.06) 0%, transparent 50%),
            linear-gradient(180deg, {COR_FUNDO} 0%, #131318 50%, {COR_FUNDO} 100%);
        background-size: 200% 200%, 200% 200%, 200% 200%, 100% 100%;
        animation: sentinelGlowDrift 22s ease-in-out infinite;
    }}
    @keyframes sentinelGlowDrift {{
        0%   {{ background-position: 0% 0%, 100% 0%, 50% 100%, 0% 0%; }}
        50%  {{ background-position: 30% 30%, 70% 20%, 55% 85%, 0% 0%; }}
        100% {{ background-position: 0% 0%, 100% 0%, 50% 100%, 0% 0%; }}
    }}
    section[data-testid="stSidebar"] {{
        background-color: {COR_FUNDO_CARTAO};
        border-right: 1px solid rgba(255, 204, 0, 0.25);
    }}
    h1, h2, h3 {{ color: #FFFFFF !important; text-shadow: 0 0 12px rgba(255, 204, 0, 0.35); }}
    h1 {{ color: {COR_MARCA} !important; }}
    p, span, label {{ color: {COR_TEXTO}; }}
    div[data-testid="stMetric"] {{
        background: linear-gradient(145deg, {COR_FUNDO_CARTAO}, #15151C);
        border: 1px solid rgba(255, 204, 0, 0.35);
        border-radius: 14px;
        padding: 14px 18px;
        box-shadow: 0 0 18px rgba(255, 204, 0, 0.08), inset 0 0 20px rgba(0,0,0,0.3);
        transition: box-shadow 0.3s ease, transform 0.2s ease;
    }}
    div[data-testid="stMetric"]:hover {{
        box-shadow: 0 0 26px rgba(255, 204, 0, 0.28);
        transform: translateY(-2px);
    }}
    div[data-testid="stMetricLabel"] {{ color: {COR_TEXTO_SECUNDARIO} !important; }}
    div[data-testid="stMetricValue"] {{ color: {COR_MARCA} !important; }}
    div[data-testid="stExpander"] {{
        background-color: {COR_FUNDO_CARTAO};
        border: 1px solid rgba(255, 204, 0, 0.25);
        border-radius: 12px;
    }}
    .stButton > button {{
        background: linear-gradient(135deg, #FFD700, #FFAA00);
        color: #1A1A00;
        font-weight: 700;
        border: none;
        border-radius: 10px;
        padding: 0.6em 1.4em;
        box-shadow: 0 0 14px rgba(255, 204, 0, 0.35);
        transition: box-shadow 0.25s ease, transform 0.15s ease;
    }}
    .stButton > button:hover {{
        box-shadow: 0 0 28px rgba(255, 204, 0, 0.65), 0 0 50px rgba(255, 170, 0, 0.25);
        transform: translateY(-1px) scale(1.02);
        color: #000000;
    }}
    .stButton > button:active {{ transform: translateY(0) scale(0.99); }}
    hr {{
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,204,0,0.6), transparent);
        margin: 1.4em 0;
    }}
    .stSlider [role="slider"] {{ background-color: {COR_MARCA} !important; }}
    div[data-baseweb="select"] > div {{
        background-color: {COR_FUNDO_CARTAO};
        border-color: rgba(255, 204, 0, 0.35) !important;
    }}
    ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
    ::-webkit-scrollbar-track {{ background: {COR_FUNDO}; }}
    ::-webkit-scrollbar-thumb {{ background: rgba(255, 204, 0, 0.4); border-radius: 6px; }}

    /* --- Fase 1.5: Cabecalho Fixo Profissional --------------------------
       "sticky" (nao "fixed"): fica preso ao TOPO da area de conteudo do
       Streamlit enquanto o utilizador percorre a pagina, sem sobrepor a
       barra de ferramentas nativa do Streamlit (que vive fora desta area
       de scroll, por isso nunca ha conflito de z-index entre as duas). --- */
    .sentinel-header-fixo {{
        position: sticky;
        top: 0;
        z-index: 999;
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 10px 18px;
        background: rgba(10, 10, 16, 0.78);
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        border: 1px solid rgba(255, 204, 0, 0.22);
        border-radius: 16px;
        padding: 14px 22px;
        margin-bottom: 1.2rem;
        box-shadow: 0 10px 30px -16px rgba(255, 204, 0, 0.3);
    }}
    .sentinel-header-fixo .sentinel-header-titulo {{
        font-size: 1.55rem;
        font-weight: 800;
        color: {COR_MARCA} !important;
        text-shadow: 0 0 14px rgba(255, 204, 0, 0.35);
        line-height: 1.2;
        margin: 0;
    }}
    .sentinel-header-fixo .sentinel-header-subtitulo {{
        font-size: 0.85rem;
        color: {COR_TEXTO_SECUNDARIO};
        margin: 2px 0 0 0;
    }}
    .sentinel-header-fixo .sentinel-header-stats {{
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
    }}
    .sentinel-header-fixo .sentinel-header-pill {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255, 204, 0, 0.08);
        border: 1px solid rgba(255, 204, 0, 0.3);
        color: {COR_TEXTO};
        padding: 5px 14px;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 600;
        white-space: nowrap;
    }}
    @media (max-width: 640px) {{
        .sentinel-header-fixo {{ flex-direction: column; align-items: flex-start; }}
    }}
    </style>
    """


# ---------------------------------------------------------------------------
# Componentes HTML reutilizaveis (retornam string, para usar com
# st.markdown(..., unsafe_allow_html=True))
# ---------------------------------------------------------------------------

def cabecalho_fixo(titulo: str, subtitulo: str, emoji: str, n_clientes: int, n_pendentes: int) -> str:
    """
    Cabecalho fixo (sticky) do topo da app -- Fase 1.5 (Polimento Visual).

    Substitui o antigo par st.title()/st.caption() por uma faixa que
    permanece visivel enquanto o utilizador percorre a pagina, com o
    titulo da app e dois indicadores rapidos (total de clientes e
    pendentes de classificacao). Os numeros sao recebidos como
    parametros -- este componente nunca consulta a base de dados
    diretamente (isso e responsabilidade do app.py, que ja os calcula
    para os st.metric() mais abaixo).
    """
    return f"""
    <div class="sentinel-header-fixo">
        <div>
            <p class="sentinel-header-titulo">{emoji} {titulo}</p>
            <p class="sentinel-header-subtitulo">{subtitulo}</p>
        </div>
        <div class="sentinel-header-stats">
            <span class="sentinel-header-pill">👥 {n_clientes} clientes</span>
            <span class="sentinel-header-pill">⏳ {n_pendentes} pendente(s)</span>
        </div>
    </div>
    """


def badge_nivel(nivel_seguranca: str) -> str:
    """Pequena pilula colorida com o Nivel de Seguranca -- usada inline no texto."""
    cor = cor_nivel(nivel_seguranca)
    emoji = emoji_nivel(nivel_seguranca)
    return (
        f'<span style="background:{cor}22; border:1px solid {cor}; color:{cor}; '
        f'padding:3px 12px; border-radius:999px; font-weight:600; font-size:0.95em;">'
        f'{emoji} {nivel_seguranca}</span>'
    )


def cartao_antes_depois(titulo: str, corpo_html: str, cor: str, emoji: str = "", intenso: bool = False) -> str:
    """
    Cartao com glow colorido para a faixa dramatica ANTES/DEPOIS do
    Isolamento Inteligente. `intenso=True` da um glow mais forte (usado
    no cartao "DEPOIS", o lado positivo da comparacao).
    """
    intensidade_glow = "0 0 30px" if intenso else "0 0 16px"
    return f"""
    <div style="background: linear-gradient(145deg, {COR_FUNDO_CARTAO}, #15151C);
                border: 2px solid {cor}; border-radius: 14px; padding: 16px 18px;
                box-shadow: {intensidade_glow} {cor}55;">
        <strong style="color:{cor}; font-size:1.05em;">{emoji} {titulo}</strong><br>
        <span style="color:{COR_TEXTO};">{corpo_html}</span>
    </div>
    """


def cartao_papel(papel: str, emoji_papel: str, n_protegidos: int) -> str:
    """Cabecalho de cartao para cada papel (Gestor Comercial / Compliance) na simulação de isolamento."""
    cor = COR_PERIGO if n_protegidos > 0 else COR_SUCESSO
    return f"""
    <div style="border:2px solid {cor}; border-radius:10px; padding:10px 14px;
                margin-bottom:10px; background:{COR_FUNDO_CARTAO};
                box-shadow:0 0 14px {cor}33;">
        <strong style="color:{COR_TEXTO};">{emoji_papel} {papel}</strong>
        <span style="color:{cor}; font-weight:600;"> -- 🔒 {n_protegidos} campo(s) protegido(s)</span>
    </div>
    """


def linha_ficha(rotulo: str, valor: str, restrito: bool = False) -> str:
    """Uma linha (rotulo: valor) da ficha isolada. `restrito=True` destaca em vermelho neon."""
    if restrito:
        return (
            f'<div style="padding:4px 0; color:{COR_TEXTO_SECUNDARIO};"><strong>{rotulo}:</strong> '
            f'<span style="color:{COR_PERIGO}; font-weight:600;">{valor}</span></div>'
        )
    return f'<div style="padding:4px 0; color:{COR_TEXTO};"><strong>{rotulo}:</strong> {valor}</div>'


# ---------------------------------------------------------------------------
# Tema para graficos Plotly (usado por dashboard_executivo.py e perfil_sentinel.py)
# ---------------------------------------------------------------------------

def aplicar_tema_plotly(fig):
    """Aplica o tema dark mode a uma figura Plotly, de forma consistente em toda a app."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COR_TEXTO, family="Segoe UI, sans-serif"),
    )
    return fig
