# 🧠 RAG Acadêmico com Few-shot | Cálculo, Álgebra Linear e Cálculo Numérico

Este projeto implementa um sistema de **RAG (Retrieval-Augmented Generation)** usando **CrewAI** com suporte a **Few-shot Prompting** para responder perguntas acadêmicas sobre Cálculo, Álgebra Linear e Cálculo Numérico.

Para a interface foi utilizado o framework Streamlit, garantindo uma experiência interativa e intuitiva para os usuários. 🚀

O sistema recupera informações de uma base que roda local na pasta knowledge e gera respostas fundamentadas, claras e precisas utilizando modelos do WatsonX(llama-4-maverick-17b-128e-instruct-fp8).

---
## Tecnologias
- CrewAI
- WatsonX
- Streamlit
- Python

## 🚀 Funcionalidades

- 🔍 Recuperação de informações acadêmicas via RAG.
- ✍️ Aplicação de Few-shot Prompting para melhorar a precisão das respostas.
- 🤖 Integração com modelos do WatsonX (IBM).
- 📚 Suporte a conteúdos de:
  - Cálculo 1, 2, 3 e 4
  - Álgebra Linear
  - Cálculo Numérico

---

## 🧠 Como funciona
### Ingestão:
Os documentos acadêmicos são processados e armazenados localmente.

RAG (Retrieval-Augmented Generation):
A pergunta do usuário é transformada em vetor e comparada à base para recuperar os documentos mais relevantes.

### Few-shot Prompting:
Um prompt é criado contendo exemplos bem definidos (few-shot) que guiam o comportamento do modelo.

### LLM:
O modelo do WatsonX recebe o contexto + pergunta + exemplos few-shot e gera a resposta.


## 📦 Instalação

### ✅ Clone o repositório:
git clone https://github.com/MariaR1t4/agent

cd agent

### ✅ Configure sua key e project no watsonX seguindo o padrão disponível em .env-example
MODEL=your_model_name

WATSONX_URL=your_url

WATSONX_APIKEY=your_api_key

WATSONX_PROJECT_ID=your_project

### ✅ Como rodar:
- Ative o ambiente virtual em /Scripts activate
- Rodar o comando streamlit run app.py
