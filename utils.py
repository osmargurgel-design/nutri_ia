"""
Funções utilitárias do Nutri IA:
- chamada ao Gemini
- cálculos nutricionais (IMC, TMB, GET, faixa calórica)
- geração de arquivos .docx e .pdf para entrega ao paciente
"""

import io
import re
from datetime import datetime

from google import genai
from google.genai import types as genai_types

from config import (
    GEMINI_MODEL,
    FAIXAS_IMC,
    FATORES_ATIVIDADE,
    AJUSTE_OBJETIVO,
    RGB_ESCURA,
    RGB_PRIMARIA,
    RGB_FUNDO_SUAVE,
    RGB_CINZA,
)


# ---------------------------------------------------------------------------
# Gemini
# ---------------------------------------------------------------------------

def _eh_erro_de_limite(mensagem: str) -> bool:
    """True quando a mensagem de erro do Google indica limite de uso atingido."""
    texto = mensagem.lower()
    return "429" in texto or "quota" in texto or "resource_exhausted" in texto


def get_gemini_response(
    prompt: str,
    api_key: str,
    system_instruction: str,
    buscar_na_web: bool = False,
) -> str:
    """Envia um prompt ao Gemini com a instrução de sistema do módulo atual.

    Quando buscar_na_web=True, ativa o Grounding with Google Search: o Gemini
    pesquisa na web antes de responder e a função anexa ao final do texto uma
    lista "Fontes consultadas" com os links usados. Se a chave/conta não tiver
    esse recurso liberado (ele pode exigir faturamento habilitado no Google
    Cloud, dependendo do tipo de chave), a função tenta de novo sem busca em
    vez de quebrar — e sinaliza isso no texto retornado.

    Se o erro for de LIMITE DE USO (429/quota), não tenta de novo sem busca:
    mostra direto a mensagem de limite, para não confundir com "busca
    indisponível".

    Levanta uma exceção com mensagem amigável em português caso a chamada falhe
    (chave inválida, limite de uso atingido, etc.) para que a interface possa
    exibir o erro de forma clara ao nutricionista.
    """
    if not api_key:
        raise ValueError("Cole sua chave da API do Gemini na barra lateral antes de continuar.")

    client = genai.Client(api_key=api_key)

    if buscar_na_web:
        try:
            return _gerar_com_busca(client, prompt, system_instruction)
        except Exception as exc:  # noqa: BLE001 - fallback deliberado, sem busca
            if _eh_erro_de_limite(str(exc)):
                # A busca na web (grounding) tem cota própria, que costuma
                # acabar antes da cota normal do modelo. Nesse caso ainda vale
                # tentar responder sem busca — só se ESSA chamada também bater
                # no limite é que o profissional vê a mensagem de limite.
                motivo = (
                    "_⚠️ Cota da busca na web esgotada por enquanto (ela tem um limite "
                    "próprio, separado do limite geral, e é renovada com o tempo). Resposta "
                )
            else:
                motivo = (
                    "_⚠️ Busca em fontes na web não disponível com esta chave de API "
                    "(pode exigir faturamento habilitado no Google Cloud). Resposta "
                )
            aviso = (
                "\n\n---\n" + motivo +
                "gerada com o conhecimento do modelo, sem consulta em tempo real — "
                "vale conferir em fontes gratuitas e confiáveis antes de aplicar clinicamente: "
                "[Guia Alimentar para a População Brasileira](https://bvsms.saude.gov.br/bvs/publicacoes/guia_alimentar_populacao_brasileira_2ed.pdf), "
                "[Ministério da Saúde](https://www.gov.br/saude), "
                "[OMS/WHO](https://www.who.int), "
                "[SciELO](https://www.scielo.org) e "
                "[PubMed](https://pubmed.ncbi.nlm.nih.gov) — todas de acesso livre._"
            )
            texto = _gerar_sem_busca(client, prompt, system_instruction)
            return texto + aviso

    return _gerar_sem_busca(client, prompt, system_instruction)


