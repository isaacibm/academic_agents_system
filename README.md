# 🎓 Agente Acadêmico 

Sistema inteligente baseado em CrewAI para suporte acadêmico em múltiplas disciplinas, utilizando documentos PDF como base de conhecimento.

## ✨ Características Principais

- **🔄 Multidisciplinar**: Suporte para Matemática, Física, Computação, Engenharia e Estatística
- **📚 Gestão Inteligente de Documentos**: Organização automática por disciplina
- **🤖 Agentes Especializados**: Cada disciplina tem um agente com conhecimento específico
- **🎯 Múltiplos Tipos de Tarefa**: Responder perguntas, explicar conceitos, resolver problemas
- **📊 Sistema de Avaliação**: Análise automática da qualidade das respostas
- **🌐 Interface Moderna**: Interface web intuitiva com Streamlit

## 🏗️ Arquitetura do Sistema

```
agent/
├── 📱 app.py                     # Interface Streamlit
├── ⚙️ main.py                    # Funções principais
├── 🤖 crew.py                    # Configuração do CrewAI
├── 📁 config/
│   ├── 👥 agents.yaml           # Configuração dos agentes
│   ├── 📋 task.yaml             # Configuração das tarefas
│   └── 📚 few-shot.py           # Exemplos de treinamento
├── 🛠️ utils/
│   ├── 📄 document_processor.py  # Processamento de documentos
│   ├── 📊 subject_manager.py     # Gerenciamento de disciplinas
│   └── 🔍 response_evaluator.py  # Avaliação de respostas
├── 📚 knowledge/                 # Base de conhecimento
│   ├── matematica/              # Documentos de matemática
│   ├── fisica/                  # Documentos de física
│   ├── computacao/              # Documentos de computação
│   ├── engenharia/              # Documentos de engenharia
│   ├── estatistica/             # Documentos de estatística
│   └── 🔧 subjects_config.json   # Configuração das disciplinas
└── 📊 logs/                     # Logs e avaliações
```

## 🚀 Instalação e Configuração

### Pré-requisitos

- Python 3.8+
- Watsonx AI ou outro modelo LLM configurado
- Streamlit

### Instalação

1. **Clone o repositório:**
```bash
git clone <repository-url>
cd agent
```

2. **Instale dependências:**
```bash
pip install -r requirements.txt
```

3. **Configure variáveis de ambiente:**
```bash
# Configurar credenciais do LLM
WATSONX_API_KEY="sua_chave_aqui"
WATSONX_PROJECT_ID="seu_projeto_aqui"
WATSONX_API_BASE="url_watsonx"
MODEL_ID="model_id_watsonx"
```

4. **Organize seus documentos:**
```bash
# Coloque documentos PDF na pasta knowledge/
mkdir -p knowledge/{matematica,fisica,computacao,engenharia,estatistica}
```

## 📚 Disciplinas Suportadas

### 🧮 Matemática
- Cálculo Diferencial e Integral
  - Álgebra Linear
- Geometria Analítica
- Análise Matemática
  - Cálculo Numérico

### ⚛️ Física
- Mecânica Clássica
- Eletromagnetismo
- Termodinâmica
- Mecânica Quântica
- Relatividade

### 💻 Computação
- Algoritmos e Estruturas de Dados
- Programação
- Teoria da Computação
- Inteligência Artificial
- Engenharia de Software

### 🔧 Engenharia
- Sistemas de Controle
- Processamento de Sinais
- Circuitos Elétricos
- Mecânica dos Materiais
- Projeto de Sistemas

### 📊 Estatística
- Estatística Descritiva
- Estatística Inferencial
- Probabilidade
- Machine Learning
- Análise de Dados

## 🎯 Tipos de Tarefas

### 1. 💬 Responder Perguntas
Responde perguntas acadêmicas baseadas nos documentos disponíveis.

**Exemplo:**
```
Pergunta: "Como calcular a derivada de uma função composta?"
Resposta: Explicação detalhada da regra da cadeia com exemplos...
```

### 2. 📖 Explicar Conceitos
Explica conceitos acadêmicos de forma didática e progressiva.

**Exemplo:**
```
Conceito: "Integral definida"
Nível: "intermediário"
Explicação: Definição, interpretação geométrica, exemplos...
```

### 3. 🔧 Resolver Problemas
Resolve problemas específicos com metodologia detalhada.

**Exemplo:**
```
Problema: "Calcule ∫ x² dx de 0 a 2"
Solução: Passo a passo da resolução...
```

## 🔧 Uso do Sistema

### Interface Web (Streamlit)

1. **Inicie a aplicação:**
```bash
streamlit run app.py
```

2. **Acesse no browser:**
```
http://localhost:8501
```

3. **Use a interface:**
   - Selecione a disciplina
   - Escolha o tipo de tarefa
   - Digite sua pergunta/problema
   - Obtenha a resposta

### Uso Programático

