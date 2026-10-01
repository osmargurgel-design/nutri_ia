# Plano — Aba "Agenda" dentro do App Nutri IA

Este arquivo existe pra você abrir uma conversa nova e eu conseguir começar a
programar direto, sem precisar reexplicar as decisões já tomadas. Cole o texto
lá no final deste arquivo (seção "Como começar a conversa nova") pra começar.

## Contexto — por que isso é diferente da skill "agenda-profissional"

Já existe uma habilidade do Claude (`agenda-profissional`, ver
`claude/06_AGENDA_PROFISSIONAL_INSTANCIA.md`) que cria/consulta/remarca/cancela
compromissos direto numa conversa com o Claude, sem depender do app. Ela já
está testada e funcionando.

Este plano aqui é **diferente e adicional**: colocar essa mesma função **dentro
da tela do app Nutri IA** (uma 6ª aba, do lado das outras 5), pra que a Gabi
(e futuras nutricionistas que usarem o app) consiga agendar consulta sem sair
do app e sem precisar conversar com o Claude.

## Decisão de arquitetura (confirmada em 08/09/2026)

- **Login individual do Google ("Continuar com o Google")**, não
  compartilhamento manual de agenda. Decisão consciente pensando em escalar —
  se o app um dia tiver várias nutricionistas usando, cada uma conecta a
  própria conta, sem precisar compartilhar agenda manualmente com ninguém. A
  senha da pessoa nunca passa pelo nosso app — ela digita na tela oficial do
  Google.
- **Fase 1 (esta rodada): login por sessão, sem banco de dados.** A pessoa
  conecta a conta Google quando abre o app; se fechar a aba e voltar bem
  depois, pode precisar clicar em "Continuar com o Google" de novo (1 clique,
  não digita nada). Guardar a conexão de forma permanente entre visitas (pra
  nunca pedir de novo) fica pra uma fase futura, só se isso incomodar no uso
  real — exige um banco de dados leve, mais complexo, não vamos construir
  agora sem necessidade comprovada.
- **Enquanto for só a Gabi e poucos testadores:** o Google exige colocar o
  e-mail de cada testador numa lista dentro do Google Cloud Console (\"modo de
  teste\" do OAuth) — 1 minuto por pessoa, eu guio o usuário passo a passo.
- **Se um dia o app abrir pra qualquer nutricionista se cadastrar sozinha**
  (sem o usuário aprovar uma por uma): o Google vai exigir um processo de
  verificação formal do app (pode levar dias, pede política de privacidade
  publicada etc.). **Não resolver agora** — só documentado aqui como próximo
  degrau, pra não pegar o usuário de surpresa lá na frente.

## O que precisa ser construído

### 1. Configuração no Google Cloud Console (feita com o usuário, passo a passo, telas e nomes exatos de botão)

- Criar um projeto no Google Cloud (gratuito, sem cartão).
- Ativar a "Google Calendar API".
- Configurar a "Tela de consentimento OAuth" (nome do app, e-mail de contato).
- Escopo de permissão: **apenas** `calendar.events` (criar/ler/editar eventos
  — não dá acesso a e-mail, contatos nem outras partes da conta Google da
  pessoa).
- Criar um "ID do cliente OAuth" tipo "Aplicativo da Web", com o endereço do
  app no Streamlit Cloud cadastrado como redirecionamento autorizado.
- Adicionar o e-mail da Gabi (e de outros testadores) na lista de "Usuários de
  teste" do Google Cloud.
- Guardar o Client ID e o Client Secret nos **Secrets do Streamlit** — mesmo
  padrão de segurança já usado hoje pra chave do Gemini (nunca fica exposto no
  código nem no GitHub).

### 2. Mudanças no código

- `requirements.txt`: adicionar `google-auth`, `google-auth-oauthlib`,
  `google-api-python-client`.
- Novas funções (arquivo novo ou dentro de `utils.py`): gerar o link de
  "Continuar com o Google", processar a volta do Google com o código de
  autorização, guardar a conexão em `st.session_state` (memória da sessão
  atual do navegador).
- `config.py`: constantes do login (escopo de permissão, textos).
- `app.py`:
  - Nova 6ª aba **"📅 Agenda"**.
  - Se a pessoa ainda não conectou: mostra botão "Continuar com o Google".
  - Se já conectou: formulário pra criar consulta (nome do paciente, data,
    horário, tipo — primeira consulta ou retorno, duração, observações) +
    lista dos próximos compromissos já marcados.
  - Mesmas regras já validadas na skill: título padrão "Consulta — [Nome]" /
    "Retorno — [Nome]", nunca colocar dado clínico (diagnóstico, peso, exame)
    na descrição do evento — só informação logística, lembrete configurável.

### 3. Escopo desta primeira versão (fase 1) — pra não travar numa entrega grande demais

- ✅ Login individual (Continuar com o Google)
- ✅ Criar novo compromisso direto na aba
- ✅ Ver a lista dos próximos compromissos
- ⏸️ Remarcar/cancelar direto na aba — decidir na hora, conforme o tempo; pode
  ficar pra uma rodada seguinte sem problema (a skill via chat já cobre isso
  hoje).
- ⏸️ Busca de eventos de nutrição dentro do app — fora do escopo desta aba por
  enquanto (já funciona via skill/chat); focar primeiro na parte de
  compromissos de pacientes.

### 4. Testes antes de entregar (processo padrão do projeto)

1. `python -m py_compile` nos arquivos `.py`.
2. Rodar o app localmente (`streamlit run app.py`).
3. Prints das telas afetadas (Playwright) antes de mandar pro usuário.
4. Empacotar `.zip` e entregar — só ao final da rodada, não no meio de uma
   lista de pedidos (regra já combinada do projeto).

## Como começar a conversa nova

Abra uma conversa nova neste mesmo Projeto ("Nutri IA — App da Gabi") e cole
isto:

> Vamos implementar a aba "Agenda" no app Nutri IA, conforme o plano em
> `claude/07_AGENDA_NO_APP_PLANO.md`. Pode começar pelo passo 1 (configuração
> no Google Cloud Console), me guiando tela por tela.
