# Como configurar o Projeto "Nutri IA" no Claude

Este arquivo explica como montar um **Projeto** no Claude (a organização por pastas
que agrupa conversas + arquivos + instruções fixas). A ideia: qualquer chat novo
que você abrir dentro desse projeto já nasce sabendo o que é o Nutri IA, o que já
foi feito e onde paramos — sem você precisar reexplicar tudo.

---

## 1. Nome sugerido do projeto

```
Nutri IA — App da Gabi
```

(Pode usar outro nome, mas mantenha algo que deixe claro que é o app da sua sobrinha
nutricionista, já que você pode vir a ter outros projetos parecidos no futuro, tipo o
"Professor IA".)

---

## 2. Instruções do projeto (cole no campo "Instruções personalizadas" / "Custom instructions")

Ao criar o projeto, existe um campo onde você cola instruções fixas que valem para
toda conversa dentro dele. Cole exatamente isto:

```
Este projeto é sobre o app "Nutri IA": um assistente web feito em Streamlit + API
do Gemini, para uma nutricionista usar no dia a dia (consulta técnica com IA,
calculadora nutricional, planejador de dieta, lista de compras e folhetos
educativos para pacientes). O app já está em produção, publicado no Streamlit
Community Cloud, com o código no GitHub.

Sempre responda em português do Brasil.

Eu (o usuário) NÃO sou desenvolvedor — não conheço termos técnicos de programação,
git, terminal, deploy, etc. Preciso de instruções passo a passo, simples e diretas,
como se estivesse me guiando pela primeira vez a cada novo passo (menus, botões,
nomes exatos de tela). Evite jargão sem explicar.

Antes de propor mudanças grandes no código, leia os arquivos deste projeto,
principalmente docs/01_VISAO_GERAL.md, docs/03_DECISOES_E_LICOES.md e
docs/05_CHANGELOG.md, para não repetir decisões já tomadas nem sugerir de novo
algo que já tentamos e não funcionou.

Sempre que fizer uma alteração relevante no app, ao final: (1) gere o arquivo .zip
atualizado do projeto para eu baixar, (2) me diga exatamente o que mudou em
linguagem simples, e (3) me lembre do passo a passo de sempre para subir no GitHub
Desktop e conferir no Streamlit Cloud.

Não gere nem entregue o .zip no meio de uma lista de pedidos — espere eu terminar
de listar tudo que quero mudar numa rodada antes de gerar o app final, a não ser
que eu peça uma entrega intermediária.
```

---

## 3. Quais arquivos anexar ao projeto

Anexe estes arquivos (todos vêm dentro do .zip que já te mandei/mando a cada
atualização):

**Documentação (pasta `docs/`) — sempre anexar, são pequenos e é o que me dá contexto:**
- `docs/01_VISAO_GERAL.md`
- `docs/02_ARQUITETURA_TECNICA.md`
- `docs/03_DECISOES_E_LICOES.md`
- `docs/04_PROXIMOS_PASSOS.md`
- `docs/05_CHANGELOG.md`

**Código-fonte atual (para eu poder ler e editar sem perguntar de novo):**
- `app.py`
- `config.py`
- `utils.py`
- `requirements.txt`
- `README.md`

Não precisa anexar `.streamlit/config.toml`, `.gitignore` nem `.env.example` — são
pequenos e raramente mudam; se algum dia eu precisar deles eu peço.

⚠️ **Nunca anexe** o arquivo `.streamlit/secrets.toml` (se ele existir na sua
pasta) — é onde fica sua chave da API. Ele nunca deve sair do seu computador nem
ir para o GitHub.

---

## 4. Fluxo para os próximos chats

1. Abra uma conversa **dentro** do projeto "Nutri IA — App da Gabi" (não uma
   conversa solta).
2. Descreva o que você quer mudar ou o problema que apareceu.
3. Eu já vou ter acesso aos arquivos anexados acima — não precisa reexplicar o
   que é o app.
4. Quando eu terminar uma rodada de mudanças, atualize os arquivos anexados: baixe
   o novo .zip que eu te mandar, extraia, e recoloque os arquivos atualizados
   (principalmente os de `docs/`, que eu vou manter atualizados a cada rodada)
   no projeto, substituindo os antigos.

---

## 5. Checklist rápido de atualização dos anexos

Sempre que eu te entregar um novo .zip:

- [ ] Baixei o .zip e extraí
- [ ] Substituí no projeto do Claude: `app.py`, `config.py`, `utils.py` (se mudaram)
- [ ] Substituí no projeto do Claude: os arquivos da pasta `docs/` (eu sempre
      atualizo pelo menos o `05_CHANGELOG.md` a cada rodada)
- [ ] Copiei os mesmos arquivos para a pasta do repositório no GitHub Desktop,
      fiz commit e push
- [ ] Conferi o app publicado (o link no Streamlit Cloud) depois de alguns minutos
