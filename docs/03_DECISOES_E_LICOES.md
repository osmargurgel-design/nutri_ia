# Decisões tomadas e lições aprendidas

Este arquivo existe para eu (Claude) não sugerir de novo algo que já foi decidido
ou já tentamos e não funcionou. Leia antes de propor mudanças de arquitetura,
provedor de IA, ferramenta de deploy, etc.

## Decisões de produto/arquitetura

- **Gemini em vez de Claude API**: decisão consciente, por causa do custo — o
  plano gratuito do Gemini atende bem o uso atual (uso interno, uma nutricionista).
  Não sugerir trocar para a API do Claude sem o usuário pedir explicitamente.
- **Streamlit em vez de outro framework**: o usuário já tinha familiaridade com
  Streamlit por causa do projeto "Professor IA" — manter o padrão.
- **GitHub + Streamlit Community Cloud** como forma de publicar: gratuito, e já
  validado que funciona para esse tipo de app. Não sugerir trocar de
  hospedagem sem motivo forte.
- **Chave de API automática (via Secrets) em vez de login/múltiplas chaves**:
  decisão consciente para a fase atual (só a sobrinha usa). Já foi discutido que,
  se um dia o app for liberado para mais pessoas, aí sim faz sentido considerar
  login ou chave por usuário — não é urgente agora.
- **Sem números fixos de limite de uso do Gemini na tela**: o Google parou de
  publicar uma tabela confiável de limites do plano gratuito. Em vez de mostrar
  número fixo (que ficaria errado com o tempo) ou linkar a chave da API (risco de
  segurança), o app mostra um **contador de uso dentro da sessão** (zera ao
  reabrir a aba) — decisão explícita do usuário: "dar o link da minha chave não é
  bom.. nem para consultar".
- **Planejador é um formulário estruturado, não texto livre**: versão inicial
  pedia pro nutricionista digitar anotações livres e a IA tentava adivinhar/
  perguntar de volta o que faltava — o usuário não gostou porque a IA ficava
  fazendo perguntas em vez de gerar o documento. Trocamos para campos separados
  (refeições, alimentos recomendados/evitar, hidratação etc.), onde cada campo
  vazio vira "Não informado nesta consulta" no documento, sem a IA inventar nem
  bloquear a geração. Só o nome do paciente é obrigatório.
- **Nome do paciente dentro do documento, não só no nome do arquivo**: pedido
  explícito do usuário, para facilitar identificar o documento depois de baixado.
  Já aplicado em Planejador, Lista de Compras e Calculadora (o título do
  documento inclui o nome quando informado).
- **Datas em formato brasileiro (DD/MM/AAAA)**: aplicado no campo de data do
  Planejador.
- **Aba "Agenda" no app (login individual do Google, não compartilhamento de
  agenda)**: decidido em 08/09/2026. Chegamos a considerar pedir pra Gabi
  compartilhar a agenda dela com uma conta "robô" do app (mais simples de
  construir), mas descartamos porque não escala — se um dia o app tiver várias
  nutricionistas usando, não dá pra ficar pedindo compartilhamento manual de
  cada uma. Decisão final: cada pessoa conecta a própria conta Google
  ("Continuar com o Google", como em outros apps) — a senha nunca passa pelo
  nosso app. Fase 1 (esta rodada): login válido só durante a sessão do
  navegador (sem banco de dados guardando a conexão entre visitas) — decisão
  consciente pra não construir complexidade sem necessidade comprovada. Ver
  plano completo em `claude/07_AGENDA_NO_APP_PLANO.md`.
- **Paleta "Verde sálvia clínico" (17/09/2026)**: o usuário achou o fundo
  branco simples demais. Foram mostradas 3 opções (Verde sálvia clínico, Azul
  saúde, Natural acolhedor) e ele escolheu a Verde sálvia, que mantém o
  verde-petróleo original. Regra seguida: fundo levemente tingido + cartões
  brancos — nada de fundo escuro ou muito colorido, porque atrapalha a leitura
  de textos longos. Cores ficam em `config.py` (não espalhar hex pelo código).
