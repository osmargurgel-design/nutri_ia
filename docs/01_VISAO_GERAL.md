# Visão Geral — Nutri IA

## O que é

O **Nutri IA** é um aplicativo web (feito em Streamlit, usando a API do Gemini do
Google) criado para apoiar o trabalho do dia a dia de um(a) nutricionista. Foi
inspirado no app "Professor IA" que o usuário já tinha para outra área.

Hoje o app é usado, no momento, **só pela sobrinha do usuário**, que é
nutricionista — está em fase de testes e melhorias antes de eventualmente ser
liberado para mais pessoas.

## Para quem é

O app fala com o **profissional de nutrição**, não diretamente com o paciente.
Ou seja, a linguagem das respostas de IA na aba de consulta técnica pode (e deve)
usar termos técnicos — só os documentos gerados para entregar ao paciente (plano,
lista de compras, folheto) usam linguagem simples.

## Onde está publicado

- **Código-fonte:** repositório `nutri_ia` no GitHub do usuário (conta
  `osmargurgel-design`), público.
- **App publicado:** Streamlit Community Cloud, link
  `https://nutri-ia-gabi.streamlit.app`
- **Chave da API do Gemini:** configurada automaticamente via "Secrets" do
  Streamlit Cloud (o app detecta sozinho — a nutricionista não precisa colar
  chave nenhuma no dia a dia).
- **Nome e CRN da nutricionista:** podem ficar nos mesmos Secrets
  (`NOME_NUTRICIONISTA` e `CRN_NUTRICIONISTA`) para já abrirem preenchidos.

## As 5 funcionalidades (abas do app)

1. **💬 Consulta técnica** — chat com IA para tirar dúvidas técnicas rápidas
   durante o atendimento. Usa busca na web em tempo real (Grounding with Google
   Search) e cita as fontes usadas ao final da resposta, priorizando fontes
   confiáveis (OMS, Ministério da Saúde, sociedades de nutrição, PubMed, SciELO).
2. **🧮 Calculadora** — calcula IMC, TMB (Mifflin-St Jeor ou Harris-Benedict), GET
   e faixa calórica por objetivo. Permite baixar os resultados em `.docx`.
3. **📋 Planejador** — formulário estruturado (não é mais texto livre) onde o
   profissional preenche campo por campo (objetivo, refeições, alimentos
   recomendados/evitar, hidratação, suplementação, observações). A IA só
   reformata/organiza em linguagem para o paciente — não inventa conteúdo
   clínico. Gera um `.docx` com o nome do paciente no título.
4. **🛒 Lista de compras** — a partir de um plano (gerado no Planejador ou colado
   manualmente), gera lista de compras por categoria, substituições inteligentes
   e uma versão simples para o paciente. Baixa em `.docx`.
5. **📄 Folhetos educativos** — a partir de um plano + um tema escolhido pelo
   profissional, gera um folheto educativo pronto para entregar ao paciente.
   Baixa em `.pdf`.

## Estilo visual

Paleta **"Verde sálvia clínico"** (escolhida em 17/09/2026): fundo da página
menta bem claro (`#EEF6F3`) com cartões e campos brancos, botões/abas em verde
`#2E8B7A`, barra lateral escura verde-petróleo (`#0F3D3E`) com o nome/CRN do
nutricionista em destaque. Os documentos Word/PDF seguem as mesmas cores
(títulos verdes, nome + CRN no cabeçalho). Cores centralizadas em `config.py`.

## Estado atual (resumo rápido)

✅ App funcionando em produção, testado pela sobrinha
✅ Deploy automático: toda vez que o usuário sobe mudança pro GitHub, o Streamlit
Cloud atualiza sozinho
✅ Chave de API automática (não exposta, via Secrets)
✅ Busca na web com fallback caso não esteja disponível na chave
✅ Contador de uso da IA na sessão (sem expor link da chave)
✅ Visual com paleta clínica e documentos com identidade visual

Veja `04_PROXIMOS_PASSOS.md` para o que ainda falta / ideias futuras, e
`05_CHANGELOG.md` para o histórico rodada a rodada.
