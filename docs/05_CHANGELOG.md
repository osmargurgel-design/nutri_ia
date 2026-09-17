# Changelog — Nutri IA

Histórico das rodadas de mudança, mais recente primeiro. Serve para eu (Claude)
e para você acompanharem o que já foi feito sem precisar reler a conversa toda.

---

## Rodada 8d — 2026-09-17 — Corrige resposta "vazia" na Consulta técnica

- Encontrado o motivo do "não funciona nem uma pergunta simples": em algumas
  perguntas (ex.: pedir um número que a IA não tem como saber, ou um tema que
  os filtros de segurança do Google barram) o Gemini devolve uma resposta sem
  nenhum texto. Antes, o app mostrava essa resposta vazia como se fosse normal
  — na tela aparecia só a linha do aviso "sem busca na web", sem nenhuma
  resposta de verdade, parecendo que o app tinha quebrado.
- Agora, quando isso acontece, o app mostra um erro claro explicando que a IA
  não conseguiu gerar uma resposta desta vez (e, quando for por causa dos
  filtros de segurança do Google, avisa isso especificamente) — em vez de
  fingir que respondeu.
- Esse problema já existia antes desta rodada; só ficou visível agora porque a
  Rodada 8c passou a anexar o aviso curto a toda resposta, inclusive às vazias.

## Rodada 8c — 2026-09-17 — Consulta técnica mais rápida e avisos melhores

Contexto: a cota da busca na web (grounding) estava esgotada na chave, então
cada pergunta fazia duas chamadas (com busca → falha → sem busca), demorando
10-15s e repetindo um aviso longo a cada resposta. Somou-se a isso um erro 503
do Google ("modelo congestionado"), que é do lado deles.

- **Memória da sessão:** assim que a busca falha uma vez, o app para de tentar a
  busca nas próximas perguntas daquela sessão — volta a ser uma chamada só.
  Recarregar a página faz ele tentar de novo.
- **Chavinha "🔎 Buscar em fontes na web"** na aba Consulta técnica (ligada por
  padrão). Desligada, a resposta sai mais rápida, sem lista de fontes.
- **Aviso curto:** o texto longo sobre a busca indisponível aparece só na
  primeira vez; depois, cada resposta leva só uma linha discreta.
- **Erro 503 (modelo congestionado):** mensagem clara em português, e sem
  segunda tentativa na hora (que só faria esperar o dobro pelo mesmo erro).

## Rodada 8b — 2026-09-17 — Correção do aviso de limite (mesmo dia)

- A rodada 8 tinha passado a mostrar "Limite de uso atingido" e PARAR quando a
  chamada com busca na web falhava por cota (429). Isso foi um erro: a busca na
  web (grounding) tem cota própria, que acaba bem antes da cota geral do modelo
  — e o app deixava de responder em situações em que a versão anterior
  respondia normalmente sem busca.
- Agora, quando a busca bate no limite, o app tenta de novo SEM busca e entrega
  a resposta com um aviso claro ("cota da busca na web esgotada por enquanto").
  A mensagem de limite só aparece se a chamada sem busca também for recusada.
- Nada no app consome cota sozinho: a IA só é chamada quando alguém clica em um
  botão ou envia uma pergunta.

## Rodada 8 — 2026-09-17 — Paleta "Verde sálvia clínico" + documentos + correções

- **Visual do app:** fundo da página trocado do branco puro para menta bem claro
  (`#EEF6F3`), com cartões e campos brancos por cima; botões, abas e seleções no
  verde `#2E8B7A`; barra lateral continua verde-petróleo (`#0F3D3E`). Cores
  centralizadas em `config.py` (constantes `COR_*` e `RGB_*`) e repetidas no
  `.streamlit/config.toml`.
- **Documentos com identidade visual:** Word (.docx) com títulos em verde e
  nome + CRN do nutricionista no cabeçalho de todas as páginas; PDF do Folheto
  com faixa verde-petróleo no topo (título + nome/CRN), subtítulos em verde,
  marcadores coloridos e número de página no rodapé.
- **Corrigido:** negrito (`**texto**`) aparecia com os asteriscos no PDF e no
  Word — agora vira negrito de verdade (itálico `*texto*` também no Word).
- **Corrigido:** travessão "—", aspas curvas e reticências viravam "?" no PDF —
  agora são trocados por equivalentes que a fonte do PDF tem. Emojis são
  removidos do PDF (antes viravam "?"). Links viram "texto (endereço)".
- **Nome e CRN já preenchidos:** o app lê `NOME_NUTRICIONISTA` e
  `CRN_NUTRICIONISTA` dos Secrets do Streamlit Cloud (continuam editáveis na
  tela). Sem configurar, funciona como antes.
- **Aviso de limite correto:** quando o limite de uso do Gemini acaba durante a
  Consulta técnica, o app agora mostra "Limite de uso atingido" em vez de
  "busca na web não disponível".
