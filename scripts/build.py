#!/usr/bin/env python3
"""
Gera a Biblioteca (docs/) a partir de content/<slug>/{meta.yaml, artigo.md, ...}.

Uso:
    python3 scripts/build.py

Fluxo para adicionar um novo item: ver README.md > "Adicionar um novo item".
"""
import html
import json
import re
import shutil
from pathlib import Path

import markdown
import yaml

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
DOCS = ROOT / "docs"
ASSETS_SRC = ROOT / "assets"  # CSS/JS são versionados aqui e copiados para docs/assets/ a cada build

SITE_TITLE = "Biblioteca — Ana Vitória Vanzin Mendes"
SITE_TAGLINE = (
    "Artigos e notas de pesquisa em história do direito e iconografia jurídica. "
    "PPGD/UFSC — tese Iconocracia: a alegoria feminina na história da cultura jurídica."
)
SITE_URL = "https://anavvanzin.github.io/biblioteca"

STATUS_ORDER = ["pronto-para-submissao", "em-revisao", "rascunho", "versao-anterior"]
STATUS_LABEL_FALLBACK = {
    "pronto-para-submissao": "Pronto para submissão",
    "em-revisao": "Em revisão",
    "rascunho": "Rascunho",
    "versao-anterior": "Versão anterior",
}
LANG_LABEL = {"pt-BR": "Português", "en-GB": "English", "en-US": "English", "es-ES": "Español"}

MD = markdown.Markdown(extensions=["extra", "sane_lists", "toc", "footnotes", "smarty"])


def slugify_material(name: str) -> str:
    return name


def strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return parts[2].lstrip("\n")
    return text


def load_items():
    items = []
    for folder in sorted(CONTENT.iterdir()):
        if not folder.is_dir() or folder.name.startswith("_"):
            continue
        meta_path = folder / "meta.yaml"
        md_path = folder / "artigo.md"
        if not meta_path.exists() or not md_path.exists():
            continue
        meta = yaml.safe_load(meta_path.read_text(encoding="utf-8")) or {}
        meta["slug"] = folder.name
        meta["_folder"] = folder
        raw_md = strip_frontmatter(md_path.read_text(encoding="utf-8"))
        MD.reset()
        meta["_body_html"] = MD.convert(raw_md)
        meta.setdefault("status_label", STATUS_LABEL_FALLBACK.get(meta.get("status"), meta.get("status", "")))
        items.append(meta)
    return items


def esc(s):
    return html.escape(s or "", quote=True)


def base_head(title, description, rel=""):
    return f"""<meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:type" content="website">
  <link rel="preconnect" href="https://api.fontshare.com">
  <link rel="stylesheet" href="https://api.fontshare.com/v2/css?f[]=fraunces@400,600,1&f[]=general-sans@400,500,600,700&display=swap">
  <link rel="stylesheet" href="{rel}assets/styles.css">"""


def header_nav(current, rel=""):
    def cls(key):
        return ' class="current"' if current == key else ""

    return f"""<header class="site-header">
    <div class="wrap">
      <a class="brand" href="{rel}index.html">
        <svg class="brand-mark" width="30" height="30" viewBox="0 0 30 30" fill="none" aria-hidden="true">
          <rect x="1.5" y="1.5" width="27" height="27" stroke="currentColor" stroke-width="1.5"/>
          <path d="M8 21V9h4.2c2 0 3.3 1 3.3 2.7 0 1.2-.7 2-1.7 2.4 1.2.3 2.1 1.2 2.1 2.7 0 1.9-1.4 3.2-3.6 3.2H8z" stroke="currentColor" stroke-width="1.3" fill="none"/>
          <path d="M12 9v12M8 15h4" stroke="currentColor" stroke-width="1"/>
        </svg>
        <span class="brand-title">Biblioteca</span>
        <span class="brand-sub">Ana Vitória Vanzin Mendes</span>
      </a>
      <nav class="site-nav">
        <a href="{rel}index.html"{cls('home')}>Acervo</a>
        <a href="{rel}sobre/index.html"{cls('sobre')}>Sobre &amp; como citar</a>
      </nav>
    </div>
  </header>"""


def footer(rel=""):
    return f"""<footer class="site-footer">
    <div class="wrap">
      <span>&copy; Ana Vitória Vanzin Mendes — conteúdo acadêmico da autora.</span>
      <span><a href="https://github.com/anavvanzin/biblioteca">código-fonte da biblioteca</a> · <a href="{rel}sobre/index.html">como adicionar um novo item</a></span>
    </div>
  </footer>"""


def render_tag(cls_extra, text):
    return f'<span class="tag {cls_extra}">{esc(text)}</span>'