def _gerar_com_busca(client, prompt: str, system_instruction: str) -> str:
    """Chama o Gemini com Grounding with Google Search ativado e anexa as
    fontes usadas ao final da resposta."""
    grounding_tool = genai_types.Tool(google_search=genai_types.GoogleSearch())
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=genai_types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=[grounding_tool],
        ),
    )
    texto = response.text

    try:
        metadata = response.candidates[0].grounding_metadata
        chunks = metadata.grounding_chunks if metadata else None
    except (AttributeError, IndexError):
        chunks = None

    if chunks:
        fontes = []
        vistos = set()
        for chunk in chunks:
            web = getattr(chunk, "web", None)
            if not web or not web.uri:
                continue
            if web.uri in vistos:
                continue
            vistos.add(web.uri)
            titulo = web.title or web.uri
            fontes.append(f"- [{titulo}]({web.uri})")
        if fontes:
            texto += "\n\n---\n**Fontes consultadas:**\n" + "\n".join(fontes)

    return texto


def _gerar_sem_busca(client, prompt: str, system_instruction: str) -> str:
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                system_instruction=system_instruction,
            ),
        )
        return response.text
    except Exception as exc:  # noqa: BLE001 - queremos capturar qualquer erro da API
        mensagem = str(exc)
        if _eh_erro_de_limite(mensagem):
            raise RuntimeError(
                "Limite de uso da API do Gemini atingido. Aguarde um pouco antes de tentar "
                "novamente ou verifique sua cota em aistudio.google.com."
            ) from exc
        if "API key" in mensagem or "API_KEY_INVALID" in mensagem:
            raise RuntimeError(
                "Chave da API inválida. Confira a chave colada na barra lateral."
            ) from exc
        raise RuntimeError(f"Erro ao consultar o Gemini: {mensagem}") from exc


# ---------------------------------------------------------------------------
# Calculadora nutricional
# ---------------------------------------------------------------------------

def calcular_imc(peso_kg: float, altura_cm: float) -> dict:
    altura_m = altura_cm / 100
    imc = peso_kg / (altura_m ** 2)
    classificacao = next(
        label for minimo, maximo, label in FAIXAS_IMC if minimo <= imc < maximo
    )
    return {"imc": round(imc, 1), "classificacao": classificacao}


def calcular_tmb(
    peso_kg: float,
    altura_cm: float,
    idade: int,
    sexo: str,
    formula: str = "Mifflin-St Jeor",
) -> float:
    """Calcula a Taxa Metabólica Basal (TMB) em kcal/dia.

    sexo: "Feminino" ou "Masculino"
    formula: "Mifflin-St Jeor" (padrão) ou "Harris-Benedict"
    """
    if formula == "Mifflin-St Jeor":
        base = 10 * peso_kg + 6.25 * altura_cm - 5 * idade
        tmb = base + 5 if sexo == "Masculino" else base - 161
    else:  # Harris-Benedict revisada
        if sexo == "Masculino":
            tmb = 88.362 + (13.397 * peso_kg) + (4.799 * altura_cm) - (5.677 * idade)
        else:
            tmb = 447.593 + (9.247 * peso_kg) + (3.098 * altura_cm) - (4.330 * idade)
    return round(tmb, 0)


def calcular_get(tmb: float, nivel_atividade: str) -> float:
    fator = FATORES_ATIVIDADE[nivel_atividade]
    return round(tmb * fator, 0)


def calcular_faixa_calorica(get: float, objetivo: str) -> tuple[float, float]:
    ajuste_min, ajuste_max = AJUSTE_OBJETIVO[objetivo]
    # para emagrecimento os ajustes são negativos, então min/max se invertem
    valores = sorted([get * (1 + ajuste_min), get * (1 + ajuste_max)])
    return round(valores[0], 0), round(valores[1], 0)


# ---------------------------------------------------------------------------
# Geração de documentos
# ---------------------------------------------------------------------------

# Links em Markdown [texto](url) viram "texto (url)" nos documentos
_RE_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")
# Trechos em **negrito** ou *itálico*
_RE_ENFASE = re.compile(r"(\*\*.+?\*\*|(?<!\*)\*(?!\s)[^*]+?(?<!\s)\*(?!\*))")


def _eh_linha_separadora(linha: str) -> bool:
    return bool(re.fullmatch(r"\s*([-*_])\s*(\1\s*){2,}", linha))


