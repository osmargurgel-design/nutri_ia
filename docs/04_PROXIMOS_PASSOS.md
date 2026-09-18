# Próximos passos / ideias futuras

Este arquivo é um backlog simples. Marque o que for feito e mova para o
`05_CHANGELOG.md` com a data.

## Em aberto no momento

- [x] **Skill "agenda-profissional" (via chat, sem depender do app)** — v0.3,
      revisada com Opus, testada end-to-end na conta pessoal do usuário
      (osmargurgel@gmail.com) em 08/09/2026. Todos os fluxos passaram: criar →
      consultar → remarcar → cancelar compromisso, lembretes nativos do Google
      Agenda funcionando, busca de eventos de nutrição com link de inscrição e
      preço, `suggest_time` cruzando corretamente com a agenda real. **Já
      funciona hoje**, independente do app — a Gabi pode usar assim que quiser,
      conectando o Google Calendar dela numa conversa com o Claude. Detalhes em
      `claude/06_AGENDA_PROFISSIONAL_INSTANCIA.md`.

- [ ] **Aba "Agenda" dentro do app Nutri IA (EM ANDAMENTO)** — próximo passo
      real: colocar a mesma função de agendamento **dentro da tela do app**,
      pra Gabi não precisar sair do app/conversar com o Claude pra marcar
      consulta. Decisão de arquitetura já fechada em 08/09/2026: cada usuária
      conecta a própria conta Google ("Continuar com o Google"), não
      compartilhamento manual de agenda — pensando em escalar pra mais
      nutricionistas no futuro. Plano técnico completo (passo a passo do
      Google Cloud Console + mudanças de código) em
      `claude/07_AGENDA_NO_APP_PLANO.md`. **Ainda não iniciado** — começar numa
      conversa nova, colando o texto sugerido no final desse arquivo de plano.

- [ ] **Nova aba "Redes Sociais" (conteúdo digital)** — ideia trazida pelo
      usuário em 20/08/2026: menu para gerar conteúdo para Instagram,
      Facebook e Status do WhatsApp (legenda, roteiro de reels/vídeo,
      carrossel, hashtags), com inspiração em técnicas de nutricionistas
      influenciadoras. Ainda não implementado — usuário está avaliando,
      pode vir junto com outros pedidos na mesma rodada.
      **Limitação técnica confirmada (pesquisa em 20/08/2026, página oficial
      de preços da API Gemini):** o plano gratuito do Gemini **não gera
      imagem nem vídeo** — só texto. Ou seja, dá para gerar de graça: legenda,
      roteiro/script de vídeo, ideias de carrossel, hashtags, ganchos de
      abertura, e ajuste/sugestão de texto para um vídeo que a nutricionista
      já gravou. NÃO dá para gerar foto nem editar vídeo de verdade sem
      habilitar cobrança (billing) na conta Google — isso é uma decisão que
      o usuário precisa tomar conscientemente se quiser essa parte no futuro,
      não é algo para implementar "de graça" por engano.

## Sugestões da reavaliação de 17/09/2026 (ainda não aprovadas para rodada)

- [ ] **Consulta técnica: respostas mais rápidas e sem alucinar, dentro do que o
      plano gratuito do Gemini permite** — pedido do usuário em 17/09/2026,
      depois de testar a aba e ver lentidão e uma pergunta fora do escopo
      (quantidade de profissionais cadastrados em SP) gerar resposta vazia.
      Ideias a avaliar juntos quando ele voltar dos testes: (1) instrução mais
      clara no prompt para a IA recusar educadamente perguntas que não sejam de
      nutrição/apoio clínico, em vez de tentar responder e falhar; (2) considerar
      um modelo Gemini mais rápido para essa aba (ex.: variante "flash-lite" ou
      equivalente disponível no plano gratuito no momento, com menos
      profundidade mas resposta mais ágil); (3) cache simples de perguntas
      repetidas na sessão. Ainda não implementado — aguardando o usuário
      terminar os testes atuais (rodada 8d) para decidir o que faz sentido.
- [ ] **Consulta técnica: aumentar a área visível do chat** — pedido do
      usuário em 17/09/2026, com print mostrando a resposta cortada numa
      caixinha pequena, precisando rolar, mesmo sobrando bastante espaço em
      branco na tela abaixo dela. Hoje a altura da janela do chat é calculada
      por `qtd_mensagens * 110`, limitada a um teto de 480px (ver `app.py`,
      aba Consulta técnica) — esse teto foi pensado lá atrás pra não pesar a
      tela com poucas mensagens, mas fica pequeno demais pra uma resposta
      longa. Ideia: aumentar esse teto (ou calcular a altura com base no
      tamanho do texto, não só na quantidade de mensagens) para aproveitar o
      espaço real da tela.
