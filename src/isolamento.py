"""
Sentinel AI - Simulacao de Isolamento Inteligente de Dados
Fase 6: O momento mais impactante da demo -- mostrar visualmente que o
Sentinel nao trata "ver os dados de um cliente" como tudo-ou-nada.

Ideia central: a MESMA ficha de cliente e mostrada de forma diferente
consoante DUAS coisas ao mesmo tempo:
  1. Quem esta a consultar (o "papel" / a funcao dessa pessoa no banco)
  2. Quao arriscado e o cliente (nivel_seguranca)

Um Gestor Comercial normal nao precisa (nem deve) ver o detalhe de risco
AML de um cliente critico -- isso e trabalho do Compliance. Mas para um
cliente de baixo risco, o Gestor ve tudo sem restricoes, porque nao ha
nada sensivel a proteger. Isto chama-se "isolamento inteligente": a
proteção adapta-se ao risco real, em vez de aplicar a mesma regra rigida
a todos os clientes.
"""

# ---------------------------------------------------------------------------
# Definicao dos campos e das regras de visibilidade
# ---------------------------------------------------------------------------

# Campos que qualquer papel pode sempre ver -- informacao basica de
# identificacao, sem valor sensivel de risco ou financeiro.
CAMPOS_SEMPRE_VISIVEIS = ["nome", "idade", "profissao", "segmento_comercial", "nivel_seguranca"]

# Campos sensiveis -- so ficam visiveis a um Gestor Comercial se o
# cliente NAO estiver num nivel de risco que exija isolamento.
CAMPOS_SENSIVEIS = ["saldo_medio", "rentabilidade", "risco_aml", "risco_credito", "sentinel_index"]

# A partir destes niveis de seguranca, o Sentinel isola automaticamente
# os campos sensiveis de quem nao for Compliance.
NIVEIS_QUE_ACIONAM_ISOLAMENTO = {"Alto", "Critico"}

PAPEIS = ["Gestor Comercial", "Oficial de Compliance"]

RESPOSTAS_SEMPRE_ISOLADAS_DE_COMERCIAL = True  # respostas adaptativas sao sempre sensiveis


def cliente_aciona_isolamento(nivel_seguranca: str) -> bool:
    """Verifica se o nivel de risco deste cliente justifica isolar dados."""
    return nivel_seguranca in NIVEIS_QUE_ACIONAM_ISOLAMENTO


def campos_visiveis_para(papel: str, nivel_seguranca: str) -> set:
    """
    Devolve o conjunto de campos que um determinado papel pode ver para
    um cliente com este nivel de seguranca.

    Esta e a funcao central da Fase 6 -- toda a logica de isolamento
    vive aqui, num unico sitio, para ser facil de auditar e explicar.
    """
    if papel == "Oficial de Compliance":
        # Compliance tem sempre acesso total -- e a funcao deles avaliar risco.
        return set(CAMPOS_SEMPRE_VISIVEIS) | set(CAMPOS_SENSIVEIS)

    # Gestor Comercial:
    if cliente_aciona_isolamento(nivel_seguranca):
        return set(CAMPOS_SEMPRE_VISIVEIS)  # campos sensiveis ficam isolados
    return set(CAMPOS_SEMPRE_VISIVEIS) | set(CAMPOS_SENSIVEIS)


def respostas_visiveis_para(papel: str) -> bool:
    """As respostas do formulario adaptativo (ex.: transacoes internacionais)
    sao sempre consideradas sensiveis e reservadas ao Compliance."""
    return papel == "Oficial de Compliance"


def contar_campos_protegidos(papel: str, nivel_seguranca: str) -> int:
    """
    Conta quantos campos sensiveis estao a ser ativamente escondidos
    deste papel, para este cliente. Usado na interface para mostrar um
    numero de impacto (ex.: "4 campos protegidos") em vez de o
    utilizador ter de contar os cadeados um a um.
    """
    visiveis = campos_visiveis_para(papel, nivel_seguranca)
    protegidos = len(set(CAMPOS_SENSIVEIS) - visiveis)
    if not respostas_visiveis_para(papel):
        protegidos += 1  # as respostas adaptativas contam como mais 1 campo protegido
    return protegidos


NOMES_LEGIVEIS = {
    "saldo_medio": "Saldo médio (Kz)",
    "rentabilidade": "Rentabilidade anual (Kz)",
    "risco_aml": "Risco AML",
    "risco_credito": "Risco de Crédito",
    "sentinel_index": "Sentinel Index",
}


def montar_ficha_isolada(cliente, respostas: dict, papel: str) -> list:
    """
    Monta a lista de linhas (campo, valor_ou_mascara) que representa como
    ESTE papel ve a ficha DESTE cliente. E o resultado que a interface
    vai desenhar lado a lado para os dois papeis.
    """
    campos_visiveis = campos_visiveis_para(papel, cliente["nivel_seguranca"])
    linhas = []

    linhas.append(("Nome", cliente["nome"]))
    linhas.append(("Idade", f"{int(cliente['idade'])} anos"))
    linhas.append(("Profissão", cliente["profissao"]))
    linhas.append(("Segmento Comercial", cliente["segmento_comercial"]))
    linhas.append(("Nível de Segurança", cliente["nivel_seguranca"]))

    for campo in CAMPOS_SENSIVEIS:
        rotulo = NOMES_LEGIVEIS[campo]
        if campo in campos_visiveis:
            valor = cliente[campo]
            if campo in ("saldo_medio", "rentabilidade"):
                linhas.append((rotulo, f"{valor:,.0f}"))
            elif campo == "sentinel_index":
                linhas.append((rotulo, f"{valor:.1f}" if valor is not None else "N/D"))
            else:
                linhas.append((rotulo, str(int(valor))))
        else:
            linhas.append((rotulo, "🔒 Acesso Restrito"))

    if respostas:
        if respostas_visiveis_para(papel):
            for pergunta, resposta in respostas.items():
                linhas.append((pergunta, str(resposta)))
        else:
            linhas.append(("Respostas do formulário adaptativo", "🔒 Acesso Restrito"))

    return linhas
