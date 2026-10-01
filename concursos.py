"""
Aba Concursos — concursos públicos e processos seletivos para nutricionista.

Regra central (decisão do usuário, 01/10/2026): a informação precisa ser
CONFIÁVEL. Por isso:
- a lista só aparece se a busca na web do Gemini devolver fontes reais; sem
  fontes, o app NÃO mostra uma lista gerada só pelo conhecimento do modelo
  (ele não sabe o que está aberto hoje) e mostra links de portais oficiais;
- a IA é instruída a nunca inventar concurso, data, vaga ou salário;
- os links mostrados são os que a busca realmente usou (não os que a IA
  escreveria no texto, que poderiam ser inventados).
"""

from datetime import datetime

import streamlit as st
from google import genai
from google.genai import types as genai_types

from config import GEMINI_MODEL, SYSTEM_PROMPT_BASE
from utils import (
    MENSAGEM_CONGESTIONADO,
    _com_detalhe_tecnico,
    _eh_erro_de_congestionamento,
    _eh_erro_de_limite,
    _texto_da_resposta,
)

ESTADOS = [
    "Brasil todo",
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG",
    "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
]

# Portais para conferir direto. Links da página inicial de cada site (as
# páginas internas mudam de endereço com frequência).
FONTES_CONFIAVEIS = [
    ("Diário Oficial da União (Imprensa Nacional)", "https://www.in.gov.br/", "editais de concursos federais"),
    ("Cebraspe", "https://www.cebraspe.org.br/", "banca de muitos concursos federais e estaduais"),
    ("FGV Conhecimento", "https://conhecimento.fgv.br/", "banca (seção de concursos)"),
    ("Vunesp", "https://www.vunesp.com.br/", "banca de concursos paulistas e outros"),
    ("IBFC", "https://www.ibfc.org.br/", "banca de concursos de vários estados"),
    ("Ebserh", "https://www.gov.br/ebserh/", "hospitais universitários federais"),
    ("Conselho Federal de Nutricionistas (CFN)", "https://www.cfn.org.br/", "notícias e informações da profissão"),
    ("PCI Concursos", "https://www.pciconcursos.com.br/", "portal que reúne concursos (confira sempre no edital)"),
]

PROMPT_CONCURSOS = SYSTEM_PROMPT_BASE + """
Módulo atual: Concursos públicos para nutricionista.
Sua tarefa é listar concursos públicos e processos seletivos para o cargo de
NUTRICIONISTA (e, quando o pedido incluir, residências multiprofissionais em
saúde com vaga para nutrição), usando SOMENTE o que você encontrou na busca na
web agora. A pessoa vai se inscrever com base nisto, então um dado errado
prejudica de verdade.

Regras de confiabilidade (invioláveis):
1. Nunca invente concurso, órgão, número de vagas, salário, banca, taxa ou data.
   Se não encontrou na busca, não escreva.
2. Se um dado não apareceu nas fontes, escreva "não localizei - confira no
   edital". Nunca estime nem deduza datas.
3. Prefira fontes oficiais: edital, site da banca organizadora, site do órgão ou
   Diário Oficial. Portais de notícias de concursos servem de pista; quando o
   dado veio só de um portal, diga isso no item.
4. NÃO escreva links/URLs no texto. As fontes realmente consultadas são listadas
   automaticamente depois da resposta. Em cada item, cite o nome do site ou órgão
   de onde o dado veio.
5. Se duas fontes divergirem num prazo, escreva as duas datas e avise da
   divergência.
6. Se não encontrou nenhum concurso em uma seção, escreva exatamente "Nenhum
   localizado nas fontes consultadas." - não complete a seção com exemplos.
7. Não recomende qual concurso escolher; só informe.

"Inscrição aberta" significa que a data de HOJE (informada no pedido) está entre
o início e o fim das inscrições. Use apenas a data de hoje informada, nunca
outra.

Responda em Markdown, sem tabelas, com EXATAMENTE estas três seções:

## Inscrições abertas agora
(ordene pelo prazo final de inscrição, do mais próximo ao mais distante)
## Inscrições ainda por abrir
(edital já publicado ou previsão oficial)
## Outros concursos do ano
(já encerrados, em andamento sem inscrição aberta, ou previstos)

Cada concurso, neste formato:
- **Órgão - cargo/área** (cidade/UF)
  - Vagas: ... | Salário: ... | Banca: ... | Taxa: ...
  - Inscrições: de DD/MM/AAAA a DD/MM/AAAA
  - Fonte dos dados: nome do site/órgão

No máximo 10 itens por seção, priorizando os de inscrição mais próxima do fim.
"""

_DIAS_SEMANA = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
                "sexta-feira", "sábado", "domingo"]


class SemFontesError(RuntimeError):
    """A busca respondeu, mas sem nenhuma fonte real — a lista não é confiável."""


def _agora_brasil() -> datetime:
    try:
        from zoneinfo import ZoneInfo

        return datetime.now(ZoneInfo("America/Sao_Paulo"))
    except Exception:  # noqa: BLE001 - sem fuso disponível, usa o relógio local
        return datetime.now()


def _fontes_da_resposta(response) -> list:
    """Lista [(título, endereço)] das fontes que a busca realmente usou."""
    try:
        metadata = response.candidates[0].grounding_metadata
        chunks = metadata.grounding_chunks if metadata else None
    except (AttributeError, IndexError):
        chunks = None
    fontes, vistos = [], set()
    for chunk in chunks or []:
        web = getattr(chunk, "web", None)
        if not web or not web.uri or web.uri in vistos:
            continue
        vistos.add(web.uri)
        fontes.append((web.title or web.uri, web.uri))
    return fontes


