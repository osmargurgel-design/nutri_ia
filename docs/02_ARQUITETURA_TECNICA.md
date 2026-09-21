# Arquitetura Técnica — Nutri IA

## Stack

- **Frontend/backend**: [Streamlit](https://streamlit.io) (Python) — um único app
  web, sem separação front/back tradicional.
- **IA**: API do Google Gemini, via pacote `google-genai` (NÃO usar o pacote
  antigo `google-generativeai`, que está descontinuado).
- **Modelo atual**: definido na constante `GEMINI_MODEL` em `config.py` (ver nota
  sobre troca de modelo abaixo).
- **Geração de documentos**: `python-docx` (arquivos `.docx`) e `fpdf2`
  (arquivos `.pdf`).
- **Deploy**: GitHub (código) → Streamlit Community Cloud (hospedagem gratuita,
  redeploy automático a cada push).

## Estrutura de arquivos

```
nutri_ia/
├── app.py                 # App principal — telas, abas, lógica de interface
├── config.py               # Prompts de sistema, modelo do Gemini, dados de apoio
├── utils.py                 # Funções: chamada à IA, cálculos, geração de docx/pdf
├── requirements.txt         # Dependências Python
├── README.md                 # Instruções de instalação/deploy (para referência)
├── .streamlit/config.toml   # Tema visual (cores)
├── .gitignore                # Garante que segredos não vão pro GitHub
├── .env.example               # Exemplo de variável de ambiente local
└── docs/                       # Esta pasta de documentação do projeto
```

## `app.py` — como está organizado

1. Configuração da página (`st.set_page_config`) + CSS customizado (cores da
   sidebar, badge do CRN, estilo das abas).
2. Barra lateral (`st.sidebar`): nome/CRN do nutricionista, detecção automática
   da chave da API (via `st.secrets`, com campo manual como alternativa),
   contador de uso da IA na sessão, aviso legal fixo.
3. Função `assinatura_rodape()`: monta o rodapé (nome + CRN) que aparece nos
   documentos gerados.
4. `st.session_state` guarda: histórico do chat, resultado da calculadora, plano
   atual gerado, contador de uso, etc. — é o que faz o app "lembrar" de uma ação
   pra outra dentro da mesma sessão do navegador.
5. Cinco abas (`st.tabs`), uma para cada funcionalidade — código explicado em
   `01_VISAO_GERAL.md`.

## `config.py` — prompts e dados de apoio

Cada funcionalidade tem um prompt de sistema próprio (`PROMPT_CONSULTA`,
`PROMPT_PLANEJADOR`, `PROMPT_LISTA_COMPRAS`, `PROMPT_FOLHETO`), todos construídos
sobre uma base comum (`SYSTEM_PROMPT_BASE`) que define regras gerais: nunca
inventar informação clínica, diferenciar consenso de evidência controversa, não
dar diagnóstico, etc.

Também guarda tabelas de apoio da calculadora (`FAIXAS_IMC`, `FATORES_ATIVIDADE`,
`AJUSTE_OBJETIVO`).

## `utils.py` — funções puras

- `get_gemini_response(...)`: função central que chama a API do Gemini. Se
  `buscar_na_web=True`, tenta usar Grounding with Google Search (busca em tempo
  real); se a chave não tiver esse recurso liberado, cai automaticamente para
  uma resposta sem busca + aviso ao profissional com links de fontes confiáveis
  para conferir manualmente.
- `calcular_imc`, `calcular_tmb`, `calcular_get`, `calcular_faixa_calorica`:
  cálculos puros da calculadora nutricional.
- `markdown_para_docx` / `markdown_para_pdf`: convertem o texto (Markdown
  simples) gerado pela IA em arquivo `.docx`/`.pdf` formatado, pronto pra
  baixar.
- `nome_arquivo`: gera nome de arquivo com nome do paciente + data.

## Sobre a chave da API e o modelo do Gemini

- A chave fica guardada nos **Secrets** do Streamlit Cloud (configurado direto na
  nuvem, nunca no código nem no GitHub). O app lê `st.secrets["GEMINI_API_KEY"]`
  primeiro; se não encontrar, mostra um campo manual (útil para testes locais ou
  se um dia o app for usado por mais pessoas, cada uma com sua chave).
- O Google **muda o nome dos modelos do Gemini com alguma frequência** e
  aposenta versões antigas sem muito aviso. Se o app parar de funcionar com um
  erro tipo "model ... is no longer available" ou "404 NOT_FOUND", é só trocar o
  valor de `GEMINI_MODEL` em `config.py` pelo nome novo (a própria mensagem de
  erro geralmente já diz qual é). Já aconteceu uma vez (`gemini-2.5-flash` →
  `gemini-3.6-flash`) — ver `03_DECISOES_E_LICOES.md`.

## Testes feitos antes de cada entrega

Antes de qualquer atualização ser entregue, o processo padrão é:
1. `python -m py_compile` nos arquivos `.py` (garante que não há erro de sintaxe).
2. Rodar o app localmente (`streamlit run app.py`) num ambiente de teste.
3. Tirar prints automáticos das telas afetadas (via Playwright) para conferir
   visualmente antes de mandar pro usuário.
4. Empacotar tudo num `.zip` e entregar.
