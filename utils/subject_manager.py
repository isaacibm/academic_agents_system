import os
import json
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import hashlib
import mimetypes
from utils.document_processor import DocumentProcessor


class SubjectManager:
    """Gerenciador avançado de matérias e documentos acadêmicos"""
    
    def __init__(self, knowledge_base_path: str = "knowledge"):
        self.knowledge_base_path = Path(knowledge_base_path)
        self.doc_processor = DocumentProcessor(knowledge_base_path)
        self.metadata_file = self.knowledge_base_path / "documents_metadata.json"
        self._load_metadata()
    
    def _load_metadata(self):
        """Carrega metadados dos documentos"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {
                "documents": {},
                "upload_history": [],
                "last_scan": None
            }
            self._save_metadata()
    
    def _save_metadata(self):
        """Salva metadados dos documentos"""
        self.knowledge_base_path.mkdir(exist_ok=True)
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calcula hash MD5 do arquivo"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def add_document(self, file_path: str, subject_id: str, description: str = "", 
                    tags: List[str] = None, move_file: bool = True) -> Dict:
        """
        Adiciona documento à base de conhecimento
        
        Args:
            file_path: Caminho do arquivo
            subject_id: ID da disciplina
            description: Descrição do documento
            tags: Tags para classificação
            move_file: Se deve mover o arquivo para o diretório da disciplina
        
        Returns:
            Informações do documento adicionado
        """
        source_path = Path(file_path)
        
        if not source_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        # Verifica se é um tipo de arquivo suportado
        if not self._is_supported_file(source_path):
            raise ValueError(f"Tipo de arquivo não suportado: {source_path.suffix}")
        
        # Cria diretório da disciplina se não existir
        subject_dir = self.knowledge_base_path / subject_id
        subject_dir.mkdir(exist_ok=True)
        
        # Define nome do arquivo no destino
        if move_file:
            target_path = subject_dir / source_path.name
            
            # Verifica se arquivo já existe
            counter = 1
            original_name = target_path.stem
            extension = target_path.suffix
            
            while target_path.exists():
                target_path = subject_dir / f"{original_name}_{counter}{extension}"
                counter += 1
            
            # Move ou copia arquivo
            if source_path.parent != target_path.parent:
                shutil.copy2(source_path, target_path)
            else:
                target_path = source_path
        else:
            target_path = source_path
        
        # Calcula hash e metadados
        file_hash = self._calculate_file_hash(target_path)
        file_stats = target_path.stat()
        
        # Cria entrada de metadados
        doc_id = f"{subject_id}_{target_path.stem}_{file_hash[:8]}"
        doc_metadata = {
            "id": doc_id,
            "filename": target_path.name,
            "path": str(target_path),
            "subject_id": subject_id,
            "description": description,
            "tags": tags or [],
            "file_hash": file_hash,
            "file_size": file_stats.st_size,
            "mime_type": mimetypes.guess_type(str(target_path))[0],
            "added_date": datetime.now().isoformat(),
            "modified_date": datetime.fromtimestamp(file_stats.st_mtime).isoformat()
        }
        
        # Adiciona aos metadados
        self.metadata["documents"][doc_id] = doc_metadata
        self.metadata["upload_history"].append({
            "doc_id": doc_id,
            "action": "added",
            "timestamp": datetime.now().isoformat(),
            "subject_id": subject_id
        })
        
        self._save_metadata()
        
        # Atualiza processador de documentos
        self.doc_processor.scan_knowledge_directory()
        
        return doc_metadata
    
    def remove_document(self, doc_id: str, delete_file: bool = True) -> bool:
        """
        Remove documento da base de conhecimento
        
        Args:
            doc_id: ID do documento
            delete_file: Se deve deletar o arquivo físico
        
        Returns:
            True se removido com sucesso
        """
        if doc_id not in self.metadata["documents"]:
            return False
        
        doc_metadata = self.metadata["documents"][doc_id]
        
        if delete_file:
            file_path = Path(doc_metadata["path"])
            if file_path.exists():
                file_path.unlink()
        
        # Remove dos metadados
        del self.metadata["documents"][doc_id]
        self.metadata["upload_history"].append({
            "doc_id": doc_id,
            "action": "removed",
            "timestamp": datetime.now().isoformat(),
            "subject_id": doc_metadata["subject_id"]
        })
        
        self._save_metadata()
        
        # Atualiza processador de documentos
        self.doc_processor.scan_knowledge_directory()
        
        return True
    
    def get_documents_by_subject(self, subject_id: str) -> List[Dict]:
        """Retorna documentos de uma disciplina específica"""
        return [
            doc for doc in self.metadata["documents"].values()
            if doc["subject_id"] == subject_id
        ]
    
    def get_all_documents(self) -> Dict[str, Dict]:
        """Retorna todos os documentos"""
        return self.metadata["documents"]
    
    def search_documents(self, query: str, subject_id: Optional[str] = None, 
                        tags: Optional[List[str]] = None) -> List[Dict]:
        """
        Busca documentos por texto, disciplina ou tags
        
        Args:
            query: Texto para buscar em nome/descrição
            subject_id: Filtrar por disciplina
            tags: Filtrar por tags
        
        Returns:
            Lista de documentos encontrados
        """
        results = []
        query_lower = query.lower() if query else ""
        
        for doc in self.metadata["documents"].values():
            # Filtro por disciplina
            if subject_id and doc["subject_id"] != subject_id:
                continue
            
            # Filtro por tags
            if tags and not any(tag in doc["tags"] for tag in tags):
                continue
            
            # Busca textual
            if query:
                searchable_text = f"{doc['filename']} {doc['description']} {' '.join(doc['tags'])}".lower()
                if query_lower not in searchable_text:
                    continue
            
            results.append(doc)
        
        return results
    
    def get_document_statistics(self) -> Dict:
        """Retorna estatísticas dos documentos"""
        stats = {
            "total_documents": len(self.metadata["documents"]),
            "by_subject": {},
            "by_type": {},
            "total_size": 0,
            "recent_uploads": 0
        }
        
        recent_threshold = datetime.now().timestamp() - (7 * 24 * 3600)  # 7 dias
        
        for doc in self.metadata["documents"].values():
            # Por disciplina
            subject = doc["subject_id"]
            if subject not in stats["by_subject"]:
                stats["by_subject"][subject] = 0
            stats["by_subject"][subject] += 1
            
            # Por tipo
            file_ext = Path(doc["filename"]).suffix.lower()
            if file_ext not in stats["by_type"]:
                stats["by_type"][file_ext] = 0
            stats["by_type"][file_ext] += 1
            
            # Tamanho total
            stats["total_size"] += doc["file_size"]
            
            # Uploads recentes
            upload_time = datetime.fromisoformat(doc["added_date"]).timestamp()
            if upload_time > recent_threshold:
                stats["recent_uploads"] += 1
        
        return stats
    
    def update_document_metadata(self, doc_id: str, description: str = None, 
                                tags: List[str] = None) -> bool:
        """Atualiza metadados de um documento"""
        if doc_id not in self.metadata["documents"]:
            return False
        
        doc = self.metadata["documents"][doc_id]
        
        if description is not None:
            doc["description"] = description
        
        if tags is not None:
            doc["tags"] = tags
        
        doc["last_updated"] = datetime.now().isoformat()
        
        self.metadata["upload_history"].append({
            "doc_id": doc_id,
            "action": "updated",
            "timestamp": datetime.now().isoformat(),
            "subject_id": doc["subject_id"]
        })
        
        self._save_metadata()
        return True
    
    def create_subject(self, subject_id: str, name: str, description: str, 
                      keywords: List[str] = None) -> bool:
        """Cria nova disciplina"""
        try:
            self.doc_processor.add_subject(subject_id, name, description, keywords or [])
            
            # Cria diretório para a disciplina
            subject_dir = self.knowledge_base_path / subject_id
            subject_dir.mkdir(exist_ok=True)
            
            return True
        except Exception:
            return False
    
    def get_upload_history(self, limit: int = 50) -> List[Dict]:
        """Retorna histórico de uploads"""
        return sorted(
            self.metadata["upload_history"],
            key=lambda x: x["timestamp"],
            reverse=True
        )[:limit]
    
    def _is_supported_file(self, file_path: Path) -> bool:
        """Verifica se o tipo de arquivo é suportado"""
        supported_extensions = {'.pdf', '.txt', '.md', '.docx', '.doc'}
        return file_path.suffix.lower() in supported_extensions
    
    def bulk_add_documents(self, documents_info: List[Dict]) -> List[Dict]:
        """
        Adiciona múltiplos documentos em lote
        
        Args:
            documents_info: Lista de dicts com 'file_path', 'subject_id', 'description', 'tags'
        
        Returns:
            Lista de resultados para cada documento
        """
        results = []
        
        for doc_info in documents_info:
            try:
                result = self.add_document(
                    file_path=doc_info["file_path"],
                    subject_id=doc_info["subject_id"],
                    description=doc_info.get("description", ""),
                    tags=doc_info.get("tags", []),
                    move_file=doc_info.get("move_file", True)
                )
                results.append({"success": True, "document": result})
            except Exception as e:
                results.append({"success": False, "error": str(e), "file_path": doc_info["file_path"]})
        
        return results
    
    def export_metadata(self, export_path: str) -> bool:
        """Exporta metadados para arquivo JSON"""
        try:
            export_data = {
                "export_date": datetime.now().isoformat(),
                "subjects": self.doc_processor.get_available_subjects(),
                "documents": self.metadata["documents"],
                "statistics": self.get_document_statistics()
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception:
            return False 