def markdown_para_docx(titulo: str, conteudo_md: str, rodape: str = "", cabecalho: str = "") -> bytes:
    """Converte um texto em Markdown simples (títulos ##, listas -, texto,
    **negrito**) em um arquivo .docx formatado com a paleta do app, retornando
    os bytes prontos para download.

    cabecalho: texto opcional (ex.: nome e CRN do nutricionista) exibido no
    topo de todas as páginas.
    """
    from docx import Document
    from docx.shared import Pt, RGBColor

    cor_escura = RGBColor(*RGB_ESCURA)
    cor_primaria = RGBColor(*RGB_PRIMARIA)
    cor_cinza = RGBColor(*RGB_CINZA)

    doc = Document()

    # Cores dos estilos de título (Title, Heading 1-3)
    for nome_estilo, cor in (("Title", cor_escura), ("Heading 1", cor_escura),
                             ("Heading 2", cor_primaria), ("Heading 3", cor_primaria)):
        try:
            doc.styles[nome_estilo].font.color.rgb = cor
        except KeyError:
            pass

    if cabecalho:
        paragrafo_cab = doc.sections[0].header.paragraphs[0]
        run_cab = paragrafo_cab.add_run(cabecalho)
        run_cab.font.size = Pt(9)
        run_cab.font.color.rgb = cor_primaria

    doc.add_heading(titulo, level=0)

    def adicionar_texto(paragrafo, texto: str):
        """Escreve o texto no parágrafo convertendo **negrito** e *itálico*."""
        texto = _RE_LINK.sub(r"\1 (\2)", texto)
        for parte in _RE_ENFASE.split(texto):
            if not parte:
                continue
            if parte.startswith("**") and parte.endswith("**") and len(parte) > 4:
                paragrafo.add_run(parte[2:-2]).bold = True
            elif parte.startswith("*") and parte.endswith("*") and len(parte) > 2:
                paragrafo.add_run(parte[1:-1]).italic = True
            else:
                paragrafo.add_run(parte)
        return paragrafo

    def titulo_limpo(texto: str) -> str:
        return texto.replace("**", "").strip()

    for linha in conteudo_md.splitlines():
        linha = linha.rstrip()
        if not linha or _eh_linha_separadora(linha):
            continue
        if linha.startswith("### "):
            doc.add_heading(titulo_limpo(linha[4:]), level=3)
        elif linha.startswith("## "):
            doc.add_heading(titulo_limpo(linha[3:]), level=2)
        elif linha.startswith("# "):
            doc.add_heading(titulo_limpo(linha[2:]), level=1)
        elif linha.lstrip().startswith(("- ", "* ")):
            adicionar_texto(doc.add_paragraph(style="List Bullet"), linha.lstrip()[2:])
        elif re.match(r"^\s*\d+\.\s", linha):
            adicionar_texto(doc.add_paragraph(style="List Number"), re.sub(r"^\s*\d+\.\s", "", linha))
        else:
            adicionar_texto(doc.add_paragraph(), linha)

    if rodape:
        doc.add_paragraph()
        p = doc.add_paragraph(rodape)
        for run in p.runs:
            run.italic = True
            run.font.size = Pt(9)
            run.font.color.rgb = cor_cinza

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


