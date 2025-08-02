from crewai import Agent, Task, Process, Crew, LLM
from crewai.project import CrewBase, agent, crew, task
from utils.document_processor import DocumentProcessor
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv  

load_dotenv()

class AcademicCrew:
    """Crew acadêmico universal para múltiplas disciplinas"""
    
    def __init__(self, subject_id: Optional[str] = None):
        self.subject_id = subject_id or "geral"
        self.doc_processor = DocumentProcessor()
        self.agents_config_path = "config/agents.yaml"
        self.tasks_config_path = "config/task.yaml"
        
        # Configuração do modelo LLM
        model_id = os.getenv("MODEL_ID", "watsonx/meta-llama/llama-3-1-70b-instruct")
        
        # Configuração explícita para WatsonX
        llm_config = {
            "model": model_id,
            "temperature": 0,
            "api_key": os.getenv("WATSONX_APIKEY"),
            "project_id": os.getenv("WX_PROJECT_ID"),
            "api_base": os.getenv("WATSONX_API_BASE")
        }
        
        self.llm = LLM(**llm_config)
        
        # Carrega configurações
        self._load_configs()
        
    def _load_configs(self):
        """Carrega configurações de agentes e tarefas"""
        import yaml
        
        with open(self.agents_config_path, 'r', encoding='utf-8') as f:
            self.agents_config = yaml.safe_load(f)
            
        with open(self.tasks_config_path, 'r', encoding='utf-8') as f:
            self.tasks_config = yaml.safe_load(f)
    
    def get_subject_agent_config(self) -> Dict[str, Any]:
        """Retorna configuração do agente para a disciplina"""
        agent_key = f"agente_{self.subject_id}"
        return self.agents_config.get(agent_key, self.agents_config.get("agente_geral"))
    
    def create_subject_agent(self) -> Agent:
        """Cria agente especializado para a disciplina"""
        agent_config = self.get_subject_agent_config()
        
        return Agent(
            config=agent_config,
            verbose=True,
            tools=[],
            llm=self.llm,
        )
    
    def create_academic_task(self, task_type: str, inputs: Dict[str, Any], agent=None) -> Task:
        """Cria tarefa acadêmica baseada no tipo"""
        task_config = self.tasks_config.get(task_type, self.tasks_config.get("responder_pergunta_academica"))
        
        # Prepara inputs com informações da disciplina
        enhanced_inputs = inputs.copy()
        
        subject_info = self.doc_processor.get_subject_info(self.subject_id)
        
        if subject_info and isinstance(subject_info, dict):
            enhanced_inputs.update({
                "area_conhecimento": subject_info.get("name", "Geral"),
                "area_codigo": self.subject_id
            })
        
        # Formatar a descrição com os inputs
        description = task_config.get("description", "").format(**enhanced_inputs)
        expected_output = task_config.get("expected_output", "")
        
        # Cria Task COM agente atribuído
        task = Task(
            description=description,
            expected_output=expected_output
        )
        
        # Atribui o agente à task se fornecido
        if agent:
            task.agent = agent
        
        return task
    
    def create_crew(self, task_type: str = "responder_pergunta_academica", inputs: Dict[str, Any] = None) -> Crew:
        """Cria crew completo para a disciplina"""
        if inputs is None:
            inputs = {}
            
        # Obtém fontes de conhecimento para a disciplina
        if self.subject_id == "geral":
            knowledge_sources = self.doc_processor.get_all_knowledge_sources()
        else:
            knowledge_sources = self.doc_processor.get_knowledge_sources_for_subject(self.subject_id)
        
        # Cria agente e tarefa
        agent = self.create_subject_agent()
        task = self.create_academic_task(task_type, inputs, agent)
        
        return Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True,
            knowledge_sources=knowledge_sources
        )
    
    def get_available_subjects(self) -> Dict[str, Dict]:
        """Retorna disciplinas disponíveis"""
        return self.doc_processor.get_available_subjects()


# Manter compatibilidade com código anterior
@CrewBase  
class ComplianceCrew:
    """Classe de compatibilidade - mantém interface anterior"""
    agents_config = "config/agents.yaml"
    tasks_config = "config/task.yaml"

    def __init__(self):
        self.academic_crew = AcademicCrew("matematica")  # Default para matemática

    @agent
    def especialista_compliance(self) -> Agent:
        """Mantém compatibilidade - retorna agente de matemática"""
        return self.academic_crew.create_subject_agent()
      
    @task
    def responder_pergunta_compliance(self) -> Task:
        """Mantém compatibilidade - cria tarefa de resposta"""
        return self.academic_crew.create_academic_task(
            "responder_pergunta_academica", 
            {"pergunta": "", "area_conhecimento": "Matemática", "area_codigo": "matematica"}
        )

    @crew
    def crew(self) -> Crew:
        """Mantém compatibilidade - cria crew de matemática"""
        return self.academic_crew.create_crew()