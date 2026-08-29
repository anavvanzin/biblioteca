#!/usr/bin/env python3
"""
Cria o esqueleto de um novo item da biblioteca a partir de content/_modelo/.

Uso:
    python3 scripts/new_item.py "Título do novo texto"
    python3 scripts/new_item.py "Título do novo texto" --slug meu-slug-custom
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
TEMPLATE = CONTENT / "_modelo"


def slugify(title: str) -> str:
    s = title.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "novo-texto"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("title", help="Título do novo texto")
    parser.add_argument("--slug", help="Slug customizado (opcional)")
    args = parser.parse_args()

    slug = args.slug or slugify(args.title)
    dest = CONTENT / slug
    if dest.exists():
        print(f"Já existe content/{slug}/ — escolha outro --slug.", file=sys.stderr)
        sys.exit(1)

    shutil.copytree(TEMPLATE, dest)
    meta_path = dest / "meta.yaml"
    meta = meta_path.read_text(encoding="utf-8")
    meta = meta.replace('title: "Título completo do texto"', f'title: "{args.title}"', 1)
    meta_path.write_text(meta, encoding="utf-8")

    artigo_path = dest / "artigo.md"
    artigo = artigo_path.read_text(encoding="utf-8")
    artigo = artigo.replace("# Título completo do texto", f"# {args.title}", 1)
    artigo_path.write_text(artigo, encoding="utf-8")

    print(f"Criado content/{slug}/")
    print("Edite meta.yaml e artigo.md, depois rode: python3 scripts/build.py")


if __name__ == "__main__":
    main()
