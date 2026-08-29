# Biblioteca — Ana Vitória Vanzin Mendes

Biblioteca pública, navegável por **tema**, **idioma** e **status de escrita**, dos artigos e
notas de pesquisa produzidos em torno da tese *Iconocracia: a alegoria feminina na história da
cultura jurídica* (PPGD/UFSC) e da disciplina DIR410346.

Site publicado: `https://anavvanzin.github.io/biblioteca/` (GitHub Pages, via GitHub Actions).

## Estrutura

```
content/
  <slug-do-texto>/
    meta.yaml       # metadados: título, autor, data, idioma, status, tema, palavras-chave, resumo/abstract
    artigo.md       # corpo do texto em Markdown
    downloads/       # artigo.pdf / artigo.docx (opcional)
    figuras/          # imagens citadas no texto (opcional)
    materiais/        # notas de apoio: fontes, revisão sistemática, matrizes, pendências (opcional)
  _modelo/           # esqueleto de referência para novos itens
scripts/
  build.py           # gera docs/ a partir de content/
  new_item.py        # cria o esqueleto de um novo item
docs/                # saída gerada (ignorada no git — recriada pelo Action a cada push)
```

## Adicionar um novo item

```bash
python3 scripts/new_item.py "Título do novo texto"
# edite content/<slug>/meta.yaml e content/<slug>/artigo.md
python3 scripts/build.py          # opcional — só para conferir localmente
git add content/<slug>
git commit -m "content: adiciona <slug>"
git push
```

O push é suficiente: o GitHub Action (`.github/workflows/deploy.yml`) reconstrói a biblioteca e
publica automaticamente em GitHub Pages. Não é preciso versionar `docs/`.

### Campos de `meta.yaml`

| Campo | Obrigatório | Descrição |
|---|---|---|
| `title` | sim | Título completo |
| `author` | sim | Nome da autora |
| `date` | sim | Ano ou `AAAA-MM-DD` |
| `lang` | sim | `pt-BR`, `en-GB`, etc. — usado no filtro de idioma |
| `status` | sim | `rascunho` \| `em-revisao` \| `pronto-para-submissao` \| `versao-anterior` — usado no filtro de status |
| `status_label` | não | Rótulo livre exibido no site (padrão deriva de `status`) |
| `tema` | sim | Linha de pesquisa/tema — usado no filtro de tema |
| `keywords` | não | Lista de palavras-chave |
| `resumo` / `abstract` | recomendado | Um ou ambos — exibidos na página do texto |
| `note` | não | Nota editorial livre (pendências, contexto) |
| `supersedes` / `superseded_by` | não | Slug de outra versão do mesmo texto — cria link cruzado |
| `pendencias_file` | não | Nome de um arquivo em `materiais/` linkado na nota editorial |

## Rodar localmente

```bash
pip install -r requirements.txt
python3 scripts/build.py
python3 -m http.server -d docs 8000   # abrir http://localhost:8000/
```

## Publicação (primeira configuração, uma vez só)

No GitHub, em **Settings → Pages**, defina *Source* como **GitHub Actions**. Depois disso, todo
`git push` para `main` reconstrói e publica a biblioteca.

## Proveniência

O conteúdo de origem — incluindo rascunhos de trabalho e revisões em andamento — vive no
repositório privado `artigos` (PPGD/UFSC). Esta biblioteca é a camada pública e navegável desse
acervo: nada nela é reescrito, apenas catalogado, cada texto com seu status de escrita real.

## Licença

Conteúdo acadêmico da autora (Ana Vitória Vanzin Mendes). Figuras: domínio público (Wikimedia
Commons), quando indicado no texto.
