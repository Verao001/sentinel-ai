"""
Sentinel AI - Tema Visual Central
Fase 10 (Refinamento Premium): glassmorphism, dourado suave + verde-azulado,
profundidade em camadas e micro-animacoes de entrada -- o nivel visual de
produtos como Linear, Vercel ou ngrok, em vez de um "dark mode generico".

Este modulo continua a ser o UNICO sitio onde cores, tokens de design e
"componentes" HTML reutilizaveis vivem. Nada de logica de negocio aqui --
so aparencia.
"""

# ---------------------------------------------------------------------------
# Paleta -- dourado suave e luminoso (nunca saturado) + verde-azulado
# ---------------------------------------------------------------------------

CORES_NIVEL_SEGURANCA = {
    "Baixo": "#3FD6B8",     # verde-azulado suave (em vez de verde puro)
    "Medio": "#FFDD77",     # dourado claro
    "Alto": "#FFB25E",      # ambar/laranja suave
    "Critico": "#FF6B6B",   # vermelho suave, sem ser garrido
}

EMOJI_NIVEL_SEGURANCA = {
    "Baixo": "🟢",
    "Medio": "🟡",
    "Alto": "🟠",
    "Critico": "🔴",
}

# Dourado -- agora deliberadamente mais claro e "leve" do que um amarelo puro.
COR_MARCA = "#FFDD77"           # dourado principal (acentos, titulos, botoes)
COR_MARCA_CLARA = "#FFEEAA"     # quase creme dourado -- hover, brilho
COR_MARCA_ESCURA = "#E8B93E"    # dourado mais profundo -- gradientes, sombras
COR_MARCA_ACENTO = "#FFCC33"    # ponto de luz mais intenso, usado com moderacao

# Segunda cor de destaque -- verde-azulado, para dar profundidade e evitar
# que tudo fique "so amarelo" (o pedido explicito de "verde-azulado suave").
COR_TEAL = "#3FD6B8"
COR_TEAL_ESCURO = "#1E8F7A"

# Fundo e superficies -- pretos com undertone quente, nunca preto puro
BG_VOID = "#06060A"
BG_BASE = "#0A0A10"
BG_ELEVADO = "rgba(24, 24, 32, 0.55)"        # vidro fosco (glass)
BG_ELEVADO_SOLIDO = "#15151C"                 # fallback sem blur (sidebar, etc.)
BG_ELEVADO_HOVER = "rgba(32, 32, 42, 0.7)"
BORDA_SUBTIL = "rgba(255,255,255,0.09)"
BORDA_GOLD = "rgba(255,221,119,0.4)"
BORDA_GOLD_FORTE = "rgba(255,221,119,0.7)"

TEXTO_PRIMARIO = "#F5F1E8"
TEXTO_SECUNDARIO = "#A9A8B8"
TEXTO_MUTED = "#6E6D7A"

COR_SUCESSO = "#3FD6B8"
COR_PERIGO = "#FF6B6B"
COR_AVISO = "#FFB25E"
COR_INFO = "#6FB7E8"


def emoji_nivel(nivel_seguranca: str) -> str:
    """Devolve o emoji correspondente a um Nivel de Seguranca (com fallback seguro)."""
    return EMOJI_NIVEL_SEGURANCA.get(nivel_seguranca, "⚪")


def cor_nivel(nivel_seguranca: str) -> str:
    """Devolve a cor hexadecimal correspondente a um Nivel de Seguranca (com fallback seguro)."""
    return CORES_NIVEL_SEGURANCA.get(nivel_seguranca, "#95A5A6")


def cor_nivel_rgba(nivel_seguranca: str, alfa: float = 0.18) -> str:
    """Versao translucida da cor de um nivel -- usada em glows e fundos de cartao."""
    hexa = cor_nivel(nivel_seguranca).lstrip("#")
    r, g, b = int(hexa[0:2], 16), int(hexa[2:4], 16), int(hexa[4:6], 16)
    return f"rgba({r},{g},{b},{alfa})"


# ---------------------------------------------------------------------------
# Plotly -- layout base partilhado por todos os graficos da aplicacao
# ---------------------------------------------------------------------------

