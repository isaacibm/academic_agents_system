import logging
import os
import time
from typing import Optional

from crew import AcademicCrew


def setup_logger() -> logging.Logger:
    """
    Configura o logger com formatação que inclui subject e task_key.
    Variáveis de ambiente opcionais:
      - ACADEMIC_ASSISTANT_LOG_LEVEL (default: INFO)
      - ACADEMIC_ASSISTANT_LOG_FILE (se quiser persistir em arquivo)
    """
    log_level_str = os.getenv("ACADEMIC_ASSISTANT_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, log_level_str, logging.INFO)

    logger = logging.getLogger("academic_assistant")
    if logger.handlers:
        logger.setLevel(level)
        return logger

    # Formatter que espera os campos extra subject e task_key
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] [subject=%(subject)s] [task_key=%(task_key)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Handler para console
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Handler opcional para arquivo
    log_file = os.getenv("ACADEMIC_ASSISTANT_LOG_FILE")
    if log_file:
        fh = logging.FileHandler(log_file)
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    logger.propagate = False
    logger.setLevel(level)

    # Também encaminha logs internos do CrewAI para o mesmo destino (se quiser)
    crewai_logger = logging.getLogger("crewai")
    crewai_logger.setLevel(level)
    for h in logger.handlers:
        crewai_logger.addHandler(h)

    return logger


class ContextFilter(logging.Filter):
    """
    Garante que todo LogRecord tenha os atributos subject e task_key,
    usando valores padrão quando não fornecidos explícitamente.
    """
    def __init__(self):
        super().__init__()
        self.subject = "unknown"
        self.task_key = "none"

    def filter(self, record: logging.LogRecord) -> bool:
        record.subject = getattr(record, "subject", self.subject)
        record.task_key = getattr(record, "task_key", self.task_key)
        return True


# Instancia logger e adiciona filtro global para contexto
logger = setup_logger()
context_filter = ContextFilter()
logger.addFilter(context_filter)


def run_academic_assistant(
    question: str,
    subject_id: str,
    task_key: str = "elaborar_explicacao_tecnica"
) -> str:
    """
    Wrapper de orquestração: cria o AcademicCrew, dispara o kickoff e faz logging detalhado.
    """
    # injeta contexto
    context_filter.subject = subject_id
    context_filter.task_key = task_key

    logger.info("Iniciando run_academic_assistant", extra={"subject": subject_id, "task_key": task_key})
    start_ts = time.perf_counter()

    try:
        crew_instance = AcademicCrew(subject_id=subject_id)

        # log de informações da disciplina
        try:
            subject_info = crew_instance.doc_processor.get_subject_info(subject_id)
            logger.debug(f"Informações da disciplina carregadas: {subject_info}", extra={"subject": subject_id, "task_key": task_key})
        except Exception as e:
            logger.warning(f"Falha ao obter subject_info: {e}", extra={"subject": subject_id, "task_key": task_key})

        # Executa via wrapper .run (que faz create_crew + kickoff)
        result = crew_instance.run(question, task_key=task_key)

        duration = time.perf_counter() - start_ts
        logger.info(f"Kickoff concluído em {duration:.2f}s", extra={"subject": subject_id, "task_key": task_key})
        logger.debug(f"Resultado bruto: {result}", extra={"subject": subject_id, "task_key": task_key})

        return str(result)

    except Exception as err:
        duration = time.perf_counter() - start_ts
        logger.exception(f"Erro durante run_academic_assistant após {duration:.2f}s: {err}", extra={"subject": subject_id, "task_key": task_key})
        return f"Erro interno ao processar a pergunta: {err}"