- [ ] **Chat da Consulta técnica com memória da conversa** — hoje cada
      pergunta vai sozinha para a IA; perguntas de continuação ("e para
      vegetarianas?") perdem o contexto. Enviar o histórico da sessão junto.
- [ ] **Calculadora com macronutrientes** — distribuição de proteína,
      carboidrato e gordura em gramas, peso ajustado e circunferência da
      cintura.
- [ ] **Histórico de pacientes entre visitas** — só se o app for aberto para
      mais nutricionistas; exige banco de dados e cuidado com LGPD.

## Visual: redesenhar o fundo da área de trabalho (18/09/2026)

O usuário confirmou que a Rodada 8 funcionou bem na barra lateral (verde) e
nas cores de texto, mas disse que o fundo da área principal (onde ficam as
abas e os formulários) ainda parece branco pra ele — o tingimento atual
(`COR_FUNDO = "#EEF6F3"`, um menta bem claro) pode estar sutil demais para
ser percebido como "não branco". Pedido: um layout mais bonito, "futurista"
e com foco em saúde — mas mantendo claro/leve (ele mesmo disse "e claro"),
não escuro.

- **Regra que já temos e deve continuar valendo** (`03_DECISOES_E_LICOES.md`):
  nada de fundo escuro ou muito colorido na área de trabalho — atrapalha a
  leitura de textos longos (planos alimentares, respostas da IA). Então o
  redesenho precisa ser "mais bonito e moderno" dentro do que já é claro, não
  uma mudança pra tema escuro.
- **Ideias a considerar quando for desenhar isso** (ainda não decidido):
  aumentar o contraste do tingimento atual (um verde mais perceptível, mas
  ainda claro) e/ou usar um gradiente sutil; dar mais destaque visual aos
  cartões brancos (sombra mais suave, cantos arredondados, uma borda fina na
  cor do tema) para o contraste entre "fundo" e "cartão" ficar mais óbvio;
  ícones/elementos gráficos discretos de saúde/nutrição; revisar espaçamento
  geral para parecer menos "formulário simples" e mais "produto". Precisa de
  um mockup/comparação visual antes de aplicar (como fizemos com as 3 opções
  de paleta na Rodada 8), para o usuário aprovar o estilo antes de eu mexer
  no código de verdade.

## Lentidão relatada em várias abas — mapeamento em andamento (18/09/2026)

Ao longo do dia 18/09/2026 o usuário reportou lentidão/erro de "modelo
congestionado" em sequência no Planejador, na Lista de Compras (mesmo
reaproveitando o plano já carregado, sem redigitar) e no Folheto (mesma
situação: mesmo plano já carregado, mesmo assim demorou muito).

- **Investigado (código):** as três abas chamam a IA pelo mesmo caminho
  simples (`get_gemini_response` sem busca na web, uma chamada só) — nenhuma
  delas foi alterada pela lógica de memória de sessão/chavinha de busca da
  Rodada 8c (essa lógica só existe na Consulta técnica). Reconferido em
  18/09/2026 (2ª rodada de investigação, depois de o usuário confirmar que o
  problema é consistente — sempre trava, sempre mensagem de congestionamento
  — e insistir que antes das minhas alterações era rápido): o modelo
  (`GEMINI_MODEL` em `config.py`) não mudou desde a Rodada 3; os prompts de
  cada aba (`config.py`) não ficaram mais longos/complexos nas últimas
  rodadas; não existe nenhum retry automático dentro do código do app nessas
  três abas.
- **Suspeita nova e mais concreta (18/09/2026):** o `requirements.txt` fixa
  `google-genai>=0.3` — SEM travar numa versão exata. Isso significa que, a
  cada novo "deploy" (cada vez que uma alteração é enviada ao GitHub e o
  Streamlit Cloud reinstala o projeto do zero), o Python pode baixar uma
  versão MAIS NOVA da biblioteca do Gemini do que a usada da última vez, sem
  eu ter pedido isso — coincide exatamente com o padrão relatado: cada rodada
  de mudança neste projeto força um redeploy, e é logo depois de um redeploy
  que o problema apareceu. Bibliotecas de API costumam adicionar, com o
  tempo, tentativas automáticas internas (retry com espera) quando o servidor
  responde 503/"sobrecarregado" — o que bateria com o padrão relatado: a tela
  demora bastante e só DEPOIS aparece a mensagem de congestionamento (a
  espera pode estar acontecendo dentro da própria biblioteca, silenciosamente,
  antes mesmo do app tentar de novo). **Ainda não confirmado nem testado** —
  é a hipótese mais concreta até agora, mais provável que "é só o Google
  devagar", porque explica por que isso só começou a acontecer depois das
  minhas alterações (o gatilho seria o redeploy, não o código em si).
