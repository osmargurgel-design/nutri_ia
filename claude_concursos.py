"""
Aba Concursos — concursos públicos e processos seletivos para nutricionista.

IMPORTANTE (descoberto em 01/10/2026): o plano GRATUITO do Gemini não inclui
busca na web (Grounding with Google Search aparece como "Not available" na
página oficial de preços). Por isso a aba funciona, por padrão, com BUSCAS
PRONTAS (links de busca já filtrados, gratuitos e sempre atuais). A busca com
IA continua no código como opção avançada: só funciona se a conta Google do
usuário tiver cobrança ativada.

Regra central (decisão do usuário, 01/10/2026): a informação precisa ser
CONFIÁVEL. Por isso, na busca com IA:
- a lista só aparece se a busca na web do Gemini devolver fontes reais; sem
  fontes, o app NÃO mostra uma lista gerada só pelo conhecimento do modelo
  (ele não sabe o que está aberto hoje) e mostra links de portais oficiais;
- a IA é instruída a nunca inventar concurso, data, vaga ou salário;
- os links mostrados são os que a busca realmente usou (não os que a IA
  escreveria no texto, que poderiam ser inventados).
"""

from datetime import datetime, timedelta
from urllib.parse import quote_plus

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

# Interruptor interno: a busca com IA fica DESLIGADA enquanto o app usar a IA
# gratuita (sem busca na web). Quando passar a usar uma API que tenha busca na
# web liberada (Gemini com cobrança ativada ou outro modelo), basta trocar para
# True — o botão aparece e o restante do código já está pronto e testado.
BUSCA_IA_ATIVA = False

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
                _com_detalhe_tecnico(
                    "O Google não liberou a busca na web para esta chave. No plano gratuito do "
                    "Gemini a busca na web não está incluída (só em contas com cobrança "
                    "ativada). Use as buscas prontas acima, que são gratuitas.",
                    mensagem,
                )
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


NOMES_ESTADOS = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas", "BA": "Bahia",
    "CE": "Ceará", "DF": "Distrito Federal", "ES": "Espírito Santo", "GO": "Goiás",
    "MA": "Maranhão", "MT": "Mato Grosso", "MS": "Mato Grosso do Sul", "MG": "Minas Gerais",
    "PA": "Pará", "PB": "Paraíba", "PR": "Paraná", "PE": "Pernambuco", "PI": "Piauí",
    "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte", "RS": "Rio Grande do Sul",
    "RO": "Rondônia", "RR": "Roraima", "SC": "Santa Catarina", "SP": "São Paulo",
    "SE": "Sergipe", "TO": "Tocantins",
}

MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto",
         "setembro", "outubro", "novembro", "dezembro"]


def calcular_ano_ref(indice_mes: int, hoje: datetime) -> int:
    """Ano a que o mês escolhido se refere: mês que já passou neste ano
    (ex.: janeiro, estando em outubro) significa o PRÓXIMO ano."""
    return hoje.year if indice_mes >= hoje.month else hoje.year + 1


def _fmt_data_google(d: datetime) -> str:
    return f"{d.month}/{d.day}/{d.year}"  # formato M/D/AAAA que o Google exige


def _link_google(consulta: str, desde: datetime = None, ultimo_mes: bool = False,
                 noticias: bool = False) -> str:
    """Link de busca no Google. `desde` filtra por DATA DE PUBLICAÇÃO (só
    resultados publicados a partir dessa data) — é o que impede páginas
    antigas (anos anteriores) de aparecerem."""
    url = "https://www.google.com/search?q=" + quote_plus(consulta)
    if ultimo_mes:
        url += "&tbs=qdr:m"  # só resultados do último mês
    elif desde is not None:
        url += f"&tbs=cdr:1,cd_min:{_fmt_data_google(desde)}"
    if noticias:
        url += "&tbm=nws"  # aba Notícias
    return url


def montar_buscas(estado: str, mes: str, ano: int, incluir_residencias: bool,
                  hoje: datetime = None) -> list:
    """Monta buscas prontas (título, explicação, link). Não usa IA nem cota:
    cada link abre uma busca já filtrada, sempre com resultados do momento.

    Filtro de data automático (para nunca trazer páginas de anos anteriores):
    - mês atual: só publicações do último mês;
    - outro mês: só publicações dos últimos 90 dias;
    - panorama do ano atual: só publicações desde 1º de janeiro deste ano;
      de ano que vem: últimos 180 dias;
    - portais e Diário Oficial: últimos 180 dias.
    """
    hoje = hoje or _agora_brasil()
    mes_atual = MESES.index(mes) + 1 == hoje.month and ano == hoje.year
    onde = "" if estado == "Brasil todo" else f" {NOMES_ESTADOS.get(estado, estado)}"

    ha_90 = hoje - timedelta(days=90)
    ha_180 = hoje - timedelta(days=180)
    inicio_panorama = datetime(hoje.year, 1, 1) if ano == hoje.year else ha_180

    buscas = [
        (
            "✅ Inscrições abertas agora",
            f"Concursos de nutricionista com inscrição aberta em {mes} de {ano}.",
            _link_google(
                f'concurso nutricionista "inscrições abertas" {mes} {ano}{onde}',
                desde=ha_90, ultimo_mes=mes_atual,
            ),
        ),
        (
            "📰 Notícias de concursos de nutrição",
            "Notícias recentes sobre editais e abertura de inscrições.",
            _link_google(f"concurso nutricionista edital{onde}", ultimo_mes=True, noticias=True),
        ),
        (
            f"📅 Panorama de {ano}",
            f"Concursos previstos, abertos e encerrados em {ano}.",
            _link_google(f"concursos nutricionista {ano}{onde} edital", desde=inicio_panorama),
        ),
        (
            "🔎 No portal PCI Concursos",
            "Resultados do portal que reúne concursos (confira sempre no edital oficial).",
            _link_google(f"site:pciconcursos.com.br nutricionista{onde}", desde=ha_180),
        ),
        (
            "🏛️ Editais no Diário Oficial da União",
            "Editais federais publicados oficialmente.",
            _link_google("site:in.gov.br edital concurso nutricionista", desde=ha_180),
        ),
    ]
    if incluir_residencias:
        buscas.append(
            (
                "🩺 Residência multiprofissional (nutrição)",
                f"Processos seletivos de residência em saúde com vaga para nutrição em {ano}.",
                _link_google(f"residência multiprofissional nutrição edital {ano}{onde}", desde=ha_180),
            )
        )
    return buscas


