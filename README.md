# 🥗 Nutri IA

Assistente de apoio ao dia a dia do profissional nutricionista, usando Gemini (gratuito).

---

## 🚀 Como rodar localmente

### 1. Clone ou baixe os arquivos
```
nutri_ia/
├── app.py
├── config.py
├── utils.py
├── requirements.txt
└── README.md
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Rode o app
```bash
streamlit run app.py
```

### 4. Configure sua chave da API
- Acesse [aistudio.google.com](https://aistudio.google.com/apikey)
- Crie uma chave gratuita (sem cartão)
- Cole na barra lateral do app

---

## ☁️ Deploy no Streamlit Cloud (grátis)

### Passo 1 — Suba o projeto no GitHub
Crie um repositório e suba apenas estes arquivos:
```
nutri_ia/
├── app.py
├── config.py
├── utils.py
├── requirements.txt
├── .env.example
└── .gitignore
```
⚠️ **NUNCA** suba `.env` nem `.streamlit/secrets.toml` — o `.gitignore` já os protege.

---

### Passo 2 — Crie o app no Streamlit Cloud
1. Acesse [share.streamlit.io](https://share.streamlit.io) e faça login com GitHub
2. Clique em **"New app"**
3. Selecione seu repositório e o arquivo `app.py`
4. Clique em **"Deploy!"**

---

### Passo 3 — Configure a chave da API com segurança
Ainda na tela de deploy (ou depois em **Settings > Secrets**):

Clique em **"Advanced settings"** → aba **"Secrets"** e cole:
```toml
GEMINI_API_KEY = "cole_sua_chave_aqui"
```

O app lê automaticamente essa chave — ninguém vê, nem fica exposta no código. ✅

---

### Resultado
Seu app terá um link público tipo:
```
https://seu-usuario-nutri-ia.streamlit.app
```
Funciona no celular, tablet e computador. Pode compartilhar com sua equipe!

---

## 📋 Funcionalidades

- ✅ **Consulta técnica** — chat de apoio para dúvidas nutricionais do dia a dia, com busca em fontes confiáveis na web (veja abaixo)
- ✅ **Calculadora** — IMC, TMB (Mifflin-St Jeor / Harris-Benedict), GET e faixa calórica por objetivo
- ✅ **Planejador** — transforma anotações de consulta em plano alimentar formatado (.docx)
- ✅ **Lista de compras** — lista consolidada, substituições inteligentes e versão simples para o paciente (.docx)
- ✅ **Folhetos educativos** — material em PDF sobre temas do plano, pronto para imprimir/enviar
- ✅ Respostas sempre ancoradas no plano já existente — nunca inventa orientação clínica do zero
- ✅ Gratuito com Gemini 2.5 Flash (~250 perguntas/dia)

---

## 🔎 Busca em fontes confiáveis (Consulta técnica)

A aba **Consulta técnica** usa o recurso *Grounding with Google Search* da API do Gemini: antes de responder, o modelo pesquisa na web e prioriza fontes como OMS, Ministério da Saúde, Guia Alimentar para a População Brasileira, sociedades de nutrição e periódicos científicos. As fontes usadas aparecem automaticamente ao final de cada resposta, como links clicáveis.

⚠️ **Atenção:** a disponibilidade desse recurso na chave gratuita "sem cartão" do Google AI Studio pode variar — em alguns casos ele só é liberado com faturamento habilitado no Google Cloud. O app já trata isso automaticamente: se a busca não estiver disponível na sua chave, ele responde mesmo assim (usando o conhecimento do modelo) e avisa isso na própria resposta, em vez de travar. Se quiser confirmar a disponibilidade e os custos atuais desse recurso, veja a documentação oficial: [Grounding with Google Search](https://ai.google.dev/gemini-api/docs/google-search).

---

## ⚠️ Limites do plano gratuito do Gemini (2026)

| Modelo | Req/min | Req/dia |
|---|---|---|
| Gemini 2.5 Flash | 10 | 250 |
| Gemini 2.5 Pro | 5 | 100 |

Para uso clínico individual, o limite gratuito costuma ser suficiente. A busca com fontes (grounding) tem cota e regras próprias, separadas desse limite — veja a seção acima.

---

## ⚠️ Aviso importante

O Nutri IA é uma ferramenta de **apoio à decisão clínica** para o profissional nutricionista.
Ele não substitui o julgamento clínico, a avaliação presencial do paciente nem a literatura
científica primária em decisões de maior complexidade ou risco.
