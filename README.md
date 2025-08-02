# 🎓 Agente Acadêmico 

Sistema inteligente baseado em CrewAI e WatsonX para suporte acadêmico em múltiplas disciplinas, utilizando documentos PDF como base de conhecimento.

## ✨ Características Principais

- **🔄 Multidisciplinar**: Suporte para matérias como Matemática, Física, Computação, Engenharia e Estatística
- **📚 Gestão Inteligente de Documentos**: Organização automática por disciplina
- **🤖 Agentes Especializados**: Cada disciplina tem um agente com conhecimento específico
- **🌐 Interface Moderna**: Interface web intuitiva com Streamlit

# Instalação 

## Pré-requisitos
- Python 3.8+
- Git
- Acesso a um LLM (ex: IBM watsonx) ou fallback configurado
- Streamlit (vai ser instalado via requirements)

## 1. Clonar e preparar o ambiente

```bash
git clone <repo-url>
cd agent
python -m venv .venv
source .venv/bin/activate       # Linux/macOS
# .venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

## 2. Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz com, no mínimo:

```env
# Watsonx (LLM)
WATSONX_APIKEY=seu_api_key_aqui
WATSONX_PROJECT_ID=seu_project_id
WATSONX_API_BASE=https://<sua-regiao>.ml.cloud.ibm.com
WATSONX_LLM_MODEL=watsonx/meta-llama/llama-3-1-70b-instruct

# Embedder (knowledge)
WATSONX_EMBEDDER_MODEL_ID=ibm/granite-embedding-278m-multilingual

# Controle do LLM
TEMPERATURE=0
TOP_P=1
MAX_TOKENS=1024
SEED=0
```

> O código também tenta cair em nomes alternativos como `WATSONX_API_KEY` e `WATSONX_URL` para compatibilidade.

## 3. Preparar base de conhecimento

Crie pastas para disciplinas, por exemplo:

```bash
mkdir -p knowledge/matematica
```

Ou use o script para criar uma nova matéria:

```bash
python scripts/cria_metadata_basico.py "Cálculo Avançado" -n "Cálculo" -d "Estudo de limites, derivadas e integrais."
```

Isso cria `knowledge/calculo_avancado/metadata.yaml` com `name`, `code` e `description`.

## 4. Executar a interface

```bash
streamlit run app.py
```

Abra no navegador: `http://localhost:8501`

## 5. Uso rápido

- Selecione a disciplina na sidebar.  
- Digite pergunta/conceito/problema no chat.  
- Receba resposta com formatação técnica (LaTeX/código).

---

## Dica de debug

Para reindexar conhecimento caso algo falhe:

```python
# Dentro do código, com um objeto crew
crew.reset_memories(command_type="knowledge")
```

---

## Licença

MIT License

