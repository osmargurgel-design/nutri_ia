# Changelog — Nutri IA

Histórico das rodadas de mudança, mais recente primeiro. Serve para eu (Claude)
e para você acompanharem o que já foi feito sem precisar reler a conversa toda.

---

## Rodada 13 — 2026-10-01 — Chat com memória da conversa + modelo estável restaurado

- **Consulta técnica lembra da conversa:** as mensagens anteriores da sessão
  vão junto da nova pergunta, escritas no mesmo texto simples de sempre (sem
  mudar o formato de envio). Na primeira pergunta, o texto enviado é idêntico
  ao de antes. A IA só cumprimenta na primeira mensagem e pergunta se há mais
  dúvidas quando o assunto parece encerrado.
- **Modelo restaurado para `gemini-3.5-flash-lite`:** a troca feita em 21/09
  (que resolveu a lentidão/congestionamento do `gemini-3.6-flash`) não estava
  salva nos arquivos do Projeto e foi desfeita sem querer nesta rodada.
- **O que NÃO deu certo no meio do caminho:** enviar o histórico como vários
  turnos separados (formato multi-turno do Gemini) gerou erro
  `MALFORMED_FUNCTION_CALL`. Voltamos ao envio em texto único.
- **Lição:** depois de cada correção entregue, atualizar também os arquivos do
  Projeto no Claude (`config.py`, `utils.py`, `app.py`, docs) — senão a
  próxima entrega parte de uma versão desatualizada e desfaz a correção.

## Rodada 12 — 2026-10-01 — Consulta técnica: sem chavinha que não funciona + área de leitura maior

Aplica a regra do usuário "nada na tela que não funcione" (ver
`03_DECISOES_E_LICOES.md`) e resolve o pedido antigo de aumentar a área de
leitura do chat. Só o `app.py` mudou. O usuário confirmou que ficou bom.

