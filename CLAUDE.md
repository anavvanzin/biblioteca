# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Camada pública e navegável do acervo de artigos de Ana Vitória Vanzin Mendes
(PPGD/UFSC, tese *Iconocracia*). Publicado em
`https://anavvanzin.github.io/biblioteca/`. O humano lê o [`README.md`](README.md).

## Comandos

```bash
pip install -r requirements.txt          # markdown==3.10.3 + pyyaml (só isso)

python3 scripts/build.py                 # gera docs/ inteiro a partir de content/ + assets/
python3 scripts/new_item.py "Título"     # copia content/_modelo/ para content/<slug>/
python3 scripts/new_item.py "Título" --slug meu-slug
python3 -m http.server -d docs 8000      # pré-visualizar o site gerado
```

Não há testes, lint nem typecheck. A verificação real é rodar `build.py` e abrir
`docs/index.html`: o build falha alto em `meta.yaml` inválido ou ausente.

O deploy é automático — `.github/workflows/deploy.yml` roda `build.py` em Python
3.12 e publica `docs/` no GitHub Pages a cada push em `main`. **Não versione
`docs/`** (está no `.gitignore`); commitar apenas `content/`, `assets/` e `scripts/`.

## Arquitetura

Gerador de site estático de arquivo único. `scripts/build.py` (~470 linhas, sem
framework, sem template engine — HTML em f-strings) faz, nesta ordem:

1. apaga e recria `docs/`, copia `assets/` → `docs/assets/`;
2. `load_items()` varre `content/*/`, ignorando pastas iniciadas por `_`, e lê
   `meta.yaml` + `artigo.md` de cada uma;
3. `build_index()` → `docs/index.html`; `build_article()` → `docs/textos/<slug>/index.html`
   (copiando `figuras/`, `downloads/`, `materiais/` de cada item);
   `build_sobre()` → página "sobre"; `build_data_json()` → `docs/data.json`;
4. escreve `docs/.nojekyll`.

**Conteúdo é dado, não código.** Cada texto é um diretório em `content/<slug>/`
com `meta.yaml` (metadados) + `artigo.md` (corpo), e as pastas opcionais
`downloads/`, `figuras/`, `materiais/`. O esqueleto canônico dos campos está em
`content/_modelo/meta.yaml` — leia-o antes de criar ou editar qualquer item; a
tabela de campos do README é a referência normativa.

**Filtros são pré-renderizados.** `assets/app.js` não consome `data.json`: ele
filtra os cards já presentes no DOM pelos atributos `data-tema`, `data-lang`,
`data-status` e `data-search` que o `build.py` emitiu. `docs/data.json` é um
índice legível por máquina, produto secundário do build. Mudar a lógica de
filtro normalmente exige tocar nos dois arquivos.

**Vocabulários controlados vivem no topo do `build.py`**, não no YAML:
`STATUS_ORDER` (que também define a ordenação da grade), `STATUS_LABEL_FALLBACK`
e `LANG_LABEL`. Um `status` ou `lang` novo em algum `meta.yaml` precisa ser
registrado ali, senão ordena e rotula errado.

## Proveniência do conteúdo

Os textos-fonte, com rascunhos e revisões em andamento, vivem no repositório
irmão `anavvanzin/artigos`. Esta biblioteca **cataloga**, não reescreve: cada
texto entra com o seu status editorial real (`rascunho`, `em-revisao`,
`pronto-para-submissao`, `versao-anterior`). Ao trazer um texto de `artigos/`,
copie o Markdown como está e descreva o estado no `meta.yaml` — não edite a prosa
da autora para "melhorar" o texto sem pedido explícito.

`supersedes` / `superseded_by` ligam versões diferentes do mesmo texto e geram
link cruzado no site; use-os em vez de apagar a versão antiga.

## Convenções

- Idioma do conteúdo, dos commits e das mensagens: português.
- Citação: ABNT NBR 6023:2025 (PT) · Chicago (EN).
- Figuras: domínio público (Wikimedia Commons), sempre indicado no texto.
