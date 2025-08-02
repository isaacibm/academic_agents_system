from crewai import Agent, Task, Process, Crew, LLM
from typing import Optional, Dict, Any
import os
import yaml
from utils.document_processor import DocumentProcessor
from utils.watson_llm import get_llm, get_embedder


class SafeDict(dict):
    def __missing__(self, key):
        return "{" + key + "}"

def safe_format(template: str, mapping: dict) -> str:
    return template.format_map(SafeDict(mapping))

class AcademicCrew:
    """Crew acadêmico universal para múltiplas disciplinas"""
    
    def __init__(self, subject_id: Optional[str] = None):
        self.subject_id = subject_id or "geral"
        self.doc_processor = DocumentProcessor()
        self.agents_config_path = "config/agents.yaml"
        self.tasks_config_path = "config/tasks.yaml"
        
        self.llm = get_llm()
        self._load_configs()
        
    def _load_configs(self):
        try:
            with open(self.agents_config_path, 'r', encoding='utf-8') as f:
                self.agents_config = yaml.safe_load(f) or {}
        except Exception:
            self.agents_config = {}
        try:
            with open(self.tasks_config_path, 'r', encoding='utf-8') as f:
                self.tasks_config = yaml.safe_load(f) or {}
        except Exception:
            self.tasks_config = {}
    
    def get_subject_agent_config(self) -> Dict[str, Any]:
        agent_key = f"agente_{self.subject_id}"
        return self.agents_config.get(agent_key, {})
    
    def create_subject_agent(self) -> Agent:
        agent_config = self.get_subject_agent_config()
        return Agent(
            config=agent_config,
            verbose=True,
            tools=[],
            llm=self.llm,
        )
    
    def get_task_config(self, task_key: str) -> Dict[str, Any]:
        task_config = self.tasks_config.get(task_key)
        if not task_config:
            raise KeyError(f"Tarefa '{task_key}' não encontrada em {self.tasks_config_path}. Chaves disponíveis: {list(self.tasks_config.keys())}")
        return task_config

    def create_academic_task(
        self,
        task_key: str,
        inputs: Dict[str, Any],
        agent: Optional[Agent] = None
    ) -> Task:
        task_config = self.get_task_config(task_key)
        enhanced_inputs = inputs.copy()

        subject_info = self.doc_processor.get_subject_info(self.subject_id)
        if subject_info and isinstance(subject_info, dict):
            enhanced_inputs.setdefault("area_conhecimento", subject_info.get("name", "Geral"))
            enhanced_inputs.setdefault("area_codigo", self.subject_id)

        description_template = task_config.get("description", "")
        try:
            description = safe_format(description_template, enhanced_inputs)
        except KeyError as e:
            missing = e.args[0]
            raise KeyError(f"Chave '{missing}' faltando para formatar a descrição da tarefa '{task_key}'. Inputs fornecidos: {list(enhanced_inputs.keys())}") from e

        expected_output_template = task_config.get("expected_output", "")
        try:
            expected_output = safe_format(expected_output_template, enhanced_inputs)
        except Exception:
            expected_output = expected_output_template

        task_obj = Task(
            description=description,
            expected_output=expected_output
        )
        if agent:
            task_obj.agent = agent
        return task_obj

    def create_crew(
        self,
        task_key: str = "elaborar_explicacao_tecnica",
        inputs: Optional[Dict[str, Any]] = None
    ) -> Crew:
        if inputs is None:
            inputs = {}

        if self.subject_id == "geral":
            knowledge_sources = self.doc_processor.get_all_knowledge_sources()
        else:
            knowledge_sources = self.doc_processor.get_knowledge_sources_for_subject(self.subject_id)

        agent = self.create_subject_agent()
        task_obj = self.create_academic_task(task_key, inputs, agent)

        return Crew(
            agents=[agent],
            tasks=[task_obj],
            process=Process.sequential,
            verbose=True,
            knowledge_sources=knowledge_sources,
            embedder=get_embedder()
        )

    def run(self, question: str, task_key: str = "elaborar_explicacao_tecnica") -> str:
        """
        Conveniência: monta os inputs a partir da pergunta, cria o crew e dispara o kickoff.
        """
        inputs = {
            "enunciado": question,
            "topico": question
        }
        crew = self.create_crew(task_key, inputs)
        result = crew.kickoff(inputs=inputs)
        return str(result)
    
    def get_available_subjects(self) -> Dict[str, Dict]:
        return self.doc_processor.get_available_subjects()

    def list_available_tasks(self) -> list[str]:
        return list(self.tasks_config.keys())