def markdown_para_pdf(titulo: str, conteudo_md: str, rodape: str = "", cabecalho: str = "") -> bytes:
    """Converte um texto em Markdown simples em um PDF pronto para impressão,
    com faixa de título na cor do app, subtítulos coloridos, **negrito** real
    e numeração de páginas.

    cabecalho: texto opcional (ex.: nome e CRN do nutricionista) exibido na
    faixa do título.
    """
    from fpdf import FPDF

    class PDFNutri(FPDF):
        def footer(self):
            self.set_y(-12)
            self.set_font("Helvetica", "", 8)
            self.set_text_color(*RGB_CINZA)
            self.cell(0, 6, f"Página {self.page_no()}", align="C")

    pdf = PDFNutri()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    largura = pdf.epw

    # Faixa de título
    altura_faixa = 30 if cabecalho else 24
    pdf.set_fill_color(*RGB_ESCURA)
    pdf.rect(0, 0, pdf.w, altura_faixa, style="F")
    pdf.set_xy(pdf.l_margin, 7)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(largura, 9, _limpar_para_pdf(titulo).replace("**", ""), new_x="LMARGIN", new_y="NEXT")
    if cabecalho:
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*RGB_FUNDO_SUAVE)
        pdf.cell(largura, 6, _limpar_para_pdf(cabecalho), new_x="LMARGIN", new_y="NEXT")
    pdf.set_y(altura_faixa + 8)

    def texto_corrido(texto: str, tamanho: int = 11, recuo: float = 0):
        pdf.set_font("Helvetica", "", tamanho)
        pdf.set_text_color(40, 40, 40)
        pdf.set_x(pdf.l_margin + recuo)
        pdf.multi_cell(largura - recuo, 6.5, texto, markdown=True, new_x="LMARGIN", new_y="NEXT")

    for linha in conteudo_md.splitlines():
        linha = linha.rstrip()
        if not linha:
            pdf.ln(2)
            continue
        if _eh_linha_separadora(linha):
            pdf.ln(1)
            pdf.set_draw_color(*RGB_FUNDO_SUAVE)
            pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + largura, pdf.get_y())
            pdf.ln(3)
            continue

        texto = _limpar_para_pdf(linha)
        pdf.set_x(pdf.l_margin)

        if texto.startswith("## ") or texto.startswith("### "):
            nivel = 3 if texto.startswith("### ") else 2
            pdf.ln(3)
            pdf.set_font("Helvetica", "B", 13 if nivel == 2 else 11.5)
            pdf.set_text_color(*RGB_PRIMARIA)
            pdf.multi_cell(largura, 8, texto[nivel + 1:].replace("**", ""), new_x="LMARGIN", new_y="NEXT")
            if nivel == 2:
                pdf.set_draw_color(*RGB_FUNDO_SUAVE)
                pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + largura, pdf.get_y())
                pdf.ln(2)
        elif texto.startswith("# "):
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 15)
            pdf.set_text_color(*RGB_ESCURA)
            pdf.multi_cell(largura, 9, texto[2:].replace("**", ""), new_x="LMARGIN", new_y="NEXT")
        elif texto.lstrip().startswith(("- ", "* ")):
            recuo_lista = 7 if texto.startswith((" ", "\t")) else 0
            y = pdf.get_y()
            pdf.set_fill_color(*RGB_PRIMARIA)
            pdf.ellipse(pdf.l_margin + recuo_lista + 1.2, y + 2.4, 1.8, 1.8, style="F")
            texto_corrido(texto.lstrip()[2:], recuo=recuo_lista + 5)
        else:
            texto_corrido(texto)

    if rodape:
        pdf.ln(5)
        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(*RGB_CINZA)
        pdf.multi_cell(largura, 5, _limpar_para_pdf(rodape), new_x="LMARGIN", new_y="NEXT")

    return bytes(pdf.output())


# Caracteres comuns em textos gerados pela IA que a fonte do PDF (Helvetica,
# só latin-1) não tem — trocados por equivalentes que ela tem.
_TROCAS_PDF = {
    "—": "-",    # — travessão
    "–": "-",    # – meia-risca
    "‒": "-",
    "−": "-",    # sinal de menos
    "“": '"', "”": '"', "„": '"',
    "‘": "'", "’": "'",
    "…": "...",  # reticências
    "•": "-",    # • marcador
    "→": "->",   # seta
    "≤": "<=", "≥": ">=",
    " ": " ",
    " ": " ", "​": "",
}


def _limpar_para_pdf(texto: str) -> str:
    """Prepara o texto para a fonte Helvetica do fpdf2 (só latin-1):
    - troca travessão, aspas curvas, reticências etc. por equivalentes;
    - converte links [texto](url) em "texto (url)";
    - converte *itálico* simples em texto normal (o negrito **x** é mantido,
      o fpdf2 desenha como negrito de verdade);
    - remove emojis e outros símbolos que a fonte não tem (antes viravam "?").
    Acentos do português (á, ç, õ...) são mantidos normalmente.
    """
    for original, troca in _TROCAS_PDF.items():
        texto = texto.replace(original, troca)
    texto = _RE_LINK.sub(r"\1 (\2)", texto)
    # "--" e "__" têm significado especial no modo markdown do fpdf2
    # (sublinhado/itálico); evita formatações acidentais.
    texto = re.sub(r"-{2,}", "-", texto)
    texto = texto.replace("__", "_")
    texto = re.sub(r"(?<!\*)\*(?!\s|\*)([^*]+?)(?<!\s)\*(?!\*)", r"\1", texto)
    texto = texto.encode("latin-1", errors="ignore").decode("latin-1")
    # Emoji removido no começo da linha pode deixar espaço sobrando
    texto = re.sub(r"^(\s*(?:[-*]|#{1,3}|\d+\.)\s)\s+", r"\1", texto)
    return texto


def nome_arquivo(prefixo: str, paciente: str, extensao: str) -> str:
    paciente_slug = re.sub(r"[^a-zA-Z0-9]+", "-", paciente.strip().lower()).strip("-") or "paciente"
    data = datetime.now().strftime("%Y-%m-%d")
    return f"{prefixo}-{paciente_slug}-{data}.{extensao}"