PLOTLY_LAYOUT_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, -apple-system, sans-serif", color=TEXTO_SECUNDARIO, size=12),
    title_font=dict(color=TEXTO_PRIMARIO),
    legend=dict(font=dict(color=TEXTO_SECUNDARIO)),
    xaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.1)", color=TEXTO_SECUNDARIO),
    yaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.1)", color=TEXTO_SECUNDARIO),
)


def aplicar_tema_plotly(fig):
    """Aplica o tema (fundo transparente, grelha subtil, texto claro) a UMA figura Plotly ja construida."""
    fig.update_layout(**PLOTLY_LAYOUT_BASE)
    return fig


# ---------------------------------------------------------------------------
# Componentes HTML reutilizaveis -- todos em "vidro fosco"
# ---------------------------------------------------------------------------

def badge_nivel(nivel_seguranca: str) -> str:
    """Pilula de vidro com o emoji + nome do nivel de seguranca, com glow proprio."""
    cor = cor_nivel(nivel_seguranca)
    return (
        f'<span style="display:inline-flex;align-items:center;gap:6px;'
        f'background:{cor_nivel_rgba(nivel_seguranca, 0.14)};color:{cor};'
        f'border:1px solid {cor_nivel_rgba(nivel_seguranca, 0.5)};'
        f'padding:4px 14px;border-radius:999px;font-size:0.85rem;font-weight:600;'
        f'box-shadow:0 0 18px -4px {cor_nivel_rgba(nivel_seguranca, 0.55)};'
        f'backdrop-filter:blur(6px);">'
        f'{emoji_nivel(nivel_seguranca)} {nivel_seguranca}</span>'
    )


def badge_restrito() -> str:
    """Pilula 'Acesso Restrito' usada no Isolamento Inteligente de Dados."""
    return (
        f'<span style="display:inline-flex;align-items:center;gap:6px;'
        f'background:rgba(255,107,107,0.1);color:{COR_PERIGO};'
        f'border:1px solid rgba(255,107,107,0.4);'
        f'padding:2px 10px;border-radius:999px;font-size:0.82rem;font-weight:600;'
        f'box-shadow:0 0 14px -4px rgba(255,107,107,0.4);">'
        f'🔒 Acesso Restrito</span>'
    )


def linha_ficha(rotulo: str, valor: str, restrito: bool = False) -> str:
    """Uma linha 'rotulo: valor' da ficha do cliente, pronta para st.markdown."""
    valor_html = badge_restrito() if restrito else f'<span style="color:{TEXTO_PRIMARIO};font-weight:500;">{valor}</span>'
    return (
        f'<div style="display:flex;justify-content:space-between;align-items:center;'
        f'padding:8px 4px;border-bottom:1px solid {BORDA_SUBTIL};font-size:0.92rem;">'
        f'<span style="color:{TEXTO_SECUNDARIO};">{rotulo}</span>{valor_html}</div>'
    )


def cartao_antes_depois(titulo: str, texto: str, cor: str, emoji: str, intenso: bool = False) -> str:
    """
    Cartao 'ANTES / DEPOIS' -- vidro fosco, borda luminosa e uma sobreposicao
    de luz diagonal subtil (pseudo-elemento) para dar sensacao de profundidade
    e drama, sem depender de nenhuma imagem externa.
    """
    escala = "scale(1.015)" if intenso else "scale(1)"
    return f"""
    <div class="sentinel-fade-in" style="position:relative; overflow:hidden;
                background:linear-gradient(160deg, rgba(255,255,255,0.045) 0%, rgba(255,255,255,0.01) 100%),
                           {BG_ELEVADO};
                backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px);
                border:1px solid {cor}4D; border-left:3px solid {cor};
                border-radius:18px; padding:22px 24px; height:100%;
                box-shadow:0 8px 32px -12px {cor}55, inset 0 1px 0 rgba(255,255,255,0.06);
                transform:{escala}; transition: all 0.35s ease;">
        <div style="position:absolute; top:-40%; right:-20%; width:70%; height:180%;
                    background:radial-gradient(circle, {cor}22, transparent 65%);
                    pointer-events:none;"></div>
        <div style="position:relative; color:{cor};font-weight:700;font-size:0.98rem;
                    margin-bottom:8px;letter-spacing:-0.01em;">
            {emoji} {titulo}
        </div>
        <div style="position:relative; color:{TEXTO_SECUNDARIO};font-size:0.93rem;line-height:1.6;">{texto}</div>
    </div>
    """


