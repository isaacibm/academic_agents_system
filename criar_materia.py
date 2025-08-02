#!/usr/bin/env python3
import os
import sys
import unicodedata
import re
import yaml
from pathlib import Path
import argparse

KNOWLEDGE_ROOT = Path("knowledge")


def slugify(text: str) -> str:
    """
    Normaliza o nome da matéria para gerar o código:
    remove acentos, converte para lowercase, substitui não alfanuméricos por underscore.
    """
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_{2,}", "_", text).strip("_")
    if not text:
        raise ValueError("Nome da matéria gerou um código vazio após normalização.")
    return text


def main():
    parser = argparse.ArgumentParser(
        description="Cria/atualiza metadata.yaml básico de uma matéria com apenas name, code e description."
    )
    parser.add_argument(
        "subject",
        nargs="*",
        help="Nome da matéria (ex: 'Cálculo Avançado'). Se omitido, será perguntado interativamente."
    )
    parser.add_argument(
        "--display-name",
        "-n",
        help="Nome legível da matéria. Se omitido, usa o nome fornecido."
    )
    parser.add_argument(
        "--description",
        "-d",
        help="Descrição breve da matéria."
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Sobrescrever metadata.yaml se já existir."
    )
    args = parser.parse_args()

    # Nome da matéria
    if args.subject:
        subject_raw = " ".join(args.subject).strip()
    else:
        subject_raw = input("Nome da matéria: ").strip()

    if not subject_raw:
        print("Erro: nome da matéria não pode ser vazio.")
        sys.exit(1)

    display_name = args.display_name or subject_raw
    description = args.description or ""
    code = slugify(subject_raw)

    subject_dir = KNOWLEDGE_ROOT / code
    subject_dir.mkdir(parents=True, exist_ok=True)

    metadata_path = subject_dir / "metadata.yaml"

    if metadata_path.exists() and not args.force:
        print(f"[!] O arquivo {metadata_path} já existe. Use --force para sobrescrever.")
        sys.exit(0)

    metadata_content = {
        "name": display_name,
        "code": code,
        "description": description,
    }

    try:
        with open(metadata_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(metadata_content, f, sort_keys=False, allow_unicode=True)
        print(f"[+] metadata.yaml criado/atualizado em: {metadata_path}")
        print("Conteúdo:")
        print(yaml.safe_dump(metadata_content, sort_keys=False, allow_unicode=True))
    except Exception as e:
        print(f"[!] Erro ao escrever o metadata.yaml: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
