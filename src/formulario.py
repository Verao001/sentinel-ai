"""
Sentinel AI - Formulario Digital Adaptativo
Fase 2: Interface de recolha de dados que se ADAPTA consoante o
segmento comercial escolhido pelo utilizador.

Este e um dos 5 elementos centrais do MVP: o Sentinel nao trata todos
os clientes da mesma forma logo desde a entrada de dados -- cada
segmento tem perguntas relevantes proprias.
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Opcoes de profissao por segmento (coerentes com os perfis da Fase 1)
# ---------------------------------------------------------------------------

PROFISSOES_POR_SEGMENTO = {
    "Private Banking": ["Empresario", "Medico", "Advogado", "Diretor Executivo", "Outra"],
    "Retalho": ["Professor", "Enfermeiro", "Funcionario Publico", "Comerciante", "Outra"],
    "Corporate": ["Importador/Exportador", "Consultor", "Gestor de Empresa", "Outra"],
    "Digital": ["Estudante", "Estagiario", "Freelancer", "Outra"],
    "Corporate / Institucional": ["Fundo de Investimento", "Seguradora", "Multinacional", "Outra"],
}

SEGMENTOS = list(PROFISSOES_POR_SEGMENTO.keys())


# ---------------------------------------------------------------------------
# Textos das perguntas adaptativas (constantes)
# ---------------------------------------------------------------------------
# Extraidas como constantes -- e nao texto solto dentro da funcao -- para que
# o Motor de Classificacao (Fase 3) as possa importar e reconhecer sem risco
# de erro de digitação (ex.: um acento a menos quebraria a regra de negocio
# silenciosamente).

PERGUNTA_PRIVATE_BANKING = "Possui investimentos ou contas no estrangeiro?"
PERGUNTA_RETALHO = "Ha quantos anos e cliente deste banco?"
PERGUNTA_CORPORATE = "Realiza transacoes internacionais com frequencia?"
PERGUNTA_DIGITAL = "Verificacao de identidade concluida via aplicacao?"
PERGUNTA_INSTITUCIONAL = "Tipo de instituicao"


def _pergunta_adaptativa(segmento: str):
    """
    Renderiza o widget certo consoante o segmento escolhido e devolve
    (texto_da_pergunta, resposta_dada_pelo_utilizador).

    Este e o "cerebro" da adaptatividade: cada segmento tem uma pergunta
    diferente, relevante para o tipo de risco tipico desse segmento.
    """
    if segmento == "Private Banking":
        pergunta = PERGUNTA_PRIVATE_BANKING
        resposta = st.selectbox(pergunta, ["Nao", "Sim"])

    elif segmento == "Retalho":
        pergunta = PERGUNTA_RETALHO
        resposta = st.slider(pergunta, 0, 40, 2)

    elif segmento == "Corporate":
        pergunta = PERGUNTA_CORPORATE
        resposta = st.selectbox(pergunta, ["Nao", "Ocasionalmente", "Frequentemente"])

    elif segmento == "Digital":
        pergunta = PERGUNTA_DIGITAL
        resposta = st.selectbox(pergunta, ["Sim", "Nao"])

    else:  # Corporate / Institucional
        pergunta = PERGUNTA_INSTITUCIONAL
        resposta = st.selectbox(pergunta, ["Fundo de Investimento", "Seguradora", "Multinacional", "Outra"])

    return pergunta, resposta


def render_formulario():
    """
    Desenha o Formulario Digital Adaptativo no ecra.

    Devolve um dicionario com todos os dados recolhidos QUANDO o
    utilizador submete o formulario. Devolve None enquanto o
    formulario ainda nao foi submetido.

    Nota tecnica importante: o "Segmento Comercial" fica FORA do
    st.form(). Em Streamlit, widgets dentro de um st.form so
    atualizam o resto do ecra quando se clica em "Registar Cliente" --
    mas precisamos que a lista de profissoes e a pergunta extra mudem
    IMEDIATAMENTE quando o utilizador troca de segmento. Por isso o
    selectbox do segmento fica fora do formulario, e so o resto fica
    dentro.
    """
    st.subheader("Novo Cliente - Formulario Digital Adaptativo")

    segmento = st.selectbox("Segmento Comercial", SEGMENTOS, key="segmento_selecionado")

    with st.form("formulario_cliente", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            nome = st.text_input("Nome completo")
            idade = st.number_input("Idade", min_value=18, max_value=100, value=30)
            profissao = st.selectbox("Profissao", PROFISSOES_POR_SEGMENTO[segmento])

        with col2:
            saldo_medio = st.number_input("Saldo medio estimado (Kz)", min_value=0.0, step=1000.0)
            rentabilidade = st.number_input("Rentabilidade anual estimada (Kz)", min_value=0.0, step=500.0)

        st.markdown("---")
        st.caption(f"Pergunta adicional para o segmento **{segmento}**:")
        pergunta_extra, resposta_extra = _pergunta_adaptativa(segmento)

        submeter = st.form_submit_button("Registar Cliente")

        if submeter:
            if not nome.strip():
                st.error("O nome e obrigatorio.")
                return None

            return {
                "nome": nome.strip(),
                "idade": int(idade),
                "profissao": profissao,
                "segmento_comercial": segmento,
                "saldo_medio": float(saldo_medio),
                "rentabilidade": float(rentabilidade),
                "respostas_adaptativas": {pergunta_extra: resposta_extra},
            }

    return None