def card_html(item, rel=""):
    slug = item["slug"]
    tema = item.get("tema", "")
    lang = item.get("lang", "")
    status = item.get("status", "")
    excerpt = (item.get("resumo") or item.get("abstract") or "").strip()
    excerpt = re.sub(r"\s+", " ", excerpt)
    if len(excerpt) > 220:
        excerpt = excerpt[:217].rsplit(" ", 1)[0] + "…"
    search_blob = " ".join(
        [
            item.get("title", ""),
            item.get("title_en", "") or "",
            tema,
            " ".join(item.get("keywords", []) or []),
            item.get("resumo", "") or "",
            item.get("abstract", "") or "",
        ]
    )
    return f"""<article class="card" data-tema="{esc(tema)}" data-lang="{esc(lang)}" data-status="{esc(status)}" data-search="{esc(search_blob)}">
        <div class="card-tags">
          {render_tag('theme', tema)}
          {render_tag('lang', LANG_LABEL.get(lang, lang))}
          {render_tag('status status-' + status, item.get('status_label', status))}
        </div>
        <h3><a href="{rel}textos/{slug}/index.html">{esc(item.get('title'))}</a></h3>
        <p class="excerpt">{esc(excerpt)}</p>
        <div class="card-foot">
          <span>{esc(str(item.get('date', '')))}</span>
          <a class="read-link" href="{rel}textos/{slug}/index.html">Ler o texto →</a>
        </div>
      </article>"""


def build_index(items):
    temas = sorted({i.get("tema", "") for i in items if i.get("tema")})
    langs = sorted({i.get("lang", "") for i in items if i.get("lang")})
    statuses = sorted({i.get("status", "") for i in items if i.get("status")}, key=lambda s: STATUS_ORDER.index(s) if s in STATUS_ORDER else 99)

    theme_chips = "\n          ".join(
        f'<button type="button" class="chip" data-group="tema" data-value="{esc(t)}" aria-pressed="false">{esc(t)}</button>' for t in temas
    )
    lang_chips = "\n          ".join(
        f'<button type="button" class="chip lang" data-group="lang" data-value="{esc(l)}" aria-pressed="false">{esc(LANG_LABEL.get(l, l))}</button>' for l in langs
    )
    status_chips = "\n          ".join(
        f'<button type="button" class="chip status" data-group="status" data-value="{esc(s)}" aria-pressed="false">{esc(STATUS_LABEL_FALLBACK.get(s, s))}</button>' for s in statuses
    )

    cards = "\n      ".join(card_html(i, rel="") for i in sorted(items, key=lambda i: str(i.get("date", "")), reverse=True))

    html_out = f"""<!doctype html>
<html lang="pt-BR">
<head>
  {base_head(SITE_TITLE, SITE_TAGLINE, rel="")}
</head>
<body>
  {header_nav('home', rel='')}
  <section class="hero">
    <div class="wrap">
      <h1>Biblioteca de artigos e notas</h1>
      <p class="lede">{esc(SITE_TAGLINE)}</p>
      <div class="hero-meta">
        <span class="stamp">{len(items)} textos catalogados</span>
        <span class="stamp">{len(temas)} temas</span>
        <span class="stamp">{len(langs)} idiomas</span>
      </div>
    </div>
  </section>
  <section class="controls">
    <div class="wrap">
      <div class="search-row">
        <input id="search" class="search-input" type="search" placeholder="Buscar por título, palavra-chave ou tema…" aria-label="Buscar na biblioteca">
      </div>
      <div class="filter-groups">
        <div class="filter-group">
          <span class="fg-label">Tema</span>
          <div class="chips">
          {theme_chips}
          </div>
        </div>
        <div class="filter-group">
          <span class="fg-label">Idioma</span>
          <div class="chips">
          {lang_chips}
          </div>
        </div>
        <div class="filter-group">
          <span class="fg-label">Status de escrita</span>
          <div class="chips">
          {status_chips}
          </div>
        </div>
      </div>
      <p class="result-count" id="result-count">{len(items)} textos encontrados</p>
    </div>
  </section>
  <main class="wrap">
    <div class="grid" id="grid">
      {cards}
    </div>
    <p class="empty-state" id="empty-state">Nenhum texto corresponde a esses filtros.</p>
  </main>
  {footer(rel="")}
  <script src="assets/app.js"></script>
</body>
</html>"""
    (DOCS / "index.html").write_text(html_out, encoding="utf-8")


def material_label(path: Path) -> str:
    stem = path.stem.replace("_", " ").replace("-", " ")
    return stem[:1].upper() + stem[1:]