```python
from main import run_academic_assistant

# Responder pergunta
resultado = run_academic_assistant(
    pergunta="O que é uma matriz inversa?",
    subject_id="matematica"
)

# Explicar conceito
from main import run_concept_explanation
explicacao = run_concept_explanation(
    conceito="Derivada",
    subject_id="matematica",
    nivel="básico"
)

# Resolver problema
from main import run_problem_solver
solucao = run_problem_solver(
    problema="Calcule a derivada de f(x) = x³ + 2x",
    subject_id="matematica",
    nivel_detalhe="detalhado"
)
```

## 📊 Sistema de Avaliação

O sistema inclui avaliação automática da qualidade das respostas baseada em:

- **Completude**: Verificação se a resposta é completa
- **Estrutura**: Organização e formatação do texto
- **Conteúdo Técnico**: Presença de termos técnicos adequados
- **Referências**: Citações e menções a fontes
- **Formatação**: Uso correto de LaTeX e apresentação

### Métricas de Qualidade

- **Excelente** (≥80%): Resposta completa e bem estruturada
- **Boa** (≥60%): Resposta adequada com pequenas melhorias
- **Regular** (≥40%): Resposta básica que necessita melhorias
- **Necessita Melhoria** (<40%): Resposta inadequada

## 📄 Gerenciamento de Documentos

### Adicionar Documentos

```python
from utils.subject_manager import SubjectManager

manager = SubjectManager()

# Adicionar documento individual
manager.add_document(
    file_path="caminho/para/documento.pdf",
    subject_id="matematica",
    description="Apostila de Cálculo I",
    tags=["calculo", "derivadas"]
)

# Adicionar múltiplos documentos
documents_info = [
    {
        "file_path": "doc1.pdf",
        "subject_id": "fisica",
        "description": "Mecânica Clássica",
        "tags": ["mecanica", "newton"]
    }
]
results = manager.bulk_add_documents(documents_info)
```

### Buscar Documentos

```python
# Buscar por texto
docs = manager.search_documents(
    query="cálculo",
    subject_id="matematica"
)

# Listar por disciplina
docs_matematica = manager.get_documents_by_subject("matematica")
```

## 🔧 Configuração Avançada

### Personalizar Disciplinas

Edite `knowledge/subjects_config.json`:

```json
{
  "nova_disciplina": {
    "name": "Nova Disciplina",
    "description": "Descrição da disciplina",
    "keywords": ["palavra1", "palavra2"],
    "documents": []
  }
}
```

### Personalizar Agentes

Edite `config/agents.yaml`:

```yaml
agente_nova_disciplina:
  role: >
    Especialista em Nova Disciplina
  goal: >
    Auxiliar estudantes com conceitos específicos...
  backstory: >
    Você é um expert com experiência...
```

### Personalizar Tarefas

Edite `config/task.yaml`:

```yaml
nova_tarefa:
  description: >
    Descrição da nova tarefa...
  expected_output: >
    Formato esperado da resposta...
  agent: agente_{area_codigo}
```

## 📈 Monitoramento e Logs

### Logs de Avaliação

```python
from utils.response_evaluator import ResponseEvaluator

evaluator = ResponseEvaluator()

# Ver estatísticas
stats = evaluator.get_statistics()
print(f"Média de confiança: {stats['average_confidence']}")

# Ver avaliações recentes
recent = evaluator.get_recent_evaluations(limit=10)
```

### Estatísticas de Documentos

```python
from utils.subject_manager import SubjectManager

manager = SubjectManager()
stats = manager.get_document_statistics()

print(f"Total de documentos: {stats['total_documents']}")
print(f"Por disciplina: {stats['by_subject']}")
```

## 🛠️ Desenvolvimento e Contribuição

### Estrutura de Classes Principais

1. **AcademicCrew**: Classe principal do CrewAI
2. **DocumentProcessor**: Processamento de documentos
3. **SubjectManager**: Gerenciamento de disciplinas
4. **ResponseEvaluator**: Avaliação de qualidade

### Adicionando Nova Disciplina

1. Criar configuração em `subjects_config.json`
2. Adicionar agente em `agents.yaml`
3. Configurar palavras-chave no `ResponseEvaluator`
4. Testar com documentos da disciplina

### Adicionando Novo Tipo de Tarefa

1. Definir tarefa em `task.yaml`
2. Criar função em `main.py`
3. Adicionar interface em `app.py`
4. Atualizar avaliador se necessário

## 🚨 Solução de Problemas

### Problemas Comuns

1. **Erro de conexão com LLM**
   - Verificar credenciais
   - Confirmar conectividade

2. **Documentos não carregados**
   - Verificar formato PDF
   - Confirmar caminho dos arquivos

3. **Respostas de baixa qualidade**
   - Verificar qualidade dos documentos
   - Ajustar configuração dos agentes

### Debug

```python
# Ativar modo verbose
crew_instance = AcademicCrew(subject_id="matematica")
crew = crew_instance.create_crew()
crew.verbose = True
```

## 📞 Suporte

Para suporte técnico ou dúvidas:
- Verificar logs em `logs/`
- Consultar documentação do CrewAI
- Revisar configurações dos agentes

## 📄 Licença

Este projeto está licenciado sob [MIT License](LICENSE).

---

**Desenvolvido com ❤️ usando CrewAI, Watsonx e Streamlit**
