"""
Sentinel AI - Aplicacao Principal (Streamlit)
Protótipo completo (Fases 1-8): Formulário Adaptativo, Motor de
Classificação Multidimensional, Sentinel Index, Perfil Único, Isolamento
Inteligente de Dados e Dashboard Executivo.

Este ficheiro e propositadamente "fino": o seu unico trabalho e
"orquestrar" -- chamar cada modulo de src/, mostrar o resultado na
interface, e ligar tudo por ordem. Toda a logica pesada (regras de
negocio, calculos, graficos) vive nos modulos dentro de src/.
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Permite importar os modulos dentro de src/ quando o Streamlit corre
# a partir da raiz do projeto.
sys.path.append(str(Path(__file__).resolve().parent / "src"))

from formulario import render_formulario  # noqa: E402
from database import (  # noqa: E402
    inserir_cliente,
    inserir_respostas_adaptativas,
    listar_clientes,
    listar_pendentes,
    listar_classificados,
    obter_cliente_por_id,
    obter_respostas_adaptativas,
    obter_dados_treino,
    atualizar_sentinel_index,
    contar_clientes,
    inicializar_schema,
)
from motor_classificacao import classificar_pendentes, treinar_modelos, obter_metadados_modelo  # noqa: E402
from sentinel_index import (  # noqa: E402
    PESOS_PADRAO,
    calcular_sentinel_index_todos,
    classificar_index,
)
from perfil_sentinel import (  # noqa: E402
    calcular_contribuicoes,
    gerar_grafico_radar,
    gerar_grafico_contribuicoes,
    gerar_explicacao_textual,
)
from isolamento import (  # noqa: E402
    PAPEIS,
    cliente_aciona_isolamento,
    montar_ficha_isolada,
    contar_campos_protegidos,
)
from dashboard_executivo import (  # noqa: E402
    calcular_kpis,
    grafico_distribuicao_niveis,
    grafico_index_por_segmento,
    grafico_dispersao_risco,
    tabela_extremos,
    GUIAO_APRESENTACAO,
)
from tema import (  # noqa: E402
    emoji_nivel,
    css_tema,
    badge_nivel,
    cartao_antes_depois,
    cartao_papel,
    linha_ficha,
    COR_SUCESSO,
    COR_PERIGO,
)

# Migracao explicita do schema -- corre aqui, de forma visivel e deliberada,
# uma vez por arranque da app. Nunca escondida dentro de outro modulo.
inicializar_schema()


st.set_page_config(page_title="Sentinel AI", page_icon="🛡️", layout="wide")

# ---------------------------------------------------------------------------
# Tema visual Dark/Gold (Fase 9 -- Redesign): todo o CSS vive em tema.py,
# injetado aqui de forma explicita e unica, no arranque da app -- nunca
# escondido dentro de outro modulo. Nao muda nenhuma logica, apenas o
# acabamento visual de toda a aplicacao.
# ---------------------------------------------------------------------------
st.markdown(css_tema(), unsafe_allow_html=True)


@st.cache_resource(show_spinner=False)
def _modelos_e_metadados_cache():
    """
    Treina os modelos de ML uma unica vez por sessao e guarda em cache.

    Sem isto, cada interacao no ecra (ex.: mexer num slider) faria o
    Streamlit correr o script inteiro outra vez -- e sem cache isso
    retreinaria os 3 modelos sem necessidade. Com 100 clientes o custo
    e pequeno, mas o cache torna a demo mais fluida (Melhoria 4).
    """
    modelos = treinar_modelos()
    metadados = obter_metadados_modelo(modelos, obter_dados_treino())
    return modelos, metadados

# ---------------------------------------------------------------------------
# Barra lateral: pesos configuraveis do Sentinel Index (Fase 4)
# ---------------------------------------------------------------------------

st.sidebar.header("⚖️ Pesos do Sentinel Index")
st.sidebar.caption(
    "Ajusta a importancia de cada dimensao. Os valores sao "
    "normalizados automaticamente para somarem 100%."
)

peso_risco_aml = st.sidebar.slider("Peso: Risco AML", 0, 100, PESOS_PADRAO["risco_aml"])
peso_risco_credito = st.sidebar.slider("Peso: Risco de Credito", 0, 100, PESOS_PADRAO["risco_credito"])
peso_rentabilidade = st.sidebar.slider("Peso: Rentabilidade", 0, 100, PESOS_PADRAO["rentabilidade"])

pesos_atuais = {
    "risco_aml": peso_risco_aml,
    "risco_credito": peso_risco_credito,
    "rentabilidade": peso_rentabilidade,
}

soma_pesos = sum(pesos_atuais.values())
if soma_pesos == 0:
    st.sidebar.error("Define pelo menos um peso maior que zero.")
else:
    st.sidebar.caption(f"Soma atual: {soma_pesos} -- sera normalizada para 100%.")

st.title("🛡️ Sentinel AI")
st.caption("Classificação Multidimensional de Clientes -- Protótipo")

with st.expander("ℹ️ O que é o Sentinel AI? (clica para ver)"):
    st.markdown(
        "O Sentinel AI trata cada cliente como um ser **multidimensional** -- "
        "não um número isolado. Este protótipo demonstra 5 elementos centrais:\n\n"
        "1. **Formulário Digital Adaptativo** -- perguntas diferentes consoante o segmento do cliente\n"
        "2. **Classificação Multidimensional** -- Machine Learning + regras de negócio explícitas\n"
        "3. **Perfil Único Sentinel** -- um cartão de identidade visual, com explicação (XAI)\n"
        "4. **Sentinel Index** -- uma única pontuação (0-100), com pesos configuráveis\n"
        "5. **Isolamento Inteligente de Dados** -- proteção de dados que se adapta ao risco real"
    )

col_metrica_1, col_metrica_2 = st.columns(2)
with col_metrica_1:
    st.metric("Clientes na base de dados", contar_clientes())
with col_metrica_2:
    st.metric("Clientes por classificar", len(listar_pendentes()))

if contar_clientes() == 0:
    st.warning(
        "⚠️ A base de dados está sem clientes sintéticos. "
        "Isto pode acontecer no primeiro arranque no Streamlit Cloud."
    )
    if st.button("🔄 Gerar clientes sintéticos agora"):
        from database import diagnosticar_e_repovoar_clientes
        with st.spinner("A gerar 100 clientes sintéticos..."):
            sucesso, mensagem = diagnosticar_e_repovoar_clientes()
        if sucesso:
            st.success(mensagem)
            st.rerun()
        else:
            st.error(f"Falhou: {mensagem}")

st.divider()

dados = render_formulario()

if dados:
    with st.spinner("A registar cliente na base de dados..."):
        novo_id = inserir_cliente(dados)
        inserir_respostas_adaptativas(novo_id, dados["respostas_adaptativas"])

    st.success(f"Cliente '{dados['nome']}' registado com sucesso! (ID {novo_id})")
    st.info(
        "Este cliente aparece agora como 'Pendente'. Usa o botão abaixo para "
        "o classificar com o Motor de Classificacao Multidimensional."
    )

st.divider()

# ---------------------------------------------------------------------------
# Motor de Classificacao Multidimensional (Fase 3)
# ---------------------------------------------------------------------------

st.subheader("🧠 Motor de Classificação Multidimensional")
st.caption(
    "Combina um modelo de Machine Learning (treinado nos clientes sinteticos) "
    "com regras de negocio explicitas, para classificar automaticamente "
    "qualquer cliente 'Pendente'."
)

total_pendentes = len(listar_pendentes())

if total_pendentes == 0:
    st.info("Não há clientes pendentes de classificação neste momento.")
else:
    st.warning(f"{total_pendentes} cliente(s) por classificar.")

    if st.button("🚀 Classificar Clientes Pendentes", type="primary"):
        try:
            with st.spinner("A treinar o modelo e a classificar clientes..."):
                resultados = classificar_pendentes()
        except ValueError as erro:
            st.error(f"Não foi possível classificar: {erro}")
            resultados = []

        if resultados:
            st.success(f"{len(resultados)} cliente(s) classificado(s) com sucesso!")

        for resultado in resultados:
            emoji = emoji_nivel(resultado["nivel_seguranca"])

            with st.expander(
                f"{emoji} {resultado['nome']} -- Nível de Segurança: {resultado['nivel_seguranca']}"
            ):
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Risco AML", resultado["risco_aml"])
                col_b.metric("Risco de Credito", resultado["risco_credito"])
                col_c.metric("Perfil mais semelhante", resultado["perfil_estimado"])

                st.markdown("**Como o motor chegou a este resultado:**")
                for linha_explicacao in resultado["explicacao"]:
                    st.markdown(f"- {linha_explicacao}")

st.divider()

# ---------------------------------------------------------------------------
# Sentinel Index (Fase 4)
# ---------------------------------------------------------------------------

st.subheader("📊 Sentinel Index")
st.caption(
    "Uma única pontuação (0-100) que resume Risco AML, Risco de Crédito "
    "e Rentabilidade -- ajusta os pesos na barra lateral e recalcula."
)

total_classificados = len(listar_classificados())

if total_classificados == 0:
    st.info("Ainda não há clientes classificados. Classifica os clientes pendentes na secção acima primeiro.")
elif soma_pesos == 0:
    st.warning("Ajusta os pesos na barra lateral antes de calcular o indice.")
else:
    if st.button("📈 Calcular / Atualizar Sentinel Index", type="primary"):
        with st.spinner("A calcular o Sentinel Index de todos os clientes..."):
            df_classificados = listar_classificados()
            df_classificados["sentinel_index"] = calcular_sentinel_index_todos(
                df_classificados, pesos=pesos_atuais
            )
            for _, linha in df_classificados.iterrows():
                atualizar_sentinel_index(int(linha["id_cliente"]), float(linha["sentinel_index"]))

        st.success(f"Sentinel Index calculado para {total_classificados} cliente(s)!")

    # O ranking mostra-se sempre com base no que esta guardado na base de
    # dados -- nao so no instante em que se clica no botao acima. Isto
    # torna a demo mais robusta: podes saltar entre seccoes sem perder
    # a tabela.
    df_indexados = listar_classificados()
    df_indexados = df_indexados[df_indexados["sentinel_index"].notna()]

    if df_indexados.empty:
        st.caption("Ainda sem Sentinel Index calculado -- clica no botão acima.")
    else:
        df_indexados["categoria"] = df_indexados["sentinel_index"].apply(classificar_index)
        tabela_ranking = df_indexados.sort_values("sentinel_index", ascending=False)[
            ["nome", "segmento_comercial", "nivel_seguranca", "risco_aml",
             "risco_credito", "rentabilidade", "sentinel_index", "categoria"]
        ]

        st.dataframe(
            tabela_ranking,
            use_container_width=True,
            hide_index=True,
            column_config={
                "sentinel_index": st.column_config.ProgressColumn(
                    "Sentinel Index",
                    min_value=0,
                    max_value=100,
                    format="%.1f",
                ),
            },
        )

st.divider()

# ---------------------------------------------------------------------------
# Perfil Unico Sentinel (Fase 5)
# ---------------------------------------------------------------------------

st.subheader("👤 Perfil Único Sentinel")
st.caption(
    "Escolhe um cliente para veres o seu 'cartão de identidade' completo: "
    "dados, riscos, Sentinel Index, gráfico radar e explicação de como "
    "chegámos àquele número (XAI básico)."
)

df_com_indice = listar_classificados()
df_com_indice = df_com_indice[df_com_indice["sentinel_index"].notna()]

if df_com_indice.empty:
    st.info(
        "Ainda não há clientes com Sentinel Index calculado. "
        "Calcula o Sentinel Index na secção acima primeiro."
    )
else:
    opcoes = {
        f"{linha['nome']} (ID {int(linha['id_cliente'])})": int(linha["id_cliente"])
        for _, linha in df_com_indice.iterrows()
    }
    escolha = st.selectbox("Selecionar cliente", list(opcoes.keys()))
    id_selecionado = opcoes[escolha]

    cliente = obter_cliente_por_id(id_selecionado)
    with st.spinner("A calcular o perfil deste cliente..."):
        contribuicoes = calcular_contribuicoes(cliente, df_com_indice, pesos=pesos_atuais)

    col_esq, col_dir = st.columns([1, 1.15])

    with col_esq:
        st.markdown(f"### {cliente['nome']}")
        st.caption(f"{cliente['profissao']} · {cliente['segmento_comercial']} · {int(cliente['idade'])} anos")

        st.markdown(f"**Nível de Segurança:** {badge_nivel(cliente['nivel_seguranca'])}", unsafe_allow_html=True)

        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric(
            "Sentinel Index", f"{cliente['sentinel_index']:.1f}",
            help="Pontuação 0-100 que resume Risco AML, Risco de Crédito e Rentabilidade, "
                 "com os pesos definidos na barra lateral.",
        )
        col_m2.metric(
            "Risco AML", int(cliente["risco_aml"]),
            help="Estimativa de risco de branqueamento de capitais (0 = nenhum risco, "
                 "100 = risco máximo), calculada pelo modelo de Machine Learning + regras de negócio.",
        )
        col_m3.metric(
            "Risco Crédito", int(cliente["risco_credito"]),
            help="Estimativa de risco de incumprimento de crédito (0 = nenhum risco, 100 = risco máximo).",
        )

        st.metric("Saldo médio (Kz)", f"{cliente['saldo_medio']:,.0f}")
        st.metric("Rentabilidade anual (Kz)", f"{cliente['rentabilidade']:,.0f}")

        st.markdown("**Como chegámos a este Sentinel Index:**")
        for frase in gerar_explicacao_textual(cliente, contribuicoes):
            st.markdown(f"- {frase}")

        # -------------------------------------------------------------------
        # Modelo de Machine Learning utilizado (Melhoria 1)
        # -------------------------------------------------------------------
        with st.expander("🔬 Modelo de Machine Learning utilizado"):
            with st.spinner("A carregar informação do modelo de Machine Learning..."):
                _, metadados_modelo = _modelos_e_metadados_cache()
            st.markdown(
                f"- **Algoritmo:** {metadados_modelo['algoritmo']}, com "
                f"**{metadados_modelo['n_arvores']} árvores de decisão** por modelo.\n"
                f"- **Dados de treino:** {metadados_modelo['n_clientes_treino']} clientes sintéticos "
                f"com risco conhecido (Fase 1).\n"
                f"- **Variáveis usadas:** {', '.join(metadados_modelo['features'])}.\n"
                f"- **Motor híbrido:** a estimativa do modelo é sempre combinada com regras de "
                f"negócio explícitas (ex.: transações internacionais frequentes) antes do "
                f"resultado final -- nunca é só \"a IA decidiu\"."
            )
            st.caption("Importância de cada variável na estimativa do Risco AML:")
            nomes_legiveis_features = {
                "idade": "Idade",
                "saldo_medio": "Saldo Médio",
                "rentabilidade": "Rentabilidade",
                "segmento_encoded": "Segmento Comercial",
            }
            importancias = pd.Series(metadados_modelo["importancia_risco_aml"])
            importancias.index = [nomes_legiveis_features.get(i, i) for i in importancias.index]
            st.bar_chart(importancias)

    with col_dir:
        st.plotly_chart(gerar_grafico_radar(contribuicoes), use_container_width=True)
        st.plotly_chart(gerar_grafico_contribuicoes(contribuicoes), use_container_width=True)

st.divider()

# ---------------------------------------------------------------------------
# Simulacao de Isolamento Inteligente de Dados (Fase 6)
# ---------------------------------------------------------------------------

st.subheader("🔒 Simulação de Isolamento Inteligente de Dados")
st.caption(
    "A mesma ficha de cliente, vista por dois papéis diferentes dentro do "
    "banco. O Sentinel isola automaticamente os campos sensíveis do "
    "Gestor Comercial quando o risco do cliente é Alto ou Crítico -- "
    "sem que ninguém precise de configurar isso manualmente."
)

df_classificados_isolamento = listar_classificados()

if df_classificados_isolamento.empty:
    st.info("Ainda não há clientes classificados para simular.")
else:
    opcoes_isolamento = {
        f"{linha['nome']} (ID {int(linha['id_cliente'])}) -- {linha['nivel_seguranca']}": int(linha["id_cliente"])
        for _, linha in df_classificados_isolamento.iterrows()
    }
    escolha_isolamento = st.selectbox(
        "Selecionar cliente para simular acesso", list(opcoes_isolamento.keys()), key="select_isolamento"
    )
    id_cliente_isolamento = opcoes_isolamento[escolha_isolamento]

    cliente_isolamento = obter_cliente_por_id(id_cliente_isolamento)
    respostas_isolamento = obter_respostas_adaptativas(id_cliente_isolamento)
    with st.spinner("A calcular níveis de acesso por papel..."):
        isolamento_ativo = cliente_aciona_isolamento(cliente_isolamento["nivel_seguranca"])
        n_protegidos_gestor = contar_campos_protegidos("Gestor Comercial", cliente_isolamento["nivel_seguranca"])

    # -------------------------------------------------------------------
    # Faixa dramática ANTES (vermelho) / DEPOIS (verde) -- Melhoria 2
    # -------------------------------------------------------------------
    col_antes, col_depois = st.columns(2)
    with col_antes:
        st.markdown(
            cartao_antes_depois(
                "ANTES -- sistema bancário tradicional",
                "Qualquer colaborador com acesso à ficha do cliente vê <u>todos</u> "
                "os dados -- saldo, rentabilidade, risco AML, risco de crédito -- "
                "independentemente da sua função ou do risco real do cliente.",
                cor=COR_PERIGO, emoji="❌",
            ),
            unsafe_allow_html=True,
        )
    with col_depois:
        st.markdown(
            cartao_antes_depois(
                "DEPOIS -- com o Sentinel AI",
                "O acesso adapta-se automaticamente ao <u>papel</u> de quem consulta "
                "e ao <u>risco real</u> do cliente. Para este cliente, o Sentinel está "
                f"a proteger <strong>{n_protegidos_gestor} campo(s)</strong> do Gestor "
                "Comercial neste preciso momento.",
                cor=COR_SUCESSO, emoji="✅", intenso=True,
            ),
            unsafe_allow_html=True,
        )

    st.write("")

    if isolamento_ativo:
        st.warning(
            f"⚠️ Este cliente tem Nível de Segurança **{cliente_isolamento['nivel_seguranca']}** -- "
            "o Sentinel está a isolar automaticamente os campos sensíveis do Gestor Comercial."
        )
    else:
        st.success(
            f"✅ Este cliente tem Nível de Segurança **{cliente_isolamento['nivel_seguranca']}** -- "
            "sem necessidade de isolamento. O Gestor Comercial vê a ficha completa."
        )

    col_papel_1, col_papel_2 = st.columns(2)

    for coluna, papel in zip((col_papel_1, col_papel_2), PAPEIS):
        with coluna:
            n_protegidos = contar_campos_protegidos(papel, cliente_isolamento["nivel_seguranca"])
            emoji_papel = "🧑‍💼" if papel == "Gestor Comercial" else "🕵️"

            st.markdown(cartao_papel(papel, emoji_papel, n_protegidos), unsafe_allow_html=True)

            linhas = montar_ficha_isolada(cliente_isolamento, respostas_isolamento, papel)
            html_ficha = "".join(
                linha_ficha(rotulo, valor, restrito=(valor == "🔒 Acesso Restrito"))
                for rotulo, valor in linhas
            )
            st.markdown(html_ficha, unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------------------------
# Dashboard Executivo + Narrativa de Apresentacao (Fase 7)
# ---------------------------------------------------------------------------

st.subheader("📊 Dashboard Executivo")
st.caption(
    "A visão de topo: a saúde de toda a carteira de clientes num relance -- "
    "o que um banco veria todas as manhãs."
)

df_dashboard = listar_classificados()
df_dashboard = df_dashboard[df_dashboard["sentinel_index"].notna()]

if df_dashboard.empty:
    st.info(
        "Ainda não há dados suficientes para o Dashboard Executivo. "
        "Classifica clientes e calcula o Sentinel Index nas secções acima primeiro."
    )
else:
    with st.spinner("A atualizar o Dashboard Executivo..."):
        kpis = calcular_kpis(df_dashboard)
        fig_distribuicao = grafico_distribuicao_niveis(df_dashboard)
        fig_por_segmento = grafico_index_por_segmento(df_dashboard)
        fig_dispersao = grafico_dispersao_risco(df_dashboard)
        top_n, bottom_n = tabela_extremos(df_dashboard, n=5)

    col_k1, col_k2, col_k3 = st.columns(3)
    col_k1.metric("Total de Clientes", kpis["total_clientes"])
    col_k2.metric("Sentinel Index Médio", kpis["sentinel_index_medio"])
    col_k3.metric("Rentabilidade Total (Kz)", f"{kpis['rentabilidade_total']:,.0f}")

    col_k4, col_k5, col_k6 = st.columns(3)
    col_k4.metric("% Nível Crítico", f"{kpis['pct_critico']}%")
    col_k5.metric(
        "🛡️ Clientes em Isolamento Ativo", f"{kpis['pct_isolamento_ativo']}%",
        help="Percentagem de clientes com Nível de Segurança Alto ou Crítico -- "
             "cujos dados sensíveis estão a ser protegidos automaticamente pelo Sentinel.",
    )
    col_k6.metric(
        "💰 Valor Protegido (Kz)", f"{kpis['valor_protegido']:,.0f}",
        help="Soma do saldo médio de todos os clientes em isolamento ativo -- "
             "o valor financeiro que está, neste momento, sob proteção reforçada de dados.",
    )

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.plotly_chart(fig_distribuicao, use_container_width=True)
    with col_g2:
        st.plotly_chart(fig_por_segmento, use_container_width=True)

    st.plotly_chart(fig_dispersao, use_container_width=True)

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown("**🏆 Top 5 -- Melhor Sentinel Index**")
        st.dataframe(top_n, hide_index=True, use_container_width=True)
    with col_t2:
        st.markdown("**⚠️ Bottom 5 -- Requerem Atenção**")
        st.dataframe(bottom_n, hide_index=True, use_container_width=True)

with st.expander("🎤 Guião de Apresentação (3-5 minutos)"):
    for titulo, texto in GUIAO_APRESENTACAO:
        st.markdown(f"**{titulo}**")
        st.markdown(texto)
        st.markdown("")

st.divider()

st.subheader("Ultimos clientes registados")
st.dataframe(listar_clientes(limite=10), use_container_width=True)