def cartao_papel(papel: str, emoji: str, n_protegidos: int) -> str:
    """Cabecalho de vidro fosco do cartao de cada 'papel' (Gestor Comercial / Compliance)."""
    cor = COR_PERIGO if n_protegidos > 0 else COR_SUCESSO
    return f"""
    <div class="sentinel-fade-in" style="border:1px solid {cor}4D; border-radius:14px; padding:14px 18px;
                margin-bottom:12px; background:linear-gradient(135deg, {cor}1A, {BG_ELEVADO});
                backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
                box-shadow:0 6px 24px -10px {cor}66, inset 0 1px 0 rgba(255,255,255,0.05);">
        <span style="font-weight:700;color:{TEXTO_PRIMARIO};">{emoji} {papel}</span>
        <span style="float:right;color:{cor};font-weight:600;">🔒 {n_protegidos} campo(s) protegido(s)</span>
    </div>
    """


def cartao_vidro(conteudo_html: str, glow: str = None) -> str:
    """
    Cartao de vidro fosco generico -- envolve qualquer bloco de HTML (usado,
    por exemplo, para agrupar texto livre com o mesmo acabamento dos outros
    cartoes da aplicacao).
    """
    cor_glow = glow or COR_MARCA
    return f"""
    <div class="sentinel-fade-in" style="background:{BG_ELEVADO}; backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px); border:1px solid {BORDA_SUBTIL};
                border-radius:16px; padding:20px 22px;
                box-shadow:0 8px 30px -14px {cor_glow}55, inset 0 1px 0 rgba(255,255,255,0.05);">
        {conteudo_html}
    </div>
    """


# ---------------------------------------------------------------------------
# CSS global -- injetado uma unica vez em app.py
# ---------------------------------------------------------------------------

