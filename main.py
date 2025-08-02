from crew import AcademicCrew, ComplianceCrew
from utils.document_processor import DocumentProcessor
from typing import Dict, Any, Optional


def run_academic_assistant(pergunta: str, subject_id: str = "geral", task_type: str = "responder_pergunta_academica") -> str:
    """
    Executa assistente acadêmico para uma disciplina específica
    
    Args:
        pergunta: Pergunta do usuário
        subject_id: ID da disciplina (matematica, fisica, computacao, etc.)
        task_type: Tipo de tarefa a executar
    
    Returns:
        Resposta do assistente acadêmico
    """
    print(f"Instanciando AcademicCrew para {subject_id}...")
    crew_instance = AcademicCrew(subject_id)
    
    print("Preparando inputs...")
    
    # Obtém informações da disciplina de forma segura
    subject_info = crew_instance.doc_processor.get_subject_info(subject_id)
    area_conhecimento = "Geral"
    
    if subject_info and isinstance(subject_info, dict):
        area_conhecimento = subject_info.get("name", "Geral")
    elif subject_id != "geral":
        # Se não encontrou a disciplina, usa o próprio ID como fallback
        area_conhecimento = subject_id.title()
    
    inputs = {
        "pergunta": pergunta,
        "area_conhecimento": area_conhecimento,
        "area_codigo": subject_id
    }
    
    print("Rodando kickoff...")
    crew = crew_instance.create_crew(task_type, inputs)
    result = crew.kickoff(inputs=inputs)
    
    return str(result)


def run_concept_explanation(conceito: str, subject_id: str, nivel: str = "intermediario") -> str:
    """
    Executa explicação de conceito acadêmico
    
    Args:
        conceito: Conceito a ser explicado
        subject_id: ID da disciplina
        nivel: Nível de explicação (basico, intermediario, avancado)
    
    Returns:
        Explicação do conceito
    """
    print(f"Explicando conceito '{conceito}' para {subject_id}...")
    crew_instance = AcademicCrew(subject_id)
    
    # Obtém informações da disciplina de forma segura
    subject_info = crew_instance.doc_processor.get_subject_info(subject_id)
    area_conhecimento = subject_id.title() if subject_id != "geral" else "Geral"
    
    if subject_info and isinstance(subject_info, dict):
        area_conhecimento = subject_info.get("name", area_conhecimento)
    
    inputs = {
        "conceito": conceito,
        "nivel": nivel,
        "area_conhecimento": area_conhecimento,
        "area_codigo": subject_id
    }
    
    crew = crew_instance.create_crew("explicar_conceito_academico", inputs)
    result = crew.kickoff(inputs=inputs)
    
    return str(result)


def run_problem_solver(problema: str, subject_id: str, nivel_detalhe: str = "detalhado") -> str:
    """
    Executa resolução de problema acadêmico
    
    Args:
        problema: Problema a ser resolvido
        subject_id: ID da disciplina
        nivel_detalhe: Nível de detalhe (resumido, detalhado, muito_detalhado)
    
    Returns:
        Solução do problema
    """
    print(f"Resolvendo problema para {subject_id}...")
    crew_instance = AcademicCrew(subject_id)
    
    # Obtém informações da disciplina de forma segura
    subject_info = crew_instance.doc_processor.get_subject_info(subject_id)
    area_conhecimento = subject_id.title() if subject_id != "geral" else "Geral"
    
    if subject_info and isinstance(subject_info, dict):
        area_conhecimento = subject_info.get("name", area_conhecimento)
    
    inputs = {
        "problema": problema,
        "nivel_detalhe": nivel_detalhe,
        "area_conhecimento": area_conhecimento,
        "area_codigo": subject_id
    }
    
    crew = crew_instance.create_crew("resolver_problema_academico", inputs)
    result = crew.kickoff(inputs=inputs)
    
    return str(result)


def get_available_subjects() -> Dict[str, Dict]:
    """Retorna disciplinas disponíveis no sistema"""
    doc_processor = DocumentProcessor()
    return doc_processor.get_available_subjects()


def get_subject_documents_info() -> Dict[str, Any]:
    """Retorna informações sobre documentos por disciplina"""
    doc_processor = DocumentProcessor()
    documents_by_subject = doc_processor.scan_knowledge_directory()
    subjects_info = {}
    
    for subject_id, subject_info in doc_processor.get_available_subjects().items():
        docs_count = len(subject_info.get("documents", []))
        subjects_info[subject_id] = {
            "name": subject_info["name"],
            "description": subject_info["description"],
            "documents_count": docs_count,
            "has_documents": docs_count > 0
        }
    
    return subjects_info


# Mantém compatibilidade com código anterior
def run_compliance_assistant(pergunta: str):
    """Função de compatibilidade - redireciona para matemática"""
    return run_academic_assistant(pergunta, "matematica")