def build_article(item, items_by_slug):
    slug = item["slug"]
    out_dir = DOCS / "textos" / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    folder = item["_folder"]

    # copy figuras
    figs_html = ""
    figs_src = folder / "figuras"
    if figs_src.exists():
        dest = out_dir / "figuras"
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(figs_src, dest)

    # copy downloads
    downloads_html = ""
    dl_src = folder / "downloads"
    if dl_src.exists():
        dest = out_dir / "downloads"
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(dl_src, dest)
        buttons = []
        if (dest / "artigo.pdf").exists():
            buttons.append(f'<a class="btn" href="downloads/artigo.pdf">Baixar PDF</a>')
        if (dest / "artigo.docx").exists():
            buttons.append(f'<a class="btn ghost" href="downloads/artigo.docx">Baixar DOCX</a>')
        if buttons:
            downloads_html = f'<div class="downloads-row">{"".join(buttons)}</div>'

    # copy materiais
    materials_html = ""
    mat_src = folder / "materiais"
    if mat_src.exists() and any(mat_src.iterdir()):
        dest = out_dir / "materiais"
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(mat_src, dest)
        rows = []
        for f in sorted(mat_src.iterdir()):
            if f.is_file():
                rows.append(
                    f'<li><span>{esc(material_label(f))}</span><a href="materiais/{esc(f.name)}">abrir →</a></li>'
                )
        if rows:
            materials_html = f"""<section class="materials">
      <h2>Materiais de apoio ({len(rows)})</h2>
      <ul>
        {"".join(rows)}
      </ul>
    </section>"""

    # keywords
    kw_html = ""
    keywords = item.get("keywords") or []
    if keywords:
        chips = "".join(f'<span class="tag theme">{esc(k)}</span>' for k in keywords)
        kw_html = f'<div class="article-tags">{chips}</div>'

    # abstract / resumo dual box
    resumo = item.get("resumo")
    abstract = item.get("abstract")
    boxes = []
    if resumo:
        boxes.append(f'<div class="abstract-box"><h2>Resumo</h2><p>{esc(resumo.strip())}</p></div>')
    if abstract:
        boxes.append(f'<div class="abstract-box"><h2>Abstract</h2><p>{esc(abstract.strip())}</p></div>')
    dual_cls = "dual" if len(boxes) == 2 else ""
    abstract_html = f'<div class="abstract-grid {dual_cls}">{"".join(boxes)}</div>' if boxes else ""

    # note box
    note_html = ""
    if item.get("note"):
        warn = " warn" if item.get("status") == "em-revisao" else ""
        note_html = f'<div class="note-box{warn}"><strong>Nota editorial</strong>{esc(item["note"].strip())}</div>'

    pend_link = ""
    if item.get("pendencias_file") and (folder / "materiais" / item["pendencias_file"]).exists():
        pend_link = f' <a href="materiais/{esc(item["pendencias_file"])}">Ver folha de decisão (C1–C6) →</a>'
        if note_html:
            note_html = note_html.replace("</div>", pend_link + "</div>")

    # version nav
    version_html = ""
    if item.get("supersedes") and item["supersedes"] in items_by_slug:
        prev = items_by_slug[item["supersedes"]]
        version_html = f'<div class="version-nav">Esta é uma versão revista de <a href="../{item["supersedes"]}/index.html">“{esc(prev.get("title"))}”</a>, mantida na biblioteca para registro do percurso de pesquisa.</div>'
    if item.get("superseded_by") and item["superseded_by"] in items_by_slug:
        nxt = items_by_slug[item["superseded_by"]]
        version_html = f'<div class="version-nav">Versão anterior. Ver a versão atual: <a href="../{item["superseded_by"]}/index.html">“{esc(nxt.get("title"))}”</a>.</div>'

    title_en_html = f'<p class="title-en">{esc(item["title_en"])}</p>' if item.get("title_en") else ""
    disciplina_html = f" · {esc(item['disciplina'])}" if item.get("disciplina") else ""

    html_out = f"""<!doctype html>
<html lang="{esc(item.get('lang', 'pt-BR'))}">
<head>
  {base_head(item.get('title', ''), (item.get('resumo') or item.get('abstract') or '')[:160], rel='../../')}
</head>
<body>
  {header_nav('texto', rel='../../')}
  <div class="wrap">
    <section class="article-header">
      <p class="breadcrumb"><a href="../../index.html">Acervo</a> / {esc(item.get('tema', ''))}</p>
      <h1>{esc(item.get('title'))}</h1>
      {title_en_html}
      <p class="article-byline">{esc(item.get('author', ''))} · {esc(str(item.get('date', '')))}{disciplina_html}</p>
      <div class="article-tags">
        {render_tag('theme', item.get('tema', ''))}
        {render_tag('lang', LANG_LABEL.get(item.get('lang', ''), item.get('lang', '')))}
        {render_tag('status status-' + item.get('status', ''), item.get('status_label', ''))}
      </div>
      {kw_html}
      {note_html}
      {version_html}
      {downloads_html}
      {abstract_html}
    </section>
    <article class="article-body">
      {item['_body_html']}
    </article>
    {materials_html}
  </div>
  {footer(rel='../../')}
</body>
</html>"""
    (out_dir / "index.html").write_text(html_out, encoding="utf-8")