- **12 — Chavinha "🔎 Buscar em fontes na web" removida da tela.** O plano
  gratuito do Gemini não tem busca na web, então a chavinha não fazia efeito.
  O texto que prometia "busca em fontes confiáveis e lista de fontes" também
  saiu (não era verdade). No lugar entrou uma nota curta: o app usa a versão
  gratuita da IA, que não inclui busca na web; as respostas vêm do
  conhecimento do modelo, sem lista de fontes, e convém conferir em fontes
  confiáveis (Guia Alimentar, Ministério da Saúde, OMS, SciELO, PubMed). A
  linha discreta no fim de cada resposta ("Resposta sem busca na web — confira
  as fontes antes de aplicar clinicamente") continua.
- **Mais rápida:** a pergunta vai direto para a IA (uma chamada só). Antes, cada
  sessão fazia uma tentativa de busca que sempre falhava.
- **Interruptor interno:** o código da busca continua no `app.py`, desligado
  por `BUSCA_WEB_DISPONIVEL = False` (logo depois dos imports). Trocar para
  `True` quando o app usar uma API com busca na web liberada.
- **12b — Área de leitura do chat maior.** Antes, a conversa ficava numa caixa
  com altura limitada (teto de 480 px) e rolagem própria; respostas longas
  eram cortadas e exigiam rolar toda hora (pedido do usuário em 17/09 e de
  novo em 01/10, com print). Agora o cartão da conversa não tem altura fixa:
  cresce com o texto e só a página rola. Verificado no navegador com resposta
  longa e duas perguntas seguidas (sem rolagem interna; campo de digitar
  continua fixo embaixo; "Limpar histórico" inalterado).
- Entregas: zips `rodada-12-consulta` e `rodada-12b-chat`, só com `app.py`.

## Rodada 11 — 2026-10-01 — Nova aba "Concursos" (buscas prontas e gratuitas)

Pedido: ajudar nutricionistas jovens, em início de carreira, a achar concursos
públicos (mês atual e ano, com inscrição ainda aberta), com informação confiável.
Plano geral em `claude/08_PLANO_JOVENS_PROFISSIONAIS_REDES_E_CONCURSOS.md`.

- **Nova aba "🏛️ Concursos"** (última aba, depois da Calculadora). Independente
  das outras: não usa dados de paciente e **não gasta a cota da IA**.
- **Como funciona:** o profissional escolhe a abrangência (Brasil todo ou um
  estado), o mês e, se quiser, residências multiprofissionais. O app monta
  buscas prontas (links do Google já filtrados): inscrições abertas agora,
  notícias, panorama do ano, portal PCI Concursos, Diário Oficial da União e
  residência. Abaixo, links dos portais oficiais (DOU, Cebraspe, FGV, Vunesp,
  IBFC, Ebserh, CFN, PCI Concursos — são páginas iniciais; não foram conferidos
  um a um). Aviso fixo: confirmar prazos e requisitos no edital oficial.
- **Ano e mês automáticos:** o mês já vem no mês atual. Se o mês escolhido já
  passou neste ano (ex.: janeiro, estando em outubro), o app entende como o
  ano seguinte (2027) e avisa isso na tela.
- **Filtro de data automático** (para não trazer páginas de anos anteriores):
  mês atual = só publicações do último mês; outro mês = últimos 90 dias;
  panorama do ano atual = desde 1º de janeiro; panorama do ano que vem, portais
  e Diário Oficial = últimos 180 dias. Validado com 720 combinações de
  datas/meses/estados (incluindo virada de ano), sem nenhum caso com ano
  anterior. O Google ainda decide o que mostrar, por isso o aviso do edital
  continua.
- **O que NÃO deu certo no meio do caminho:** a 1ª versão usava a busca na web
  da IA (Grounding with Google Search) para montar uma lista com fontes. Deu
  erro de "cota esgotada" logo no primeiro uso. Causa descoberta: **o plano
  gratuito do Gemini não inclui busca na web** (a página oficial de preços do
  Gemini marca "Not available" no plano gratuito, para os modelos Flash; só
  na conta com cobrança há 5.000 buscas grátis/mês e depois cerca de US$ 14
  por mil). Não era cota gasta nem erro do usuário.
- **Decisão do usuário:** ficar no gratuito (buscas prontas) e **não deixar na
  tela nenhum botão que não funcione**. O botão "Busca com IA" foi retirado da
  tela. O código dele continua em `concursos.py`, atrás do interruptor
  `BUSCA_IA_ATIVA = False` (topo do arquivo). Quando houver uma API com busca na
  web liberada (Gemini com cobrança ativada ou outro modelo gratuito com
  busca), basta trocar para `True`. Na tela fica só uma nota curta explicando
  por que a aba usa buscas prontas.
- **Arquivos:** `concursos.py` (novo) e `app.py` (só 3 pontos: importação, nome
  da aba nova e a chamada dentro dela). `utils.py`, `config.py` e
  `requirements.txt` não mudaram — nenhuma biblioteca nova.
- Entregas intermediárias no mesmo dia: 11, 11b (buscas prontas), 11c (sem o
  botão de IA), 11d (mês passado vira ano seguinte), 11e (filtro de data).
  O usuário confirmou que a aba ficou boa.

## Rodada 10 — 2026-09-18 — Colar ou carregar um plano já pronto no Planejador

- **Novo jeito de montar o plano:** a aba Planejador agora pergunta "Como você
  quer montar o plano desta consulta?" com duas opções — "Preencher o
  formulário" (o jeito de sempre, campo a campo) ou **"Colar ou carregar um
  plano já pronto"** (novo). Isso evita redigitar um plano que a nutricionista
  já tem pronto em outro lugar.
- **Colar o texto:** um campo simples para colar o plano já pronto.
- **Carregar arquivo:** também dá para enviar o arquivo direto (.docx do Word
  ou .pdf), desde que o texto seja "de verdade" (documento digitado, não
  escaneado/foto — isso não tem como ler sem reconhecimento de texto em
  imagem, que o app não faz; se o arquivo não tiver texto de verdade dentro,
  aparece um aviso explicando e pedindo para colar o texto).
- **Sem usar a IA:** o plano colado/carregado é usado exatamente como está,
  sem nenhuma reescrita — mais rápido, sem gastar cota da IA, e sem risco de
  a IA reinterpretar algo errado do plano.
- Assim que usado, o plano já fica disponível para a Lista de Compras e os
  Folhetos Educativos (com o preenchimento automático de nome que já existia
  desde a Rodada 9) e pode ser baixado em `.docx`, igual a um plano gerado
  pelo formulário.
- Corrigido, durante os testes: o texto colado/carregado aparecia "grudado"
  num parágrafo só na pré-visualização da tela (o `.docx` baixado já saía
  certo, quebrado em parágrafos) — agora a quebra de linha original aparece
  certinha na tela também.
- Nova biblioteca adicionada ao projeto: `pypdf` (leitura de texto de PDF) —
  gratuita, mesmo padrão das outras bibliotecas já usadas no app.

## Rodada 9 — 2026-09-18 — Preenchimento automático de nomes + Calculadora independente

- **Nome do paciente preenchido automaticamente:** ao gerar um plano no
  Planejador e depois abrir a Lista de Compras ou os Folhetos usando "Usar
  plano gerado no Planejador", o nome do paciente já vem preenchido — não
  precisa digitar de novo. Continua editável (dá para trocar a qualquer
  momento) e, se você trocar para "Colar outro plano", o campo é limpo
  automaticamente (só quando não foi editado à mão) para não sugerir o nome
  errado num plano diferente.
- **Aba Folhetos ganhou campo de nome do paciente** (antes só tinha tema e
  nome da clínica) — o nome aparece no título do documento gerado e ajuda a
  identificar o arquivo depois.
- **Nome/CRN do nutricionista preenchidos automaticamente no Folheto:** o
  campo "Nome da clínica/nutricionista para o rodapé" agora já vem com o
  nome e CRN da barra lateral, sem precisar digitar de novo — continua
  editável para quem preferir assinar diferente (ex. nome da clínica).
- **Corrigido, durante os testes desta rodada:** a aba Folhetos não estava
  selecionando automaticamente "Usar plano gerado no Planejador" quando um
  plano já existia — ficava presa em "Colar outro plano" por causa de um
  detalhe de como o Streamlit lembra a seleção de um campo. Agora, assim que
  um plano existir pela primeira vez na sessão, tanto a Lista de Compras
  quanto os Folhetos selecionam ele automaticamente (e continuam respeitando
  se você trocar manualmente depois).
- **Calculadora agora é a última aba** (antes era a 2ª, logo depois de
  Consulta técnica) — e ganhou um aviso deixando claro que ela é
  independente: o nome de paciente preenchido ali não é usado em nenhuma
  outra aba, e vice-versa.
- Nada mudou na geração de texto pela IA (prompts, modelo) nem na aparência
  visual das cores — só esses ajustes de preenchimento e organização das
  abas.

## Rodada 8e — 2026-09-18 — Detalhe técnico nos erros de IA (para conferência)

Contexto: o usuário reportou que o Planejador (que sempre usou pouca IA e era
rápido) passou a mostrar "modelo congestionado" com frequência, e pediu pra
confirmar se a mensagem era mesmo verdadeira ou se tinha algo errado no app.

- **Conferido:** o Planejador continua chamando a IA exatamente como sempre
  chamou — uma chamada só, sem busca na web. Nada nas rodadas 8/8b/8c/8d
  mudou isso. A mensagem de "congestionado" só aparece quando o texto do erro
  devolvido pela própria Google contém "503"/"unavailable"/"overloaded" — ou
  seja, reflete um erro real do lado da Google, não é inventada pelo app;
  antes ela aparecia do mesmo jeito, só que com o texto técnico cru em inglês
  em vez dessa frase mais clara.
- **Adicionado:** agora, quando esse erro (ou o de "resposta vazia sem
  motivo") acontecer, a mensagem na tela traz uma segunda linha com o detalhe
  técnico original por trás da tradução — assim dá pra conferir com certeza,
  sem depender de acesso aos registros do Streamlit Cloud.

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
  (Removida da tela na Rodada 12.)
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
  conversa). (Altura limitada removida na Rodada 12b: agora o cartão não tem
  altura fixa.)
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