- **Hipótese das tentativas automáticas TESTADA e DESCARTADA (18/09/2026):**
  antes de aplicar a correção, abri o código-fonte real da biblioteca do
  Gemini (versão mais nova disponível hoje, 2.24.0) para confirmar a teoria.
  A biblioteca até tem uma função de "tentar de novo automaticamente" (usa a
  ferramenta `tenacity`), mas ela só entra em ação quando o app pede
  explicitamente essa opção (`retry_options`) — o Nutri IA nunca configurou
  isso, então, por padrão, a biblioteca faz **uma tentativa só e já devolve o
  erro na hora**, sem espera escondida. Ou seja: essa hipótese específica não
  explica a demora. Fica só como boa prática travar a versão da biblioteca
  (evita surpresa de comportamento em deploys futuros), mas não é a causa da
  lentidão de hoje — avisado ao usuário para não prometer uma correção que
  não resolveria o problema de verdade.
- **Hipótese mais provável agora:** ou é congestionamento real do lado do
  Google nesse momento, ou o uso intenso de testes durante as rodadas de hoje
  (muitas chamadas seguidas, minhas e do usuário) esbarrou num limite de
  taxa (quantidade de pedidos por minuto) do plano gratuito, que o Google às
  vezes devolve com a mesma cara de "servidor sobrecarregado" (503) em vez de
  um aviso claro de limite. Não dá para confirmar essa parte daqui — não há
  acesso aos registros de uso da chave nem ao painel de cota em tempo real
  nesta sessão. Melhor teste possível: o usuário tentar de novo depois de um
  tempo sem usar o app (ex.: depois de uma hora, ou no dia seguinte) — se
  voltar a ficar rápido, reforça a teoria de limite de uso temporário; se
  continuar lento mesmo assim, é mais provável ser algo do lado do Google
  fora do nosso controle.

## Preenchimento mais rápido e "inteligente" entre abas (ideia trazida em 18/09/2026)

Pedido do usuário: agilizar o preenchimento dos relatórios e deixar o app mais
esperto sobre o que ele já sabe, para a Gabi digitar menos coisa repetida.
Exemplo dado por ele: se o nome do paciente for preenchido na Calculadora, o
app deveria sugerir o mesmo nome no Planejador e nas outras abas quando for o
mesmo plano/atendimento.

**Regra de segurança a manter em qualquer versão disto:** a Gabi atende vários
pacientes na mesma aba do navegador ao longo do dia. Autopreencher só pode
puxar o nome de onde a ligação é garantida (o mesmo plano carregado) — nunca
"lembrar" o nome do paciente anterior e aplicar sozinho em um documento de
outro paciente. Prefilled sempre editável, nunca campo travado.

- [ ] **Lembrar as últimas escolhas da Calculadora** (fórmula da TMB, nível de
      atividade) como padrão da próxima vez na mesma sessão — muitas consultas
      seguidas usam a mesma fórmula; só a Gabi ajusta quando for diferente.
- [ ] **Ideia maior, para avaliar com calma (não é só um ajuste pequeno):** um
      conceito de "paciente atual da sessão" no topo do app, que todas as abas
      leem por padrão — evitaria digitar o nome mais de uma vez em qualquer
      combinação de abas, não só nas ligadas a um plano. Precisa de mais
      conversa antes de implementar, pela mesma regra de segurança acima (não
      pode virar fonte de erro entre pacientes diferentes).
- [ ] **Planejador → Agenda: criar/sugerir compromisso a partir dos "próximos
      passos"** — ideia trazida em 18/09/2026. Quando o campo "Observações e
      próximos passos" do Planejador falar em retorno (ex.: "retorno em 30
      dias"), o app poderia detectar isso e oferecer criar o compromisso na
      agenda automaticamente, em vez da Gabi ter que fazer isso à parte.
      Depende de a aba "Agenda" dentro do app existir primeiro (ver item
      "Aba Agenda dentro do app Nutri IA" mais acima, ainda não iniciado) —
      ou, enquanto isso não sai, pode usar a skill `agenda-profissional` já
      pronta (conversa separada com o Claude). Pontos a resolver quando for
      desenhar isso: como interpretar datas relativas escritas em texto livre
      ("em 30 dias", "daqui a 3 semanas") sem inventar data errada, e nunca
      criar o compromisso sozinho sem a Gabi confirmar (sugerir, não agendar
      automaticamente).

## Ideias mencionadas ao longo do projeto (sem compromisso, avaliar quando fizer sentido)

- [ ] **Login ou chave por usuário**, caso o app seja liberado para mais
      pessoas além da sobrinha no futuro (hoje usa uma chave só, automática).
      Relacionado ao item "Aba Agenda" acima — o login com Google que vamos
      construir pra Agenda é só pra essa função; a chave do Gemini continua
      automática/compartilhada por enquanto, seguem sendo decisões separadas.
- [ ] Revisar periodicamente se `GEMINI_MODEL` (em `config.py`) ainda é válido —
      o Google descontinua modelos sem muito aviso.
- [ ] Acompanhar se o Grounding with Google Search (busca na web da aba
      Consulta técnica) passa a exigir faturamento — hoje já tem fallback, mas
      vale conferir de tempos em tempos.

## Como usar este arquivo

Quando o usuário pedir algo novo, adicione aqui como item pendente. Quando for
implementado e entregue, mova a linha para `05_CHANGELOG.md` com a data da
entrega e remova daqui.
