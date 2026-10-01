# Plano: apoio a nutricionistas jovens (carreira, redes sociais e concursos)

Anotado em 01/10/2026, a pedido do usuário. Segue a regra do projeto: uma
funcionalidade por vez, entrega deployável a cada passo, só mudança aditiva
(sem refatorar o que já funciona).

## Status (atualizado em 01/10/2026)

- **Frente B — Concursos: ENTREGUE** (Rodada 11, ver `05_CHANGELOG.md`), numa
  versão **gratuita com buscas prontas** (links já filtrados por mês, estado e
  data), e não com a lista gerada pela IA como o desenho abaixo previa. Motivo:
  o plano gratuito do Gemini não tem busca na web. A versão com IA está
  guardada no código (`concursos.py`, interruptor `BUSCA_IA_ATIVA = False`).
- **Frente A — Redes Sociais (Instagram e LinkedIn): próxima etapa**, ainda não
  iniciada.
- **Frente C — apoio à carreira inicial:** só ideias, sem compromisso.

## Por quê (mudança de foco do app)

Hoje o app é usado só pela Gabi (sobrinha do usuário). O usuário quer que ele
passe a ajudar **nutricionistas jovens, que estão começando a carreira**, em
duas frentes além do atendimento:

1. **Captar pacientes/clientes** — com apoio de conteúdo para redes sociais
   (Instagram e LinkedIn).
2. **Concursos públicos** — saber, com informação confiável, quais concursos
   para nutricionista estão acontecendo **neste mês** (principalmente os que
   ainda têm inscrição aberta) e **no ano**.

Isto amplia o público (ver `01_VISAO_GERAL.md`) e aproxima o app da ideia de
"liberar para mais pessoas" já registrada em `04_PROXIMOS_PASSOS.md`.

## Frente A — Temas de posts (LinkedIn e Instagram)

Evolui a aba "Redes Sociais" que já está no backlog (ideia de 20/08/2026).
Continua valendo a limitação confirmada: **plano gratuito do Gemini gera só
texto** (legenda, roteiro, carrossel, hashtags, ganchos), não imagem nem
vídeo. **Regra do usuário:** nada na tela que não funcione com o plano
gratuito.

**Banco de temas sugerido** (a nutricionista escolhe um tema, o app gera o
texto; o usuário ajusta a lista conforme for testando):

- Instagram (captar pacientes, linguagem simples e próxima):
  mitos e verdades de alimentação; "o que eu como num dia" (sem promessa de
  resultado); dicas rápidas de compras e substituições; receitas práticas;
  bastidores do consultório; quando procurar um nutricionista (sinais);
  perguntas frequentes de pacientes; datas de saúde do mês (campanhas do
  calendário de saúde).
- LinkedIn (autoridade profissional, rede de contatos, vagas e parcerias):
  início de carreira (primeiros passos, estágio, primeiro emprego);
  como se posicionar como recém-formada; resumo de estudo/artigo explicado em
  linguagem simples; áreas de atuação (clínica, esportiva, materno-infantil,
  hospitalar, saúde pública); bastidores de concursos e residência; casos
  anônimos de aprendizado (sem identificar paciente).
- Calendário editorial mensal: o app poderia sugerir 4 a 8 temas por mês,
  alternando Instagram e LinkedIn, ligados a datas de saúde do mês.

**Regras de segurança e ética (conferir antes de implementar):**
- A publicidade de nutricionistas é regulada pelo Conselho Federal de
  Nutricionistas (Código de Ética e de Conduta; do que lembro, é a Resolução
  CFN nº 599/2018, **a confirmar na fonte oficial antes de usar**). Em geral:
  sem promessa de resultado, sem "antes e depois", sem sensacionalismo, sem
  expor paciente. O prompt da aba deve instruir a IA a respeitar isso e o app
  deve mostrar um aviso curto: "revise o texto conforme o Código de Ética do
  CFN/CRN antes de publicar".
- Nunca gerar texto com dado de paciente real identificável.

## Frente B — Concursos públicos (mês atual e ano) — ENTREGUE

**Objetivo:** ajudar a ver concursos para nutricionista, com destaque para
**inscrições ainda abertas no mês** e uma visão do **ano**, com informação
confiável.

**O que foi entregue (Rodada 11):** aba com buscas prontas (links do Google já
filtrados) por abrangência (Brasil/estado), mês e residências; ano calculado
automaticamente (mês que já passou = ano seguinte); filtro de data de
publicação (nunca traz anos anteriores); links dos portais oficiais; aviso de
conferir o edital. Não gasta cota da IA.

**Princípio que continua valendo (decisão do usuário): a informação precisa
ser confiável.** Para qualquer versão futura com IA:
- Nunca inventar concurso, data, vaga ou salário; só mostrar o que veio de
  busca com fonte. Se não achou, dizer que não achou.
- Cada item com fonte e link, de preferência o **edital oficial**.
- Campos mínimos: órgão, cargo/área, vagas, salário, período de inscrição,
  banca, taxa, link do edital, data da consulta.
- Sem fontes = sem lista (mostrar só links oficiais). **Nunca** preencher a
  lista com o conhecimento do modelo (ele não sabe o que está aberto hoje).

**Por que a versão com IA não foi para a tela:** a busca na web do Gemini
(Grounding with Google Search) **não está disponível no plano gratuito**
(confirmado em 01/10/2026 na página oficial de preços). A versão com IA já está
pronta no código, desligada (`BUSCA_IA_ATIVA = False` em `concursos.py`).

**Para o futuro:** ligar quando houver API com busca na web (Gemini com
cobrança ou outro modelo gratuito). Perguntas a revisar na hora: abrangência,
alerta de prazo, integração com a Agenda (lembrete do fim da inscrição —
sugerir, nunca criar sozinho).

## Frente C — Ideias de apoio à carreira inicial (sem compromisso)

- Checklist do início de carreira (registro no CRN, documentos, primeiros
  passos para abrir consultório ou atender online).
- Banco de modelos de texto: bio de Instagram/LinkedIn, mensagem de
  apresentação, resposta a perguntas comuns de pacientes.
- Guia de preparação para concurso (conteúdo programático comum: nutrição
  clínica, saúde coletiva, legislação do SUS), apenas como apoio de estudo, com
  fontes.

## Ordem

1. ✅ Aba **Concursos** (entregue em 01/10/2026).
2. **Redes Sociais** com banco de temas (Instagram e LinkedIn) e aviso de
   ética do CFN — próxima etapa.
3. Calendário editorial mensal e itens da Frente C.

## Pontos em aberto

- Decisão sobre uso de busca na web paga (billing) × só plano gratuito
  (por ora: só gratuito).
- Se o app será aberto a mais usuárias, isso reabre as decisões de login/chave
  por usuário (já registradas em `04_PROXIMOS_PASSOS.md`).
