import re
import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from pathlib import Path


class ResponseEvaluator:
    """Sistema de avaliação de qualidade e confiança das respostas acadêmicas"""
    
    def __init__(self):
        self.evaluation_history_file = Path("logs/evaluation_history.json")
        self.evaluation_history_file.parent.mkdir(exist_ok=True)
        self._load_history()
    
    def _load_history(self):
        """Carrega histórico de avaliações"""
        if self.evaluation_history_file.exists():
            with open(self.evaluation_history_file, 'r', encoding='utf-8') as f:
                self.history = json.load(f)
        else:
            self.history = {"evaluations": [], "statistics": {}}
            self._save_history()
    
    def _save_history(self):
        """Salva histórico de avaliações"""
        with open(self.evaluation_history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)
    
    def evaluate_response(self, question: str, response: str, subject_id: str, 
                         task_type: str) -> Dict[str, any]:
        """
        Avalia a qualidade de uma resposta acadêmica
        
        Args:
            question: Pergunta original
            response: Resposta gerada
            subject_id: ID da disciplina
            task_type: Tipo de tarefa
        
        Returns:
            Dicionário com métricas de avaliação
        """
        evaluation = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "response": response,
            "subject_id": subject_id,
            "task_type": task_type,
            "metrics": {}
        }
        
        # Análise de completude
        evaluation["metrics"]["completeness"] = self._evaluate_completeness(response)
        
        # Análise de estrutura
        evaluation["metrics"]["structure"] = self._evaluate_structure(response)
        
        # Análise de conteúdo técnico
        evaluation["metrics"]["technical_content"] = self._evaluate_technical_content(
            response, subject_id
        )
        
        # Análise de referências e citações
        evaluation["metrics"]["references"] = self._evaluate_references(response)
        
        # Análise de formatação
        evaluation["metrics"]["formatting"] = self._evaluate_formatting(response, subject_id)
        
        # Cálculo de confiança geral
        evaluation["confidence_score"] = self._calculate_confidence_score(evaluation["metrics"])
        
        # Classificação de qualidade
        evaluation["quality_rating"] = self._classify_quality(evaluation["confidence_score"])
        
        # Sugestões de melhoria
        evaluation["suggestions"] = self._generate_suggestions(evaluation["metrics"])
        
        # Salva no histórico
        self.history["evaluations"].append(evaluation)
        self._update_statistics()
        self._save_history()
        
        return evaluation
    
    def _evaluate_completeness(self, response: str) -> Dict[str, any]:
        """Avalia completude da resposta"""
        metrics = {
            "length": len(response),
            "word_count": len(response.split()),
            "has_introduction": False,
            "has_development": False,
            "has_conclusion": False,
            "score": 0.0
        }
        
        # Verifica estrutura básica
        paragraphs = response.split('\n\n')
        metrics["paragraph_count"] = len([p for p in paragraphs if p.strip()])
        
        # Verifica introdução (primeiros 20% do texto)
        intro_threshold = len(response) * 0.2
        intro_text = response[:int(intro_threshold)].lower()
        intro_keywords = ['introdução', 'conceito', 'definição', 'vamos', 'primeiro']
        metrics["has_introduction"] = any(keyword in intro_text for keyword in intro_keywords)
        
        # Verifica desenvolvimento (texto tem exemplos, explicações)
        dev_keywords = ['exemplo', 'por exemplo', 'considere', 'demonstração', 'prova', 'método']
        metrics["has_development"] = any(keyword in response.lower() for keyword in dev_keywords)
        
        # Verifica conclusão
        conclusion_keywords = ['conclusão', 'resumo', 'portanto', 'assim', 'finalmente', 'em suma']
        metrics["has_conclusion"] = any(keyword in response.lower() for keyword in conclusion_keywords)
        
        # Calcula score
        score = 0.0
        if metrics["word_count"] >= 50: score += 0.2
        if metrics["word_count"] >= 150: score += 0.2
        if metrics["has_introduction"]: score += 0.2
        if metrics["has_development"]: score += 0.2
        if metrics["has_conclusion"]: score += 0.2
        
        metrics["score"] = min(score, 1.0)
        return metrics
    
    def _evaluate_structure(self, response: str) -> Dict[str, any]:
        """Avalia estrutura e organização da resposta"""
        metrics = {
            "has_headings": False,
            "has_lists": False,
            "has_numbered_steps": False,
            "paragraph_organization": 0.0,
            "score": 0.0
        }
        
        # Verifica cabeçalhos
        heading_patterns = [r'^#+\s', r'^\*\*.*\*\*$', r'^###?\s']
        metrics["has_headings"] = any(
            re.search(pattern, response, re.MULTILINE) for pattern in heading_patterns
        )
        
        # Verifica listas
        list_patterns = [r'^\s*[-*+]\s', r'^\s*\d+\.\s']
        metrics["has_lists"] = any(
            re.search(pattern, response, re.MULTILINE) for pattern in list_patterns
        )
        
        # Verifica passos numerados
        step_pattern = r'^\s*\d+[\.)]\s'
        metrics["has_numbered_steps"] = bool(re.search(step_pattern, response, re.MULTILINE))
        
        # Avalia organização de parágrafos
        paragraphs = [p.strip() for p in response.split('\n\n') if p.strip()]
        if paragraphs:
            avg_length = sum(len(p) for p in paragraphs) / len(paragraphs)
            if 100 <= avg_length <= 500:  # Tamanho ideal de parágrafo
                metrics["paragraph_organization"] = 1.0
            elif avg_length < 50:
                metrics["paragraph_organization"] = 0.3
            else:
                metrics["paragraph_organization"] = 0.7
        
        # Calcula score
        score = 0.0
        if metrics["has_headings"]: score += 0.3
        if metrics["has_lists"]: score += 0.2
        if metrics["has_numbered_steps"]: score += 0.2
        score += metrics["paragraph_organization"] * 0.3
        
        metrics["score"] = min(score, 1.0)
        return metrics
    
    def _evaluate_technical_content(self, response: str, subject_id: str) -> Dict[str, any]:
        """Avalia conteúdo técnico específico da disciplina"""
        metrics = {
            "has_formulas": False,
            "has_definitions": False,
            "has_examples": False,
            "technical_depth": 0.0,
            "score": 0.0
        }
        
        # Verifica fórmulas (LaTeX ou matemática)
        formula_patterns = [r'\$.*\$', r'\\[a-zA-Z]+', r'[∑∫∂∆λμπσ]', r'\^[0-9]', r'_[0-9]']
        metrics["has_formulas"] = any(
            re.search(pattern, response) for pattern in formula_patterns
        )
        
        # Verifica definições
        def_keywords = ['define', 'definição', 'conceito', 'é definido como', 'significa']
        metrics["has_definitions"] = any(keyword in response.lower() for keyword in def_keywords)
        
        # Verifica exemplos
        example_keywords = ['exemplo', 'por exemplo', 'considere', 'suponha', 'caso']
        metrics["has_examples"] = any(keyword in response.lower() for keyword in example_keywords)
        
        # Avalia profundidade técnica baseada na disciplina
        subject_keywords = self._get_subject_keywords(subject_id)
        technical_terms_found = sum(1 for keyword in subject_keywords if keyword in response.lower())
        if subject_keywords:
            metrics["technical_depth"] = min(technical_terms_found / len(subject_keywords), 1.0)
        
        # Calcula score
        score = 0.0
        if subject_id in ['matematica', 'fisica'] and metrics["has_formulas"]: score += 0.4
        elif subject_id not in ['matematica', 'fisica']: score += 0.2  # Menos peso para outras disciplinas
        if metrics["has_definitions"]: score += 0.3
        if metrics["has_examples"]: score += 0.3
        score += metrics["technical_depth"] * 0.2
        
        metrics["score"] = min(score, 1.0)
        return metrics
    
    def _evaluate_references(self, response: str) -> Dict[str, any]:
        """Avalia presença de referências e citações"""
        metrics = {
            "has_citations": False,
            "mentions_sources": False,
            "citation_quality": 0.0,
            "score": 0.0
        }
        
        # Verifica citações
        citation_patterns = [r'\[.*\]', r'\(.*\)', r'segundo.*', r'de acordo com']
        metrics["has_citations"] = any(
            re.search(pattern, response, re.IGNORECASE) for pattern in citation_patterns
        )
        
        # Verifica menção a fontes
        source_keywords = ['documento', 'material', 'apostila', 'livro', 'fonte', 'referência']
        metrics["mentions_sources"] = any(keyword in response.lower() for keyword in source_keywords)
        
        # Avalia qualidade das citações
        if metrics["has_citations"] and metrics["mentions_sources"]:
            metrics["citation_quality"] = 1.0
        elif metrics["has_citations"] or metrics["mentions_sources"]:
            metrics["citation_quality"] = 0.5
        
        # Calcula score
        score = 0.0
        if metrics["has_citations"]: score += 0.4
        if metrics["mentions_sources"]: score += 0.3
        score += metrics["citation_quality"] * 0.3
        
        metrics["score"] = min(score, 1.0)
        return metrics
    
    def _evaluate_formatting(self, response: str, subject_id: str) -> Dict[str, any]:
        """Avalia formatação e apresentação"""
        metrics = {
            "proper_latex": False,
            "good_spacing": False,
            "clear_presentation": False,
            "score": 0.0
        }
        
        # Verifica LaTeX para disciplinas matemáticas
        if subject_id in ['matematica', 'fisica', 'estatistica']:
            latex_patterns = [r'\$[^$]+\$', r'\\[a-zA-Z]+\{[^}]*\}']
            metrics["proper_latex"] = any(
                re.search(pattern, response) for pattern in latex_patterns
            )
        else:
            metrics["proper_latex"] = True  # Não aplicável
        
        # Verifica espaçamento
        lines = response.split('\n')
        empty_lines = sum(1 for line in lines if not line.strip())
        total_lines = len(lines)
        if total_lines > 0:
            empty_ratio = empty_lines / total_lines
            metrics["good_spacing"] = 0.05 <= empty_ratio <= 0.3
        
        # Verifica apresentação clara
        metrics["clear_presentation"] = (
            not re.search(r'[.]{3,}', response) and  # Sem muitas reticências
            not re.search(r'[!]{2,}', response) and  # Sem muitas exclamações
            len(re.findall(r'[A-Z]{3,}', response)) < 3  # Sem muito texto em maiúsculas
        )
        
        # Calcula score
        score = 0.0
        if metrics["proper_latex"]: score += 0.4
        if metrics["good_spacing"]: score += 0.3
        if metrics["clear_presentation"]: score += 0.3
        
        metrics["score"] = min(score, 1.0)
        return metrics
    
    def _calculate_confidence_score(self, metrics: Dict) -> float:
        """Calcula score de confiança geral"""
        weights = {
            "completeness": 0.25,
            "structure": 0.20,
            "technical_content": 0.30,
            "references": 0.15,
            "formatting": 0.10
        }
        
        total_score = sum(
            metrics[metric]["score"] * weight 
            for metric, weight in weights.items()
        )
        
        return round(total_score, 3)
    
    def _classify_quality(self, confidence_score: float) -> str:
        """Classifica qualidade baseada no score"""
        if confidence_score >= 0.8:
            return "Excelente"
        elif confidence_score >= 0.6:
            return "Boa"
        elif confidence_score >= 0.4:
            return "Regular"
        else:
            return "Necessita Melhoria"
    
    def _generate_suggestions(self, metrics: Dict) -> List[str]:
        """Gera sugestões de melhoria"""
        suggestions = []
        
        if metrics["completeness"]["score"] < 0.6:
            suggestions.append("Resposta pode ser mais completa com mais detalhes")
        
        if metrics["structure"]["score"] < 0.6:
            suggestions.append("Melhore a organização com cabeçalhos e listas")
        
        if metrics["technical_content"]["score"] < 0.6:
            suggestions.append("Inclua mais conteúdo técnico específico da disciplina")
        
        if metrics["references"]["score"] < 0.6:
            suggestions.append("Adicione mais referências aos materiais consultados")
        
        if metrics["formatting"]["score"] < 0.6:
            suggestions.append("Melhore a formatação e apresentação do texto")
        
        return suggestions
    
    def _get_subject_keywords(self, subject_id: str) -> List[str]:
        """Retorna palavras-chave técnicas para cada disciplina"""
        keywords = {
            "matematica": ["derivada", "integral", "limite", "função", "matriz", "determinante", 
                          "vetor", "equação", "teorema", "demonstração"],
            "fisica": ["força", "energia", "momento", "campo", "onda", "partícula", 
                      "velocidade", "aceleração", "massa", "temperatura"],
            "computacao": ["algoritmo", "complexidade", "estrutura", "dados", "função", 
                          "classe", "objeto", "recursão", "iteração"],
            "engenharia": ["sistema", "controle", "projeto", "análise", "design", 
                          "processo", "otimização", "modelo"],
            "estatistica": ["probabilidade", "distribuição", "amostra", "hipótese", 
                           "correlação", "regressão", "variância", "média"]
        }
        return keywords.get(subject_id, [])
    
    def _update_statistics(self):
        """Atualiza estatísticas do histórico"""
        if not self.history["evaluations"]:
            return
        
        recent_evals = self.history["evaluations"][-100:]  # Últimas 100 avaliações
        
        self.history["statistics"] = {
            "total_evaluations": len(self.history["evaluations"]),
            "average_confidence": sum(e["confidence_score"] for e in recent_evals) / len(recent_evals),
            "quality_distribution": {},
            "by_subject": {},
            "by_task_type": {}
        }
        
        # Distribuição de qualidade
        for eval_data in recent_evals:
            quality = eval_data["quality_rating"]
            if quality not in self.history["statistics"]["quality_distribution"]:
                self.history["statistics"]["quality_distribution"][quality] = 0
            self.history["statistics"]["quality_distribution"][quality] += 1
        
        # Por disciplina
        for eval_data in recent_evals:
            subject = eval_data["subject_id"]
            if subject not in self.history["statistics"]["by_subject"]:
                self.history["statistics"]["by_subject"][subject] = {"count": 0, "avg_score": 0}
            self.history["statistics"]["by_subject"][subject]["count"] += 1
        
        # Calcula médias por disciplina
        for subject, data in self.history["statistics"]["by_subject"].items():
            subject_evals = [e for e in recent_evals if e["subject_id"] == subject]
            if subject_evals:
                data["avg_score"] = sum(e["confidence_score"] for e in subject_evals) / len(subject_evals)
    
    def get_statistics(self) -> Dict:
        """Retorna estatísticas de avaliação"""
        return self.history.get("statistics", {})
    
    def get_recent_evaluations(self, limit: int = 20) -> List[Dict]:
        """Retorna avaliações recentes"""
        return self.history["evaluations"][-limit:] 