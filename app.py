"""
Nutri IA — Assistente de apoio ao dia a dia do profissional nutricionista.

Módulos:
1. Consulta técnica  — dúvidas nutricionais rápidas com embasamento científico
2. Calculadora        — IMC, TMB, GET e faixa calórica por objetivo
3. Planejador          — transforma anotações de consulta em plano formatado
4. Lista de compras    — lista + substituições + versão simples a partir de um plano
5. Folhetos educativos — material em PDF para o paciente, a partir de um plano
"""

import streamlit as st

from config import (
    NOME_APP,
    DESCRICAO_APP,
    FATORES_ATIVIDADE,
    AJUSTE_OBJETIVO,
    PROMPT_CONSULTA,
    PROMPT_PLANEJADOR,
    PROMPT_LISTA_COMPRAS,
    PROMPT_FOLHETO,
)
from utils import (
    get_gemini_response,
    calcular_imc,
    calcular_tmb,
    calcular_get,
    calcular_faixa_calorica,
    markdown_para_docx,
    markdown_para_pdf,
    nome_arquivo,
)

st.set_page_config(page_title=NOME_APP, page_icon="🩺", layout="wide")

# ---------------------------------------------------------------------------
# Visual — painel clínico verde-petróleo
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] {
        background-color: #0f3d3e;
    }
    section[data-testid="stSidebar"] * {
        color: #eaf4f2 !important;
    }
    section[data-testid="stSidebar"] input, section[data-testid="stSidebar"] textarea {
        background-color: #134a4b !important;
        color: #ffffff !important;
        border: 1px solid #1e5a5b !important;
    }
    section[data-testid="stSidebar"] a {
        color: #9fd8cf !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: #1e5a5b !important;
    }
    div[data-testid="stSidebarUserContent"] .stCaption, section[data-testid="stSidebar"] .stCaption {
        color: #a9c9c4 !important;
    }
    .crn-badge {
        background-color: #134a4b;
        border-radius: 6px;
        padding: 10px 12px;
        font-size: 12.5px;
        color: #bcdad5;
        margin-top: 10px;
        line-height: 1.5;
    }
    button[data-baseweb="tab"] {
        font-weight: 500;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #0f3d3e !important;
    }
    div[data-baseweb="tab-highlight"] {
        background-color: #0f3d3e !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Barra lateral — identidade profissional, chave da API e contexto
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(f"### 🩺 {NOME_APP}")
    st.caption("Painel clínico do profissional")

    nome_nutricionista = st.text_input("Nome do nutricionista", key="nome_nutricionista", placeholder="Dra. Ana Souza")
    crn_nutricionista = st.text_input("CRN", key="crn_nutricionista", placeholder="12345-SP")
    if nome_nutricionista or crn_nutricionista:
        st.markdown(
            f'<div class="crn-badge">{nome_nutricionista or "Nome não informado"}<br>'
            f'{("CRN " + crn_nutricionista) if crn_nutricionista else "CRN não informado"}</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    # Se GEMINI_API_KEY estiver configurada em Secrets (Streamlit Cloud) ou em
    # .streamlit/secrets.toml (local), o app usa essa chave automaticamente e
    # não pede nada na tela — bom para uso restrito (ex.: só a família/equipe).
    # Sem essa configuração, cada pessoa cola a própria chave gratuita, o que
    # é melhor quando o link for compartilhado com mais gente.
    try:
        chave_automatica = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        chave_automatica = ""

    if chave_automatica:
        api_key = chave_automatica
        st.success("✅ Chave da API configurada para este app.")
    else:
        api_key = st.text_input(
            "Chave da API do Gemini",
            type="password",
            help="Gere gratuitamente em aistudio.google.com/apikey",
        )
        st.markdown("[Criar chave gratuita →](https://aistudio.google.com/apikey)")

    st.divider()
    if "contador_ia" not in st.session_state:
        st.session_state.contador_ia = 0
    st.caption(f"📊 Consultas à IA nesta sessão: **{st.session_state.contador_ia}**")
    st.caption(
        "Esse número conta só o que foi usado desde que essa aba foi aberta — "
        "não é o limite total da chave (o Google não publica mais esse número de "
        "forma fixa/confiável)."
    )

    st.divider()
    st.caption(
        "⚠️ O Nutri IA é uma ferramenta de apoio à decisão clínica. Ele não substitui o "
        "julgamento do profissional, avaliação clínica presencial nem literatura primária "
        "em decisões de alto impacto."
    )


def assinatura_rodape(texto_base: str = "") -> str:
    """Monta o rodapé dos documentos com a identidade do profissional, quando informada."""
    nome = st.session_state.get("nome_nutricionista", "")
    crn = st.session_state.get("crn_nutricionista", "")
    partes = [texto_base] if texto_base else []
    if nome or crn:
        assinatura = " — ".join(p for p in [nome, f"CRN {crn}" if crn else ""] if p)
        partes.append(assinatura)
    return "\n".join(partes)

if "historico_consulta" not in st.session_state:
    st.session_state.historico_consulta = []
if "plano_atual" not in st.session_state:
    st.session_state.plano_atual = ""

tab_consulta, tab_calc, tab_plano, tab_lista, tab_folheto = st.tabs(
    [
        "💬 Consulta técnica",
        "🧮 Calculadora",
        "📋 Planejador",
        "🛒 Lista de compras",
        "📄 Folhetos educativos",
    ]
)

# ---------------------------------------------------------------------------
# Aba 1 — Consulta técnica (chat)
# ---------------------------------------------------------------------------
with tab_consulta:
    st.subheader("Tire dúvidas técnicas rápidas durante o atendimento")
    st.caption(
        "Interações fármaco-nutriente, bases fisiológicas, comparação de abordagens "
        "dietéticas e embasamento científico para uma orientação."
    )
    st.caption(
        "🔎 Este módulo busca em fontes confiáveis na web (OMS, Ministério da Saúde, "
        "sociedades de nutrição, periódicos científicos) e lista as fontes usadas ao "
        "final de cada resposta."
    )

    if st.session_state.historico_consulta:
        col_limpar, _ = st.columns([1, 4])
        with col_limpar:
            if st.button("🗑️ Limpar histórico", key="btn_limpar_chat", use_container_width=True):
                st.session_state.historico_consulta = []
                st.rerun()

    # Janela com altura máxima: cresce junto com a conversa (poucas mensagens
    # ficam compactas, sem área vazia) e só passa a rolar internamente depois
    # de preencher o espaço — sem pesar a página nem perder o scroll automático.
    qtd_mensagens = len(st.session_state.historico_consulta)
    if qtd_mensagens == 0:
        janela_chat = st.container()
        with janela_chat:
            st.caption("💬 Sua conversa vai aparecer aqui. Digite sua dúvida abaixo para começar.")
    else:
        altura_chat = min(480, max(160, qtd_mensagens * 110))
        janela_chat = st.container(height=altura_chat)
        with janela_chat:
            for autor, mensagem in st.session_state.historico_consulta:
                with st.chat_message(autor):
                    st.markdown(mensagem)

    pergunta = st.chat_input("💬 Digite sua dúvida técnica e aperte Enter...")
    if pergunta:
        st.session_state.historico_consulta.append(("user", pergunta))
        with janela_chat:
            with st.chat_message("user"):
                st.markdown(pergunta)
            with st.chat_message("assistant"):
                with st.spinner("Consultando..."):
                    try:
                        resposta = get_gemini_response(
                            pergunta, api_key, PROMPT_CONSULTA, buscar_na_web=True
                        )
                        st.markdown(resposta)
                        st.session_state.historico_consulta.append(("assistant", resposta))
                        st.session_state.contador_ia += 1
                        sucesso = True
                    except (ValueError, RuntimeError) as erro:
                        st.error(str(erro))
                        sucesso = False
        if sucesso:
            # Rerun só quando deu certo: recalcula a altura da janela do chat
            # já com a nova mensagem. Em caso de erro, não rerodamos para não
            # apagar o aviso antes do profissional conseguir lê-lo.
            st.rerun()

# ---------------------------------------------------------------------------
# Aba 2 — Calculadora nutricional
# ---------------------------------------------------------------------------
with tab_calc:
    st.subheader("IMC, TMB, gasto energético e faixa calórica")
    st.caption("Cálculos de apoio à avaliação — sempre ajuste com seu julgamento clínico.")

    col1, col2 = st.columns(2)
    with col1:
        peso = st.number_input("Peso (kg)", min_value=1.0, max_value=400.0, value=70.0, step=0.5)
        altura = st.number_input("Altura (cm)", min_value=50.0, max_value=250.0, value=170.0, step=0.5)
        idade = st.number_input("Idade (anos)", min_value=1, max_value=120, value=30)
    with col2:
        sexo = st.radio("Sexo biológico", ["Feminino", "Masculino"], horizontal=True)
        formula_tmb = st.radio(
            "Fórmula da TMB", ["Mifflin-St Jeor", "Harris-Benedict"], horizontal=True
        )
        nivel_atividade = st.selectbox("Nível de atividade física", list(FATORES_ATIVIDADE.keys()))
        objetivo = st.selectbox("Objetivo (opcional)", ["—"] + list(AJUSTE_OBJETIVO.keys()))

    nome_paciente_calc = st.text_input("Nome do paciente (opcional, usado só no nome do arquivo)", key="calc_paciente")

    if st.button("Calcular", type="primary"):
        imc_resultado = calcular_imc(peso, altura)
        tmb_resultado = calcular_tmb(peso, altura, int(idade), sexo, formula_tmb)
        get_resultado = calcular_get(tmb_resultado, nivel_atividade)
        faixa_min = faixa_max = None
        if objetivo != "—":
            faixa_min, faixa_max = calcular_faixa_calorica(get_resultado, objetivo)

        st.session_state.calc_resultado = {
            "peso": peso, "altura": altura, "idade": idade, "sexo": sexo,
            "formula_tmb": formula_tmb, "nivel_atividade": nivel_atividade,
            "objetivo": objetivo, "imc": imc_resultado, "tmb": tmb_resultado,
            "get": get_resultado, "faixa_min": faixa_min, "faixa_max": faixa_max,
        }

    if st.session_state.get("calc_resultado"):
        r = st.session_state.calc_resultado
        with st.container(border=True):
            st.markdown("**INDICADORES ATUAIS**")
            c1, c2, c3 = st.columns(3)
            c1.metric("IMC", f"{r['imc']['imc']}", r['imc']['classificacao'])
            c2.metric(f"TMB ({r['formula_tmb']})", f"{r['tmb']:.0f} kcal/dia")
            c3.metric("GET (gasto total estimado)", f"{r['get']:.0f} kcal/dia")

            if r["faixa_min"] is not None:
                st.info(f"Faixa calórica estimada para **{r['objetivo'].lower()}**: {r['faixa_min']:.0f} – {r['faixa_max']:.0f} kcal/dia")

            st.caption(
                "O IMC não diferencia massa magra de massa gorda nem considera composição "
                "corporal — use como indicador de triagem, não diagnóstico. Os valores de TMB/GET "
                "são estimativas; ajuste conforme julgamento clínico e, quando disponível, métodos "
                "mais precisos (bioimpedância, calorimetria indireta)."
            )

            linhas_calc = [
                f"## Dados informados",
                f"- Peso: {r['peso']} kg",
                f"- Altura: {r['altura']} cm",
                f"- Idade: {r['idade']} anos",
                f"- Sexo biológico: {r['sexo']}",
                f"- Nível de atividade: {r['nivel_atividade']}",
                f"",
                f"## Resultados",
                f"- IMC: {r['imc']['imc']} ({r['imc']['classificacao']})",
                f"- TMB ({r['formula_tmb']}): {r['tmb']:.0f} kcal/dia",
                f"- GET (gasto energético total estimado): {r['get']:.0f} kcal/dia",
            ]
            if r["faixa_min"] is not None:
                linhas_calc.append(f"- Faixa calórica para {r['objetivo'].lower()}: {r['faixa_min']:.0f} – {r['faixa_max']:.0f} kcal/dia")

            titulo_calc = (
                f"Cálculos nutricionais — {nome_paciente_calc.strip()}"
                if nome_paciente_calc.strip()
                else "Cálculos nutricionais"
            )
            docx_calc = markdown_para_docx(
                titulo_calc,
                "\n".join(linhas_calc),
                assinatura_rodape(
                    "Valores estimados de apoio à decisão clínica — não substituem avaliação "
                    "completa nem métodos mais precisos (bioimpedância, calorimetria indireta)."
                ),
            )
            st.download_button(
                "⬇️ Baixar cálculos em .docx",
                data=docx_calc,
                file_name=nome_arquivo("calculos", nome_paciente_calc or "paciente", "docx"),
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )

# ---------------------------------------------------------------------------
# Aba 3 — Planejador nutricional
# ---------------------------------------------------------------------------
with tab_plano:
    st.subheader("Monte o plano alimentar do paciente")
    st.caption(
        "Preencha os campos que fizer sentido para esta consulta — não precisa preencher "
        "tudo. O que ficar em branco aparece como \"Não informado\" no documento final, "
        "sem o Nutri IA inventar nada no lugar."
    )

    col_a, col_b = st.columns(2)
    with col_a:
        nome_paciente = st.text_input("Nome do paciente", key="plano_paciente")
    with col_b:
        data_consulta = st.date_input("Data da consulta", key="plano_data", format="DD/MM/YYYY")

    objetivo_acompanhamento = st.text_area(
        "Objetivo do acompanhamento", height=80, key="plano_objetivo",
        placeholder="Ex.: emagrecimento, ganho de massa magra, controle glicêmico...",
    )
    orientacoes_gerais = st.text_area(
        "Orientações gerais", height=80, key="plano_orientacoes",
        placeholder="Ex.: fracionar refeições, mastigar devagar, evitar frituras...",
    )

    st.markdown("**Plano alimentar por refeição** (preencha as que se aplicarem)")
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        cafe_manha = st.text_area("Café da manhã", height=70, key="plano_cafe")
        almoco = st.text_area("Almoço", height=70, key="plano_almoco")
        lanches = st.text_area("Lanches", height=70, key="plano_lanches")
    with col_r2:
        jantar = st.text_area("Jantar", height=70, key="plano_jantar")
        ceia = st.text_area("Ceia", height=70, key="plano_ceia")

    col_c, col_d = st.columns(2)
    with col_c:
        alimentos_recomendados = st.text_area("Alimentos recomendados", height=80, key="plano_recomendados")
        hidratacao = st.text_area("Hidratação", height=70, key="plano_hidratacao")
    with col_d:
        alimentos_evitar = st.text_area("Alimentos a evitar/restringir", height=80, key="plano_evitar")
        suplementacao = st.text_area("Suplementação (se houver)", height=70, key="plano_suplementacao")

    observacoes = st.text_area(
        "Observações e próximos passos", height=80, key="plano_observacoes",
        placeholder="Ex.: retorno em 30 dias, solicitar exames, reavaliação antropométrica...",
    )
    anotacoes_livres = st.text_area(
        "Anotações adicionais (opcional)", height=100, key="plano_anotacoes_livres",
        placeholder="Qualquer outra observação da consulta que não se encaixe nos campos acima.",
    )

    if st.button("Gerar plano formatado", type="primary", key="btn_plano"):
        if not nome_paciente:
            st.warning("Informe pelo menos o nome do paciente para gerar o documento.")
        else:
            campos_preenchidos = {
                "Objetivo do acompanhamento": objetivo_acompanhamento,
                "Orientações gerais": orientacoes_gerais,
                "Café da manhã": cafe_manha,
                "Almoço": almoco,
                "Lanches": lanches,
                "Jantar": jantar,
                "Ceia": ceia,
                "Alimentos recomendados": alimentos_recomendados,
                "Alimentos a evitar/restringir": alimentos_evitar,
                "Hidratação": hidratacao,
                "Suplementação": suplementacao,
                "Observações e próximos passos": observacoes,
                "Anotações adicionais": anotacoes_livres,
            }
            if not any(v.strip() for v in campos_preenchidos.values()):
                st.warning("Preencha pelo menos um campo além do nome do paciente.")
            else:
                with st.spinner("Formatando plano..."):
                    try:
                        data_consulta_br = data_consulta.strftime("%d/%m/%Y")
                        blocos = [f"Nome do paciente: {nome_paciente}", f"Data da consulta: {data_consulta_br}"]
                        for titulo, valor in campos_preenchidos.items():
                            blocos.append(f"\n{titulo}: {valor.strip() if valor.strip() else '(não preenchido)'}")
                        prompt = "\n".join(blocos)
                        resultado = get_gemini_response(prompt, api_key, PROMPT_PLANEJADOR)
                        st.session_state.plano_atual = resultado
                        st.session_state.plano_paciente_nome = nome_paciente
                        st.session_state.contador_ia += 1
                    except (ValueError, RuntimeError) as erro:
                        st.error(str(erro))

    if st.session_state.plano_atual:
        with st.container(border=True):
            st.markdown(st.session_state.plano_atual)

            rodape = assinatura_rodape(
                "Este plano reflete a orientação individual do profissional e não substitui acompanhamento clínico contínuo."
            )
            docx_bytes = markdown_para_docx(
                f"Plano alimentar — {st.session_state.get('plano_paciente_nome', 'Paciente')}",
                st.session_state.plano_atual,
                rodape,
            )
            st.download_button(
                "⬇️ Baixar plano em .docx",
                data=docx_bytes,
                file_name=nome_arquivo("plano", st.session_state.get("plano_paciente_nome", "paciente"), "docx"),
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
            st.caption("💡 Este plano fica disponível nas abas Lista de Compras e Folhetos Educativos para gerar os materiais complementares.")

# ---------------------------------------------------------------------------
# Aba 4 — Lista de compras
# ---------------------------------------------------------------------------
with tab_lista:
    st.subheader("Lista de compras, substituições e versão simples para o paciente")

    usar_plano_atual = bool(st.session_state.plano_atual)
    origem = st.radio(
        "Plano de origem",
        (["Usar plano gerado no Planejador"] if usar_plano_atual else []) + ["Colar outro plano"],
        horizontal=True,
    )

    if origem == "Usar plano gerado no Planejador":
        plano_texto = st.session_state.plano_atual
        st.text_area("Plano em uso", plano_texto, height=150, disabled=True)
    else:
        plano_texto = st.text_area("Cole aqui o plano alimentar já pronto", height=220, key="lista_plano_colado")

    nome_paciente_lista = st.text_input("Nome do paciente", key="lista_paciente")

    if st.button("Gerar lista de compras", type="primary", key="btn_lista"):
        if not plano_texto or not nome_paciente_lista:
            st.warning("Informe o nome do paciente e o plano alimentar de origem.")
        else:
            with st.spinner("Gerando lista..."):
                try:
                    resultado = get_gemini_response(plano_texto, api_key, PROMPT_LISTA_COMPRAS)
                    st.session_state.lista_resultado = resultado
                    st.session_state.lista_paciente_nome = nome_paciente_lista
                    st.session_state.contador_ia += 1
                except (ValueError, RuntimeError) as erro:
                    st.error(str(erro))

    if st.session_state.get("lista_resultado"):
        with st.container(border=True):
            st.markdown(st.session_state.lista_resultado)
            docx_bytes = markdown_para_docx(
                f"Lista de compras — {st.session_state.get('lista_paciente_nome', 'Paciente')}",
                st.session_state.lista_resultado,
                assinatura_rodape("Material de apoio ao dia a dia — não substitui o plano alimentar original."),
            )
            st.download_button(
                "⬇️ Baixar lista em .docx",
                data=docx_bytes,
                file_name=nome_arquivo("lista-compras", st.session_state.get("lista_paciente_nome", "paciente"), "docx"),
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )

# ---------------------------------------------------------------------------
# Aba 5 — Folhetos educativos
# ---------------------------------------------------------------------------
with tab_folheto:
    st.subheader("Folhetos educativos em PDF a partir de um plano existente")

    usar_plano_atual_folheto = bool(st.session_state.plano_atual)
    origem_folheto = st.radio(
        "Plano de origem",
        (["Usar plano gerado no Planejador"] if usar_plano_atual_folheto else []) + ["Colar outro plano"],
        horizontal=True,
        key="origem_folheto",
    )

    if origem_folheto == "Usar plano gerado no Planejador":
        plano_texto_folheto = st.session_state.plano_atual
        st.text_area("Plano em uso", plano_texto_folheto, height=150, disabled=True, key="folheto_plano_view")
    else:
        plano_texto_folheto = st.text_area("Cole aqui o plano alimentar já pronto", height=220, key="folheto_plano_colado")

    tema = st.text_input(
        "Tema do folheto",
        placeholder="Ex.: hidratação, lanches práticos, como ler rótulos, substituições de açúcar...",
    )
    nome_clinica = st.text_input("Nome da clínica/nutricionista para o rodapé (opcional)")

    if st.button("Gerar folheto", type="primary", key="btn_folheto"):
        if not plano_texto_folheto or not tema:
            st.warning("Informe o plano de origem e o tema do folheto.")
        else:
            with st.spinner("Gerando folheto..."):
                try:
                    prompt = f"Plano alimentar:\n{plano_texto_folheto}\n\nTema do folheto: {tema}"
                    resultado = get_gemini_response(prompt, api_key, PROMPT_FOLHETO)
                    st.session_state.folheto_resultado = resultado
                    st.session_state.folheto_tema = tema
                    st.session_state.contador_ia += 1
                except (ValueError, RuntimeError) as erro:
                    st.error(str(erro))

    if st.session_state.get("folheto_resultado"):
        with st.container(border=True):
            st.markdown(st.session_state.folheto_resultado)
            rodape = nome_clinica or assinatura_rodape()
            pdf_bytes = markdown_para_pdf(
                f"Folheto — {st.session_state.get('folheto_tema', 'Orientação nutricional')}",
                st.session_state.folheto_resultado,
                rodape,
            )
            st.download_button(
                "⬇️ Baixar folheto em .pdf",
                data=pdf_bytes,
                file_name=nome_arquivo("folheto", st.session_state.get("folheto_tema", "paciente"), "pdf"),
                mime="application/pdf",
            )
