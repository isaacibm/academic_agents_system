import os
import json
from pathlib import Path
from typing import List, Dict, Optional
from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource


class DocumentProcessor:
    """Classe para processamento de documentos acadêmicos de múltiplos formatos"""
    
    def __init__(self, knowledge_base_path: str = "knowledge"):
        self.knowledge_base_path = Path(knowledge_base_path)
        self.subjects_config_path = self.knowledge_base_path / "subjects_config.json"
        self._load_subjects_config()
    
    def _load_subjects_config(self):
        """Carrega configuração de matérias ou cria uma padrão"""
        if self.subjects_config_path.exists():
            with open(self.subjects_config_path, 'r', encoding='utf-8') as f:
                self.subjects_config = json.load(f)
        else:
            self.subjects_config = {
                "matematica": {
                    "name": "Matemática",
                    "description": "Cálculo, Álgebra Linear, Geometria, Análise",
                    "keywords": ["calculo", "algebra", "linear", "geometria", "derivada", "integral", "matriz"],
                    "documents": []
                },
                "fisica": {
                    "name": "Física",
                    "description": "Física Geral, Mecânica, Eletromagnetismo, Termodinâmica",
                    "keywords": ["fisica", "mecanica", "eletromagnetismo", "termodinamica", "optica"],
                    "documents": []
                },
                "computacao": {
                    "name": "Ciência da Computação",
                    "description": "Algoritmos, Estruturas de Dados, Programação",
                    "keywords": ["algoritmo", "programacao", "estrutura", "dados", "software"],
                    "documents": []
                },
                "engenharia": {
                    "name": "Engenharia",
                    "description": "Engenharia em geral, Sistemas, Controle",
                    "keywords": ["engenharia", "sistema", "controle", "projeto", "design"],
                    "documents": []
                },
                "estatistica": {
                    "name": "Estatística",
                    "description": "Estatística Descritiva, Inferencial, Probabilidade",
                    "keywords": ["estatistica", "probabilidade", "amostra", "hipotese", "regressao"],
                    "documents": []
                }
            }
            self._save_subjects_config()
    
    def _save_subjects_config(self):
        """Salva configuração de matérias"""
        self.knowledge_base_path.mkdir(exist_ok=True)
        with open(self.subjects_config_path, 'w', encoding='utf-8') as f:
            json.dump(self.subjects_config, f, indent=2, ensure_ascii=False)
    
    def get_available_subjects(self) -> Dict[str, Dict]:
        """Retorna lista de matérias disponíveis"""
        return self.subjects_config
    
    def categorize_document_by_filename(self, filename: str) -> Optional[str]:
        """Categoriza documento baseado no nome do arquivo"""
        filename_lower = filename.lower()
        
        for subject_id, subject_info in self.subjects_config.items():
            for keyword in subject_info["keywords"]:
                if keyword in filename_lower:
                    return subject_id
        
        return "geral"  # categoria padrão
    
    def scan_knowledge_directory(self) -> Dict[str, List[str]]:
        """Escaneia diretório de conhecimento e organiza documentos por matéria"""
        documents_by_subject = {}
        
        if not self.knowledge_base_path.exists():
            return documents_by_subject
        
        # Busca por arquivos PDF no diretório knowledge
        for file_path in self.knowledge_base_path.glob("**/*.pdf"):
            if file_path.is_file():
                subject = self.categorize_document_by_filename(file_path.name)
                
                if subject not in documents_by_subject:
                    documents_by_subject[subject] = []
                
                # Armazena caminho relativo ao knowledge_base_path
                relative_path = file_path.relative_to(self.knowledge_base_path)
                documents_by_subject[subject].append(str(relative_path))
        
        # Atualiza configuração com documentos encontrados
        for subject_id in self.subjects_config:
            if subject_id in documents_by_subject:
                self.subjects_config[subject_id]["documents"] = documents_by_subject[subject_id]
            else:
                self.subjects_config[subject_id]["documents"] = []
        
        # Adiciona categoria geral se houver documentos não categorizados
        if "geral" in documents_by_subject:
            if "geral" not in self.subjects_config:
                self.subjects_config["geral"] = {
                    "name": "Geral",
                    "description": "Documentos não categorizados",
                    "keywords": [],
                    "documents": documents_by_subject["geral"]
                }
        
        self._save_subjects_config()
        return documents_by_subject
    
    def get_knowledge_sources_for_subject(self, subject_id: str) -> List:
        """Retorna fontes de conhecimento para uma matéria específica"""
        self.scan_knowledge_directory()
        
        if subject_id not in self.subjects_config:
            return []
        
        documents = self.subjects_config[subject_id]["documents"]
        
        if not documents:
            return []
        
        try:
            # Converte para caminhos absolutos dentro do diretório knowledge
            full_paths = []
            for doc_path in documents:
                # Se o caminho já é absoluto, usa diretamente
                if Path(doc_path).is_absolute():
                    full_path = Path(doc_path)
                else:
                    # Se é relativo, combina com knowledge_base_path
                    full_path = self.knowledge_base_path / doc_path
                
                if full_path.exists():
                    full_paths.append(str(full_path))
                else:
                    print(f"Aviso: Documento não encontrado: {full_path}")
            
            if not full_paths:
                print(f"Nenhum documento válido encontrado para {subject_id}")
                return []
            
            # Para o PDFKnowledgeSource, precisa ser apenas o caminho relativo do arquivo
            # sem o "knowledge/" no início, pois ele adiciona automaticamente
            relative_paths = []
            for full_path in full_paths:
                # Remove "knowledge/" do início se estiver presente
                relative_path = full_path.replace("knowledge/", "") if full_path.startswith("knowledge/") else full_path
                relative_paths.append(relative_path)
            
            # Cria fonte de conhecimento PDF para os documentos da matéria
            pdf_source = PDFKnowledgeSource(file_paths=relative_paths)  # Usando file_paths em vez de file_path
            return [pdf_source]
        except Exception as e:
            print(f"Erro ao criar fonte de conhecimento para {subject_id}: {e}")
            return []
    
    def get_all_knowledge_sources(self) -> List:
        """Retorna todas as fontes de conhecimento disponíveis"""
        all_documents = []
        self.scan_knowledge_directory()
        
        for subject_info in self.subjects_config.values():
            all_documents.extend(subject_info.get("documents", []))
        
        if not all_documents:
            return []
        
        try:
            # Converte para caminhos absolutos e valida existência
            valid_documents = []
            for doc_path in all_documents:
                # Se o caminho já é absoluto, usa diretamente
                if Path(doc_path).is_absolute():
                    full_path = Path(doc_path)
                else:
                    # Se é relativo, combina com knowledge_base_path
                    full_path = self.knowledge_base_path / doc_path
                
                if full_path.exists():
                    valid_documents.append(str(full_path))
                else:
                    print(f"Aviso: Documento não encontrado: {full_path}")
            
            if not valid_documents:
                print("Nenhum documento válido encontrado")
                return []
            
            # Para o PDFKnowledgeSource, precisa ser apenas o caminho relativo do arquivo
            # sem o "knowledge/" no início, pois ele adiciona automaticamente
            relative_paths = []
            for full_path in valid_documents:
                # Remove "knowledge/" do início se estiver presente
                relative_path = full_path.replace("knowledge/", "") if full_path.startswith("knowledge/") else full_path
                relative_paths.append(relative_path)
                
            pdf_source = PDFKnowledgeSource(file_paths=relative_paths)  # Usando file_paths
            return [pdf_source]
        except Exception as e:
            print(f"Erro ao criar fontes de conhecimento: {e}")
            return []
    
    def add_subject(self, subject_id: str, name: str, description: str, keywords: List[str]):
        """Adiciona nova matéria"""
        self.subjects_config[subject_id] = {
            "name": name,
            "description": description,
            "keywords": keywords,
            "documents": []
        }
        self._save_subjects_config()
    
    def get_subject_info(self, subject_id: str) -> Optional[Dict]:
        """Retorna informações de uma matéria específica"""
        return self.subjects_config.get(subject_id) 