- **Texto da Calculadora:** campo do paciente agora diz que o nome aparece no
  título do documento e no nome do arquivo.

## Rodada 7 — 2026-09-08 — Skill "agenda-profissional" (v0.3)

- Criada a Claude Skill `agenda-profissional` — organiza a agenda de
  compromissos de pacientes no Google Calendário e busca eventos de nutrição
  sob demanda. **Não é código no app Streamlit** — é uma habilidade do Claude
  que usa o conector Google Calendar.
- Testada end-to-end na conta pessoal do usuário: criar, consultar, remarcar e
  cancelar compromissos, lembretes nativos (confirmado: popup disparou
  corretamente), busca de eventos com link de inscrição e preço.
- v0.1 → v0.2: arquitetura em camadas (skill + arquivo de instância),
  onboarding de 8 etapas, confidencialidade, templates.
- v0.2 → v0.3 (revisão Opus): corrigido `update_event` faltando na lista de
  ferramentas; eventos agora exigem link de inscrição e preço obrigatoriamente
  (feedback do usuário); verificação de conflitos obrigatória antes de criar;
  onboarding com fuso horário confirmável; validação de datas ambíguas/passadas;
  desambiguação de pacientes; `suggest_time` detalhado; alertas de urgência
  para eventos; templates de remarcação e cancelamento.
- Criado arquivo de instância de teste
  (`claude/06_AGENDA_PROFISSIONAL_INSTANCIA.md`) com configuração da conta
  pessoal — a ser refeito na conta da nutricionista quando for para produção.
- Criado lembrete recorrente pessoal (fora da skill): "IR sobre operações
  Trade — BTG", todo primeiro dia útil do mês.

## Rodada 6 — 2026-08-18 — Documentação do projeto

- Criada a pasta `docs/` com toda a documentação para configurar um Projeto no
  Claude (este conjunto de arquivos).

## Rodada 5 — 2026-08-18 — Chat mais bonito + ajustes finais

- Aba Consulta técnica: janela do chat agora cresce conforme o tamanho da
  conversa (antes tinha altura fixa grande, ficava vazia quando havia pouca
  conversa).
- Campo de digitar mensagem ficou mais visível/identificável.
- Adicionado botão "🗑️ Limpar histórico" (só aparece quando já existe conversa).
- Corrigido um bug em que a mensagem de erro (ex.: "cole sua chave") sumia antes
  do profissional conseguir ler, por causa do recarregamento automático da tela.
- Planejador: campo de data agora mostra formato brasileiro (DD/MM/AAAA).
- Nome do paciente incluído como título dentro do documento `.docx` gerado pela
  Calculadora (já existia no Plano e na Lista de Compras).

## Rodada 4 — 2026-08-18 — Calculadora, Planejador estruturado, contador de uso

- Calculadora: adicionada opção de baixar os resultados em `.docx`.
- Planejador: trocado de "anotações livres" para formulário estruturado por
  campo (objetivo, refeições, alimentos recomendados/evitar, hidratação,
  suplementação, observações) — só o nome do paciente é obrigatório; campos
  vazios aparecem como "Não informado" no documento, sem a IA inventar nem
  bloquear a geração.
- Removido o link direto para a chave da API da barra lateral (risco de
  segurança) — substituído por um contador de uso de IA dentro da sessão atual.
- Melhorada a mensagem de aviso quando a busca na web (grounding) não está
  disponível: agora sugere fontes gratuitas e confiáveis para conferir
  manualmente (Guia Alimentar, Ministério da Saúde, OMS, SciELO, PubMed).

## Rodada 3 — 2026-08-18 — Correção do modelo Gemini + deploy estável

- Corrigido erro 404 em produção: modelo `gemini-2.5-flash` foi descontinuado
  pelo Google para novos usuários — trocado para `gemini-3.6-flash` em
  `config.py`.
- Resolvido problema de app travando em loading infinito no Streamlit Cloud:
  causa era a versão do Python configurada (3.14); corrigido para 3.12.
- Chave da API do Gemini configurada via Secrets do Streamlit Cloud (automática
  para a nutricionista, sem precisar colar).
- Ativado Grounding with Google Search na aba Consulta técnica, com fallback
  automático caso a chave não tenha esse recurso liberado.

## Rodada 2 — 2026-08-17/18 — Deploy inicial (GitHub + Streamlit Cloud)

- Criado repositório `nutri_ia` no GitHub (público).
- Publicado o app no Streamlit Community Cloud
  (`nutri-ia-gabi.streamlit.app`).
- Configurado tema visual verde-petróleo/teal, sidebar com nome/CRN do
  nutricionista.

## Rodada 1 — 2026-08-17 — Primeira versão do app

- Criado o app Nutri IA do zero: 5 abas (Consulta técnica, Calculadora,
  Planejador, Lista de compras, Folhetos educativos), usando a API do Gemini.
- Baseado nas 5 skills de nutrição desenhadas anteriormente no projeto.
