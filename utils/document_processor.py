import os
from pathlib import Path
from typing import List, Dict
from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource
import yaml


class DocumentProcessor:
    """
    Processa documentos para agentes de IA baseando-se em uma estrutura de pastas.

    A lógica foi desenvolvida para que cada subpasta dentro da base de conhecimento
    represente uma matéria acadêmica.
    """
    
    def __init__(self, knowledge_base_path: str = "knowledge"):
        """
        Inicializa o processador, definindo o caminho para a base de conhecimento.
        
        Args:
            knowledge_base_path: O caminho para a pasta principal que contém
                                 as subpastas de cada matéria.
        """
        self.knowledge_base_path = Path(knowledge_base_path)
        # Garante que o diretório principal de conhecimento exista
        self.knowledge_base_path.mkdir(exist_ok=True)
        
    def get_available_subjects(self) -> List[str]:
        """
        Escaneia a base de conhecimento e retorna uma lista com os nomes das matérias
        disponíveis (baseado nos nomes das subpastas).
        
        Returns:
            Uma lista de strings, onde cada string é o nome de uma matéria.
        """
        if not self.knowledge_base_path.exists():
            return []
        
        # Lista todas as entradas no diretório e filtra apenas as que são pastas
        subjects = [entry.name for entry in self.knowledge_base_path.iterdir() if entry.is_dir()]
        return subjects

    def get_subject_info(self, subject: str) -> Dict[str, str]:
        """
        Retorna metadados da disciplina (como nome legível, código, descrição).
        Procura por um arquivo de metadata dentro da pasta da matéria.
        Se não encontrar, devolve um fallback baseado no nome da pasta.
        """
        subject_path = self.knowledge_base_path / subject
        if not subject_path.is_dir():
            return {}

        # possíveis nomes de arquivo de metadata
        metadata_candidates = ["metadata.yaml", "subject.yaml", "info.yaml"]
        for fname in metadata_candidates:
            metadata_path = subject_path / fname
            if metadata_path.exists():
                try:
                    with open(metadata_path, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f) or {}
                        # garante pelo menos o nome formatado
                        if "name" not in data:
                            data["name"] = subject.replace("_", " ").title()
                        if "code" not in data:
                            data["code"] = subject
                        return data
                except Exception:
                    # se falhar no parse, ignora e vai para fallback
                    break

        # fallback simples
        return {
            "name": subject.replace("_", " ").title(),
            "code": subject
        }
    
    def get_knowledge_sources_for_subject(self, subject: str) -> List[PDFKnowledgeSource]:
        """
        Encontra todos os arquivos PDF dentro da pasta de uma matéria específica
        e os carrega em uma fonte de conhecimento para o CrewAI.
        
        Args:
            subject: O nome da matéria (que deve corresponder a uma subpasta).
        
        Returns:
            Uma lista contendo um objeto PDFKnowledgeSource com os documentos da matéria.
        """
        subject_path = self.knowledge_base_path / subject
        
        if not subject_path.is_dir():
            print(f"Aviso: A pasta da matéria '{subject}' não foi encontrada em '{self.knowledge_base_path}'.")
            return []

        # Encontra todos os arquivos PDF diretamente na pasta da matéria
        pdf_path_objects = list(subject_path.glob("*.pdf"))

        if not pdf_path_objects:
            print(f"Aviso: Nenhum arquivo PDF foi encontrado na pasta '{subject}'.")
            return []
        
        try:
            relative_paths = [str(p.relative_to(self.knowledge_base_path)) for p in pdf_path_objects]

            print(f"Carregando {len(relative_paths)} documento(s) da matéria '{subject}': {relative_paths}")

            knowledge_source = PDFKnowledgeSource(
                file_paths=relative_paths,
                knowledge_base_directory=str(self.knowledge_base_path)
            )
            return [knowledge_source]
        except Exception as e:
            print(f"Erro ao criar a fonte de conhecimento para a matéria '{subject}': {e}")
            return []
    
    def get_all_knowledge_sources(self) -> List[PDFKnowledgeSource]:
        """
        Cria uma fonte de conhecimento contendo TODOS os PDFs de TODAS as matérias.
        
        Returns:
            Uma lista contendo um único objeto PDFKnowledgeSource com todos os documentos.
        """
        # Usa rglob para buscar recursivamente em todas as subpastas
        all_pdf_path_objects = list(self.knowledge_base_path.rglob("*.pdf"))
        
        if not all_pdf_path_objects:
            print("Aviso: Nenhum arquivo PDF foi encontrado em nenhuma das pastas de matérias.")
            return []

        try:
            relative_paths = [str(p.relative_to(self.knowledge_base_path)) for p in all_pdf_path_objects]

            print(f"Carregando um total de {len(relative_paths)} documento(s) de todas as matérias.")
            
            knowledge_source = PDFKnowledgeSource(
                file_paths=relative_paths,
                knowledge_base_directory=str(self.knowledge_base_path)
            )
            return [knowledge_source]
        except Exception as e:
            print(f"Erro ao criar a fonte de conhecimento global: {e}")
            return []