def css_tema() -> str:
    """
    Devolve o bloco <style> completo do tema Premium Glass. Continua a ser
    uma funcao (nao uma constante solta) para ser injetada de forma
    explicita em app.py -- nada acontece "escondido" so por importar este
    modulo.
    """
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    :root {{
        --gold: {COR_MARCA};
        --gold-light: {COR_MARCA_CLARA};
        --gold-deep: {COR_MARCA_ESCURA};
        --gold-accent: {COR_MARCA_ACENTO};
        --teal: {COR_TEAL};
        --bg-void: {BG_VOID};
        --bg-base: {BG_BASE};
        --bg-elev: {BG_ELEVADO};
        --bg-elev-solid: {BG_ELEVADO_SOLIDO};
        --bg-elev-hover: {BG_ELEVADO_HOVER};
        --border-subtle: {BORDA_SUBTIL};
        --border-gold: {BORDA_GOLD};
        --border-gold-strong: {BORDA_GOLD_FORTE};
        --text-primary: {TEXTO_PRIMARIO};
        --text-secondary: {TEXTO_SECUNDARIO};
        --text-muted: {TEXTO_MUTED};
    }}

    * {{ scroll-behavior: smooth; }}

    html, body, [data-testid="stAppViewContainer"], .stApp {{
        background-color: var(--bg-base) !important;
        color: var(--text-primary);
        font-family: 'Inter', -apple-system, sans-serif;
    }}

    /* --- Fundo em camadas: gradiente escuro de base + manchas de luz
       douradas e verde-azuladas, muito suaves, que se fundem lentamente --- */
    [data-testid="stAppViewContainer"]::before {{
        content: "";
        position: fixed;
        inset: 0;
        z-index: 0;
        pointer-events: none;
        background:
            radial-gradient(ellipse 1000px 600px at 8% -10%, rgba(255,221,119,0.14), transparent 60%),
            radial-gradient(ellipse 800px 550px at 100% 8%, rgba(63,214,184,0.10), transparent 60%),
            radial-gradient(ellipse 700px 500px at 45% 105%, rgba(255,204,51,0.08), transparent 60%),
            radial-gradient(ellipse 600px 500px at 90% 100%, rgba(63,214,184,0.06), transparent 60%),
            linear-gradient(180deg, var(--bg-void) 0%, var(--bg-base) 45%, var(--bg-void) 100%);
        background-color: var(--bg-base);
    }}

    /* Textura fina de grao/grelha para sensacao "premium tech" (bem subtil) */
    [data-testid="stAppViewContainer"]::after {{
        content: "";
        position: fixed;
        inset: 0;
        z-index: 0;
        pointer-events: none;
        opacity: 0.4;
        background-image:
            linear-gradient(rgba(255,255,255,0.012) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.012) 1px, transparent 1px);
        background-size: 42px 42px;
    }}

    [data-testid="stHeader"] {{
        background: rgba(6,6,10,0.55) !important;
        backdrop-filter: blur(10px);
        border-bottom: 1px solid var(--border-subtle);
    }}

    section.main > div {{ position: relative; z-index: 1; }}

    /* --- Micro-animacao de entrada: fade + subtle scale-up --- */
    @keyframes sentinelFadeInUp {{
        from {{ opacity: 0; transform: translateY(14px) scale(0.99); }}
        to   {{ opacity: 1; transform: translateY(0) scale(1); }}
    }}
    .sentinel-fade-in {{ animation: sentinelFadeInUp 0.55s cubic-bezier(0.22,1,0.36,1) both; }}

    div[data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="stExpander"],
    div[data-testid="stMetric"],
    [data-testid="stPlotlyChart"],
    [data-testid="stDataFrame"] {{
        animation: sentinelFadeInUp 0.6s cubic-bezier(0.22,1,0.36,1) both;
    }}

    /* --- Sidebar --- */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #08080C 0%, #0E0E14 100%);
        border-right: 1px solid var(--border-subtle);
    }}
    [data-testid="stSidebar"] * {{ color: var(--text-secondary); }}
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
        color: var(--gold) !important;
    }}

    /* --- Titulos --- */
    h1, h2, h3 {{
        color: var(--text-primary) !important;
        font-weight: 700;
        letter-spacing: -0.02em;
    }}
    h1 {{
        background: linear-gradient(90deg, var(--gold-light) 0%, var(--gold) 40%, var(--teal) 130%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        filter: drop-shadow(0 0 22px rgba(255,221,119,0.22));
        display: inline-block;
        padding-bottom: 4px;
    }}
    h2, h3 {{
        border-left: 3px solid var(--gold);
        padding-left: 12px;
        margin-top: 0.6em;
    }}

    p, li, span, label, .stCaption, [data-testid="stCaptionContainer"] {{
        color: var(--text-secondary);
    }}
    [data-testid="stMarkdownContainer"] strong {{ color: var(--text-primary); }}

    /* --- Cartoes de layout (containers com borda do Streamlit) --- */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: var(--bg-elev);
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        border: 1px solid var(--border-subtle);
        border-radius: 18px;
    }}

    /* --- Metricas: vidro fosco com glow dourado no hover --- */
    div[data-testid="stMetric"] {{
        background: var(--bg-elev);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--border-subtle);
        border-radius: 16px;
        padding: 16px 20px;
        transition: all 0.3s cubic-bezier(0.22,1,0.36,1);
    }}
    div[data-testid="stMetric"]:hover {{
        border-color: var(--border-gold-strong);
        box-shadow: 0 12px 40px -14px rgba(255,221,119,0.4), 0 0 0 1px rgba(255,221,119,0.15) inset;
        transform: translateY(-3px);
    }}
    [data-testid="stMetricValue"] {{
        font-family: 'JetBrains Mono', monospace;
        color: var(--gold) !important;
        font-weight: 700;
        text-shadow: 0 0 20px rgba(255,221,119,0.3);
    }}
    [data-testid="stMetricLabel"] {{ color: var(--text-secondary) !important; }}

    /* --- Expanders: vidro fosco --- */
    div[data-testid="stExpander"] {{
        background: var(--bg-elev);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--border-subtle);
        border-left: 3px solid var(--gold);
        border-radius: 14px;
        overflow: hidden;
        transition: box-shadow 0.3s ease;
    }}
    div[data-testid="stExpander"] summary {{
        color: var(--text-primary) !important;
        font-weight: 600;
    }}
    div[data-testid="stExpander"]:hover {{
        box-shadow: 0 10px 34px -14px rgba(255,221,119,0.35);
    }}

    /* --- Plotly charts: moldura de vidro --- */
    [data-testid="stPlotlyChart"] {{
        background: var(--bg-elev);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid var(--border-subtle);
        border-radius: 16px;
        padding: 10px;
        transition: box-shadow 0.3s ease;
    }}
    [data-testid="stPlotlyChart"]:hover {{
        box-shadow: 0 14px 40px -16px rgba(255,221,119,0.3);
    }}

    /* --- Botoes: gradiente dourado suave + glow forte no hover --- */
    .stButton > button, .stFormSubmitButton > button {{
        background: linear-gradient(135deg, var(--gold-light), var(--gold) 55%, var(--gold-deep));
        color: #241C00;
        font-weight: 700;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 1.3rem;
        box-shadow: 0 4px 18px -8px rgba(255,221,119,0.35);
        transition: all 0.3s cubic-bezier(0.22,1,0.36,1);
    }}
    .stButton > button:hover, .stFormSubmitButton > button:hover {{
        box-shadow: 0 0 0 1px rgba(255,238,170,0.5), 0 0 40px rgba(255,204,51,0.6);
        transform: translateY(-2px) scale(1.015);
        color: #241C00;
    }}
    .stButton > button:active {{ transform: translateY(0) scale(0.99); }}

    /* --- Inputs, selects, sliders ---------------------------------------
       CORRECAO CRITICA (v2): o bug persistia porque o <input> em si tem
       fundo transparente no Streamlit -- quem realmente pinta o fundo
       visivel e o "wrapper" a volta dele (div[data-baseweb="input"] e
       div[data-baseweb="base-input"]). Antes so escurecemos o <input>;
       o wrapper continuava claro por baixo, e o texto branco ficava
       "branco sobre claro" = invisivel. Agora escurecemos TODAS as
       camadas ao mesmo tempo (wrapper + input) para nao haver nenhuma
       superficie clara por tras do texto. ------------------------------- */

    /* Wrappers visiveis do campo -- e aqui que a cor de fundo REALMENTE
       aparece (nao no <input>, que e transparente por cima) */
    div[data-testid="stTextInput"] div[data-baseweb="input"],
    div[data-testid="stTextInput"] div[data-baseweb="base-input"],
    div[data-testid="stNumberInput"] div[data-baseweb="input"],
    div[data-testid="stNumberInput"] div[data-baseweb="base-input"],
    div[data-testid="stTextArea"] div[data-baseweb="base-input"],
    div[data-testid="stTextArea"] div[data-baseweb="textarea"],
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div {{
        background-color: #1A1A22 !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 10px !important;
    }}

    /* Campo em si -- fundo transparente de proposito (para mostrar o
       wrapper escuro de cima, sem "costuras" de cor entre as duas
       camadas) e texto branco puro, sempre */
    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea,
    input[type="text"],
    input[type="number"],
    textarea {{
        background-color: transparent !important;
        color: #FFFFFF !important;
        caret-color: var(--gold) !important;
        border: none !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }}

    /* Botoes de incremento/decremento (+ / -) do number_input */
    div[data-testid="stNumberInput"] button {{
        background-color: #1A1A22 !important;
        border-color: var(--border-subtle) !important;
    }}
    div[data-testid="stNumberInput"] button svg {{
        fill: #FFFFFF !important;
    }}

    /* Placeholders -- claros mas distinguiveis do texto escrito */
    .stTextInput input::placeholder,
    .stNumberInput input::placeholder,
    .stTextArea textarea::placeholder,
    input::placeholder,
    textarea::placeholder {{
        color: #B9B8C4 !important;
        opacity: 1 !important;
        -webkit-text-fill-color: #B9B8C4 !important;
    }}

    /* Selectbox / Multiselect (BaseWeb) -- tudo o que esta dentro do
       campo fechado (valor selecionado, seta, tags) fica branco */
    div[data-baseweb="select"] * {{
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }}
    /* "Tags" de um multiselect -- fundo dourado proprio, texto escuro,
       para nao ficarem brancas sobre a caixa (agora tambem) escura */
    div[data-baseweb="tag"] {{
        background-color: var(--gold-deep) !important;
    }}
    div[data-baseweb="tag"] * {{
        color: #1A1400 !important;
        -webkit-text-fill-color: #1A1400 !important;
    }}

    /* Lista de opcoes do dropdown -- renderizada num portal separado,
       por isso e estilizada fora de qualquer wrapper do Streamlit */
    div[data-baseweb="popover"] ul[role="listbox"],
    div[data-baseweb="menu"] {{
        background-color: #1A1A22 !important;
        border: 1px solid var(--border-subtle) !important;
    }}
    div[data-baseweb="popover"] li,
    div[data-baseweb="menu"] li,
    div[data-baseweb="popover"] li *,
    div[data-baseweb="menu"] li * {{
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }}
    div[data-baseweb="popover"] li:hover,
    div[data-baseweb="menu"] li:hover {{
        background-color: rgba(255,221,119,0.15) !important;
    }}

    /* Estado de foco -- glow amarelo bem visivel em qualquer campo */
    div[data-testid="stTextInput"]:focus-within div[data-baseweb="input"],
    div[data-testid="stNumberInput"]:focus-within div[data-baseweb="input"],
    div[data-testid="stTextArea"]:focus-within div[data-baseweb="base-input"],
    div[data-testid="stSelectbox"] div[data-baseweb="select"]:focus-within > div {{
        border-color: var(--gold) !important;
        box-shadow: 0 0 0 3px rgba(255,221,119,0.25), 0 0 18px rgba(255,221,119,0.35) !important;
        outline: none !important;
    }}

    [data-baseweb="slider"] div[role="slider"] {{
        background-color: var(--gold) !important;
        box-shadow: 0 0 16px rgba(255,221,119,0.7);
    }}
    [data-testid="stSlider"] [data-baseweb="slider"] > div > div {{
        background: linear-gradient(90deg, var(--teal), var(--gold)) !important;
    }}
    /* Numeros e texto de apoio do slider (min/max/valor atual) */
    [data-testid="stSlider"] [data-testid="stTickBarMin"],
    [data-testid="stSlider"] [data-testid="stTickBarMax"],
    [data-testid="stSlider"] div[data-testid="stThumbValue"] {{
        color: var(--text-primary) !important;
        font-weight: 600;
    }}

    /* --- Divider --- */
    hr {{
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,221,119,0.55), rgba(63,214,184,0.25), transparent);
        margin: 1.8rem 0;
    }}

    /* --- Tabelas / DataFrames --- */
    [data-testid="stDataFrame"] {{
        background: var(--bg-elev);
        backdrop-filter: blur(14px);
        border: 1px solid var(--border-subtle);
        border-radius: 14px;
        overflow: hidden;
    }}

    /* --- Alertas (success / info / warning / error) --- */
    div[data-testid="stAlertContainer"], div[data-testid="stNotification"], .stAlert {{
        border-radius: 14px !important;
        border: 1px solid var(--border-subtle) !important;
        background: var(--bg-elev) !important;
        backdrop-filter: blur(10px);
    }}

    /* --- Tabs --- */
    [data-testid="stTabs"] button[aria-selected="true"] {{
        color: var(--gold) !important;
        border-bottom-color: var(--gold) !important;
    }}

    /* --- Scrollbar --- */
    ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
    ::-webkit-scrollbar-track {{ background: var(--bg-void); }}
    ::-webkit-scrollbar-thumb {{
        background: linear-gradient(var(--gold-deep), var(--gold));
        border-radius: 6px;
    }}

    /* --- Rede de seguranca final: colocada deliberadamente por ultimo no
       ficheiro, para ganhar qualquer "empate" de especificidade CSS com
       estilos internos do Streamlit/BaseWeb. Garante que, seja qual for
       a versao do Streamlit, nunca existe texto escrito invisivel dentro
       de um campo. --- */
    input, textarea, select {{
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }}
    </style>
    """