- **Nome/CRN via Secrets (17/09/2026)**: para não precisar digitar a cada
  visita, sem colocar dados pessoais no código (o repositório é público).

## Lições técnicas (para não repetir erro)

- **Nome de modelo do Gemini muda com o tempo.** Já tivemos um caso real: o app
  quebrou em produção com erro 404 porque `gemini-2.5-flash` foi descontinuado
  para novos usuários. Sempre que a IA parar de responder com erro tipo "model
  ... no longer available" ou "NOT_FOUND", a solução é trocar `GEMINI_MODEL` em
  `config.py` — a própria mensagem de erro do Google costuma indicar o nome novo.
- **Python 3.14 no Streamlit Cloud causou o app travar num loading infinito.**
  Se isso acontecer de novo, o primeiro passo é conferir a versão do Python nas
  "Advanced settings" do app no Streamlit Cloud e voltar para uma versão estável
  como 3.12.
- **Grounding with Google Search (busca na web) pode não estar disponível em
  toda chave gratuita** — pode depender de faturamento habilitado no Google
  Cloud. Por isso o app sempre tenta com busca primeiro e, se falhar, cai
  automaticamente para resposta sem busca + aviso com links de fontes confiáveis
  (não trava o app). Isso vale inclusive quando o erro é de cota da busca
  (429) — ver a lição logo abaixo.
- **Cota da busca esgotada = duas chamadas por pergunta = app lento.** Lição de
  17/09/2026: quando o fallback existe, ele precisa de memória — depois da
  primeira falha, não insistir na busca na mesma sessão. E erro 503
  (congestionamento do modelo) não tem fallback útil: avisar na hora.
- **Nunca transformar o fallback da busca em erro fatal.** Na rodada 8 o erro
  de cota (429) na chamada com grounding passou a virar mensagem de limite,
  sem tentar responder sem busca — e o app parou de responder em casos que
  antes funcionavam. Regra: cota da busca esgotada = responder sem busca com
  aviso; só mostrar "limite atingido" se a chamada sem busca também falhar.
- **`pkill -f "streamlit run"` matando o processo errado**: detalhe só relevante
  para quem está testando o app no ambiente de desenvolvimento — evitar matar
  processos com `pkill` encadeado no mesmo comando que sobe um novo servidor;
  preferir subir em portas novas.
- **fpdf2 pode dar erro "Not enough horizontal space"** com certas
  formatações — resolvido fixando a posição X antes de cada bloco de texto
  (`pdf.set_x(pdf.l_margin)`).
- **PDF com fonte Helvetica só aceita latin-1**: travessão, aspas curvas,
  reticências e emojis viravam "?". Solução adotada (17/09/2026): trocar esses
  caracteres por equivalentes em `_limpar_para_pdf` e remover emojis, em vez de
  embutir um arquivo de fonte no projeto. Negrito usa o modo `markdown=True` do
  fpdf2 — por isso "--" e "__" são neutralizados no texto (senão viram
  sublinhado/itálico sem querer).

## Sobre o jeito de trabalhar com o usuário

- **O usuário não é desenvolvedor.** Não conhece git, terminal, deploy — precisa
  de instruções passo a passo, telas, nomes exatos de botão/menu, sem pressupor
  conhecimento técnico.
- **Já tivemos bastante confusão de pastas no GitHub Desktop** (arquivos
  copiados na pasta errada, "0 changed files" aparecendo, etc.). O jeito que
  funcionou melhor: `File → Add local repository` apontando direto para uma
  pasta já com os arquivos extraídos do zip, criando um repositório novo do
  zero — evita esse tipo de confusão.
- **Esperar o usuário terminar de listar todos os pedidos de uma rodada** antes
  de gerar e entregar o `.zip` final — instrução explícita do usuário
  ("antes de ficar gerando app esperar.. pois tem mais pedidos..").
- **Sempre responder em português do Brasil** (decisão explícita, válida a
  partir de agora para todo o projeto).