def buscar_concursos(api_key: str, estado: str, incluir_residencias: bool) -> dict:
    """Busca concursos de nutricionista na web (com fontes) e devolve um dict
    com 'texto', 'fontes', 'data_consulta' e 'estado'.

    Levanta SemFontesError quando a busca não devolve fontes reais, e
    RuntimeError (mensagem amigável) nos demais problemas.
    """
    if not api_key:
        raise ValueError("Cole sua chave da API do Gemini na barra lateral antes de continuar.")

    agora = _agora_brasil()
    hoje = f"{_DIAS_SEMANA[agora.weekday()]}, {agora.strftime('%d/%m/%Y')}"
    onde = "em todo o Brasil" if estado == "Brasil todo" else f"no estado {estado}"
    pedido = (
        f"Hoje é {hoje}. Procure concursos públicos e processos seletivos para o cargo de "
        f"nutricionista {onde}, com foco nos que têm inscrição aberta hoje e nos previstos "
        f"para {agora.year}."
    )
    if incluir_residencias:
        pedido += " Inclua também residências multiprofissionais em saúde com vaga para nutrição."

    client = genai.Client(api_key=api_key)
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=pedido,
            config=genai_types.GenerateContentConfig(
                system_instruction=PROMPT_CONCURSOS,
                tools=[genai_types.Tool(google_search=genai_types.GoogleSearch())],
            ),
        )
    except Exception as exc:  # noqa: BLE001 - qualquer erro da API vira mensagem amigável
        mensagem = str(exc)
        if _eh_erro_de_congestionamento(mensagem):
            raise RuntimeError(_com_detalhe_tecnico(MENSAGEM_CONGESTIONADO, mensagem)) from exc
        if _eh_erro_de_limite(mensagem):
            raise RuntimeError(
                "A cota da busca na web acabou por enquanto (ela tem limite próprio e é "
                "renovada com o tempo). Tente de novo mais tarde."
            ) from exc
        if "API key" in mensagem or "API_KEY_INVALID" in mensagem:
            raise RuntimeError("Chave da API inválida. Confira a chave colada na barra lateral.") from exc
        raise RuntimeError(
            _com_detalhe_tecnico(
                "Não consegui fazer a busca de concursos agora (a busca na web pode não estar "
                "disponível com esta chave).",
                mensagem,
            )
        ) from exc

    texto = _texto_da_resposta(response)
    fontes = _fontes_da_resposta(response)
    if not fontes:
        raise SemFontesError(
            "A busca não devolveu nenhuma fonte para esta consulta. Por segurança, o app não "
            "mostra uma lista sem fonte (um concurso ou prazo errado prejudicaria a inscrição)."
        )

    return {
        "texto": texto,
        "fontes": fontes,
        "data_consulta": agora.strftime("%d/%m/%Y às %H:%M"),
        "estado": estado,
    }


def _mostrar_fontes_confiaveis(aberto: bool) -> None:
    with st.expander("🔗 Onde conferir direto nos portais oficiais", expanded=aberto):
        for nome, url, descricao in FONTES_CONFIAVEIS:
            st.markdown(f"- [{nome}]({url}) — {descricao}")
        st.caption(
            "Links da página inicial de cada site. Procure por \"concursos\" ou \"editais\" e "
            "pelo cargo de nutricionista."
        )


def render_aba_concursos(api_key: str) -> None:
    """Desenha a aba Concursos (chamada pelo app.py dentro da aba)."""
    st.subheader("Concursos públicos para nutricionista")
    st.caption(
        "Útil para quem está começando a carreira: veja o que está com inscrição aberta "
        "agora e o panorama do ano, com a fonte de cada informação."
    )
    st.info(
        "ℹ️ Esta aba é independente das outras (não usa dados de paciente). "
        "A lista vem de uma busca na web feita na hora e **sempre deve ser conferida no "
        "edital oficial** antes de se inscrever."
    )

    col_estado, col_resid = st.columns([2, 3])
    with col_estado:
        estado = st.selectbox("Abrangência", ESTADOS, key="concursos_estado")
    with col_resid:
        incluir_residencias = st.checkbox(
            "Incluir residências multiprofissionais com vaga para nutrição",
            key="concursos_residencias",
        )

    erro_nesta_busca = False
    if st.button("🔎 Buscar concursos", type="primary", key="btn_concursos"):
        with st.spinner("Buscando concursos em fontes na web..."):
            try:
                st.session_state.concursos_resultado = buscar_concursos(
                    api_key, estado, incluir_residencias
                )
                st.session_state.contador_ia += 1
            except SemFontesError as erro:
                erro_nesta_busca = True
                st.session_state.concursos_resultado = None
                st.warning(str(erro))
            except (ValueError, RuntimeError) as erro:
                erro_nesta_busca = True
                st.session_state.concursos_resultado = None
                st.error(str(erro))
        if erro_nesta_busca:
            st.caption("Enquanto isso, você pode conferir direto nos portais oficiais abaixo.")

    resultado = st.session_state.get("concursos_resultado")
    if resultado:
        with st.container(border=True):
            st.caption(
                f"Consulta feita em {resultado['data_consulta']} · Abrangência: {resultado['estado']}"
            )
            st.warning(
                "Confira prazos, vagas e requisitos no edital oficial antes de se inscrever. "
                "Se algo estiver diferente do edital, vale o edital."
            )
            st.markdown(resultado["texto"])
            st.markdown("---")
            st.markdown("**Fontes consultadas na busca:**")
            for titulo, uri in resultado["fontes"]:
                st.markdown(f"- [{titulo}]({uri})")

    _mostrar_fontes_confiaveis(aberto=erro_nesta_busca or not resultado)
