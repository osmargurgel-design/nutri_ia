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

- [ ] **Chat da Consulta técnica com memória da conversa** — hoje cada
      pergunta vai sozinha para a IA; perguntas de continuação ("e para
      vegetarianas?") perdem o contexto. Enviar o histórico da sessão junto.
- [ ] **Calculadora com macronutrientes** — distribuição de proteína,
      carboidrato e gordura em gramas, peso ajustado e circunferência da
      cintura.
- [ ] **Histórico de pacientes entre visitas** — só se o app for aberto para
      mais nutricionistas; exige banco de dados e cuidado com LGPD.

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
- [ ] Nome do paciente dentro do documento também na aba Folhetos educativos,
      caso um dia essa aba passe a ter campo de paciente (hoje ela usa
      tema/clínica, não nome de paciente).

## Como usar este arquivo

Quando o usuário pedir algo novo, adicione aqui como item pendente. Quando for
implementado e entregue, mova a linha para `05_CHANGELOG.md` com a data da
entrega e remova daqui.