def _mostrar_fontes_confiaveis(aberto: bool) -> None:
    with st.expander("🔗 Onde conferir direto nos portais oficiais", expanded=aberto):
        for nome, url, descricao in FONTES_CONFIAVEIS:
            st.markdown(f"- [{nome}]({url}) — {descricao}")
        st.caption(
            "Links da página inicial de cada site. Procure por \"concursos\" ou \"editais\" e "
            "pelo cargo de nutricionista."
        )


def _busca_com_ia(api_key: str, estado: str, incluir_residencias: bool) -> None:
    """Busca com IA (só aparece quando BUSCA_IA_ATIVA = True; ver o topo do arquivo)."""
    with st.container(border=True):
        st.markdown("**🤖 Busca com IA**")
        st.caption(
            "A IA monta uma lista com a fonte de cada concurso. Se a busca não devolver "
            "fontes, nenhuma lista é mostrada."
        )
        if st.button("Tentar busca com IA", key="btn_concursos_ia"):
            with st.spinner("Buscando concursos em fontes na web..."):
                try:
                    st.session_state.concursos_resultado = buscar_concursos(
                        api_key, estado, incluir_residencias
                    )
                    st.session_state.contador_ia += 1
                except SemFontesError as erro:
                    st.session_state.concursos_resultado = None
                    st.warning(str(erro))
                except (ValueError, RuntimeError) as erro:
                    st.session_state.concursos_resultado = None
                    st.error(str(erro))

        resultado = st.session_state.get("concursos_resultado")
        if resultado:
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


def render_aba_concursos(api_key: str) -> None:
    """Desenha a aba Concursos (chamada pelo app.py dentro da aba)."""
    agora = _agora_brasil()

    st.subheader("Concursos públicos para nutricionista")
    st.caption(
        "Útil para quem está começando a carreira: com um clique você abre buscas já "
        "filtradas (nutricionista + mês + estado) e vê o que está com inscrição aberta "
        "agora e o panorama do ano."
    )
    st.info(
        "ℹ️ Esta aba é independente das outras (não usa dados de paciente) e não gasta a "
        "cota da IA. Os links abrem buscas feitas na hora — **sempre confirme prazos e "
        "requisitos no edital oficial** antes de se inscrever."
    )

    col_estado, col_mes, col_resid = st.columns([2, 2, 3])
    # Mês escolhido já passado neste ano (ex.: janeiro, estando em outubro)
    # significa o PRÓXIMO ano — por isso o ano é calculado, não fixo.
    with col_estado:
        estado = st.selectbox("Abrangência", ESTADOS, key="concursos_estado")
    with col_mes:
        mes = st.selectbox("Mês", MESES, index=agora.month - 1, key="concursos_mes")
    with col_resid:
        incluir_residencias = st.checkbox(
            "Incluir residências multiprofissionais com vaga para nutrição",
            key="concursos_residencias",
        )

    indice_mes = MESES.index(mes) + 1
    ano_ref = calcular_ano_ref(indice_mes, agora)
    with st.container(border=True):
        st.markdown(f"**Buscas prontas — {mes} de {ano_ref}**")
        if ano_ref != agora.year:
            st.caption(f"Como {mes} já passou em {agora.year}, as buscas são para {mes} de {ano_ref}.")
        buscas = montar_buscas(estado, mes, ano_ref, incluir_residencias, hoje=agora)
        for titulo, descricao, url in buscas:
            st.markdown(f"- [{titulo}]({url}) — {descricao}")
        st.caption(
            "Dica: ao abrir um concurso, confira no edital o período de inscrição, a taxa, "
            "o número de vagas, o salário e os requisitos (inclusive o registro no CRN)."
        )

    _mostrar_fontes_confiaveis(aberto=False)
    if BUSCA_IA_ATIVA:
        _busca_com_ia(api_key, estado, incluir_residencias)
    else:
        st.caption(
            "ℹ️ O Nutri IA usa a versão gratuita da IA do Google, que não inclui busca na "
            "web. Por isso esta aba usa buscas prontas (gratuitas e sempre atuais) em vez "
            "de uma lista gerada pela IA."
        )