def build_sobre(items):
    n = len(items)
    html_out = f"""<!doctype html>
<html lang="pt-BR">
<head>
  {base_head('Sobre — Biblioteca de Ana Vitória Vanzin Mendes', 'Proveniência do acervo e fluxo para adicionar novos itens.', rel='../')}
</head>
<body>
  {header_nav('sobre', rel='../')}
  <div class="wrap prose">
    <h1>Sobre esta biblioteca</h1>
    <p>Esta biblioteca reúne {n} artigos acadêmicos e suas notas de apoio, produzidos no âmbito
    da disciplina DIR410346 (História do Direito Penal e da Justiça Criminal, PPGD/UFSC) e da
    tese de doutorado <em>Iconocracia: a alegoria feminina na história da cultura jurídica</em>.
    Cada texto é catalogado por tema, idioma e status de escrita, e apresentado com resumo,
    palavras-chave, texto completo e, quando existem, materiais de apoio (fontes iconográficas,
    revisões sistemáticas, matrizes comparativas).</p>

    <h2>Como citar</h2>
    <p>Cite pelo nome completo da autora (Ana Vitória Vanzin Mendes), título do artigo, ano e o
    endereço permanente da página individual de cada texto nesta biblioteca. Os arquivos PDF e
    DOCX disponíveis para download preservam a formatação de referência de cada versão.</p>

    <h2>Proveniência e método</h2>
    <p>O conteúdo é mantido no repositório-fonte <code>artigos</code> (privado, com os rascunhos
    de trabalho e revisões) e replicado aqui, na biblioteca pública, a partir de metadados
    estruturados por texto. Rascunhos e versões anteriores são mantidos publicamente, marcados
    com seu status de escrita real — nada é ocultado, apenas identificado.</p>

    <h2>Adicionar um novo item</h2>
    <p>O fluxo é deliberadamente simples e não exige tocar em HTML ou CSS:</p>
    <ol>
      <li>Crie uma pasta em <code>content/&lt;slug-do-texto&gt;/</code>.</li>
      <li>Dentro dela, crie <code>meta.yaml</code> (título, autor, data, idioma, status,
        tema, palavras-chave, resumo/abstract) e <code>artigo.md</code> com o texto completo.
        Use <code>content/_modelo/</code> como ponto de partida.</li>
      <li>Opcionalmente, adicione <code>downloads/artigo.pdf</code>, <code>downloads/artigo.docx</code>,
        <code>figuras/</code> ou <code>materiais/</code> (notas de apoio).</li>
      <li>Rode <code>python3 scripts/build.py</code> para gerar as páginas, ou simplesmente
        <code>git push</code> — o GitHub Action reconstrói e publica a biblioteca automaticamente.</li>
    </ol>
    <pre>content/
  meu-novo-artigo/
    meta.yaml
    artigo.md
    downloads/
      artigo.pdf
    materiais/
      notas-de-leitura.md</pre>
    <p>Um script auxiliar cria o esqueleto por você:</p>
    <pre>python3 scripts/new_item.py "Título do novo texto"</pre>
  </div>
  {footer(rel="../")}
</body>
</html>"""
    out_dir = DOCS / "sobre"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(html_out, encoding="utf-8")


def build_data_json(items):
    slim = []
    for i in items:
        slim.append(
            {
                "slug": i["slug"],
                "title": i.get("title"),
                "title_en": i.get("title_en"),
                "author": i.get("author"),
                "date": i.get("date"),
                "lang": i.get("lang"),
                "status": i.get("status"),
                "status_label": i.get("status_label"),
                "tema": i.get("tema"),
                "keywords": i.get("keywords"),
                "resumo": i.get("resumo"),
                "abstract": i.get("abstract"),
                "url": f"textos/{i['slug']}/index.html",
            }
        )
    (DOCS / "data.json").write_text(json.dumps(slim, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    if DOCS.exists():
        shutil.rmtree(DOCS)
    DOCS.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ASSETS_SRC, DOCS / "assets")
    items = load_items()
    items_by_slug = {i["slug"]: i for i in items}
    build_index(items)
    for item in items:
        build_article(item, items_by_slug)
    build_sobre(items)
    build_data_json(items)
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Biblioteca gerada: {len(items)} textos em {DOCS}")


if __name__ == "__main__":
    main()
