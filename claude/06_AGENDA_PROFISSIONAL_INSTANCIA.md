
# Agenda Profissional — Arquivo de instância (fase de teste)

Este arquivo guarda as preferências confirmadas para uso da skill
`agenda-profissional`, conforme previsto na v0.3 (seção "Arquitetura: skill +
arquivo de instância"). **Importante: esta é a configuração de TESTE, feita na
conta pessoal do usuário (osmargurgel@gmail.com), não na conta da
nutricionista.** Quando a skill for de fato usada pela profissional, este
arquivo deve ser refeito com o onboarding completo na conta dela.

## Onboarding — status: valores de teste confirmados em 08/09/2026

- **Calendário usado:** `osmargurgel@gmail.com` (calendário principal — único
  pessoal disponível na conta; a conta também tem o calendário automático
  "Feriados no Brasil", só leitura).
- **Horário de atendimento (teste):** segunda a sexta, 8h–18h.
- **Duração padrão de consulta:** 50 minutos.
- **Intervalo entre consultas:** 15 minutos.
- **Preferência de lembrete:** 1 dia antes + 1 hora antes (notificação popup do
  Google Agenda).
- **Formato do título do evento:** "Consulta — [Nome]" (primeira vez) /
  "Retorno — [Nome]" (retorno).
- **Fuso horário:** America/Sao_Paulo.

## Eventos criados nesta fase de teste

- **Lembrete recorrente pessoal (fora do escopo da skill, criado à parte, sob
  pedido direto do usuário em 08/09/2026):** "Lembrete: conferir IR sobre
  operações Trade — BTG" — todo primeiro dia útil do mês, 9h–9h15, com
  lembrete no horário + 1 dia antes. Recorrência via RRULE
  `FREQ=MONTHLY;BYDAY=MO,TU,WE,TH,FR;BYSETPOS=1` (aproximação de "primeiro dia
  útil" — não desconta feriados nacionais, só fins de semana; se cair em
  feriado, o evento ainda aparece nesse dia).
- **Teste do fluxo de compromissos de paciente (08/09/2026):**
  - "Consulta — Paciente Teste 1" — 08/09/2026, 15h30–16h20. Lembrete de 1h
    antes disparou corretamente (confirmado pelo usuário).
  - "Consulta — Paciente Teste 2" — criada 09/09/2026 10h–10h50, depois
    **remarcada** via teste para 11h–11h50 (mesmo dia). Segue ativa no
    calendário.
  - "Consulta — Paciente Teste 3" — criada 09/09/2026 14h–14h50, depois
    **cancelada** via teste. Removida do calendário.

## Resultado da validação (08/09/2026)

Fluxo completo testado e funcionando: **criar → consultar agenda → remarcar →
cancelar**, todos com lembrete nativo do Google Agenda dando o aviso
corretamente. Skill validada na conta pessoal do usuário.

**Teste do `suggest_time` (08/09/2026):** pedido de horários livres para
09–15/09/2026, respeitando expediente (8h–18h) e excluindo fins de semana.
Resultado correto: a ferramenta identificou automaticamente o compromisso
"Consulta — Paciente Teste 2" (11h–11h50 em 09/09) como ocupado e devolveu os
blocos livres ao redor dele, confirmando que o cruzamento com a agenda real
funciona. Skill aplicou o intervalo de 15 min salvo para sugerir horários
concretos (ex.: 09/09 às 8h, 10/09 às 9h, 11/09 às 14h) em vez de blocos brutos.

## Próximo passo

- Perguntar ao usuário se quer excluir os eventos de teste remanescentes
  ("Consulta — Paciente Teste 1" e "Consulta — Paciente Teste 2", ambos ainda
  no calendário) para não poluir a agenda pessoal.
- Quando o usuário decidir levar a skill para a conta real da nutricionista,
  refazer o onboarding completo (9 etapas, v0.3) na conta dela e criar um novo
  arquivo de instância específico para ela.
