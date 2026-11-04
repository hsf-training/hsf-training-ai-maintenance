# Hugo

Lessons built with [Hugo](https://gohugo.io/) and the shared
[`oer-particle-physics/hugo-styles`](https://github.com/oer-particle-physics/hugo-styles)
theme module, which is based on Hextra.

## Repos *(as of 2026-10-28)*

- `hsf-training-cicd-github`. Default branch `gh-pages`.

## Layout

| Path | What it is |
|---|---|
| `content/` | **Content.** Lesson pages. |
| `static/` | **Content.** Static assets. |
| `hugo.toml` | Site config and Hugo module imports (mounts from `hugo-styles`). |
| `go.mod`, `go.sum` | Hugo module versions, e.g. `hugo-styles`. |
| `_vendor/` | Vendored Hugo modules, refreshed by a scheduled workflow. Don't edit by hand. |
| `scripts/` | Build helpers, e.g. `build-versioned-site.py` (builds a versioned site). |
| `lychee.toml`, `.lycheeignore` | Link checker config. |
| `.github/workflows/` | `pages.yml` → `reusable-pages.yml` (build + link check + deploy), `refresh-vendored-modules.yml` (scheduled theme updates), `labeler.yml`, `cffconvert.yml`. |

## Build locally

Follow the hugo-styles docs, which are the source of truth for authoring and
local previews:

- Quickstart: <https://oer-particle-physics.github.io/hugo-styles/docs/quickstart/>
- Authoring guide: <https://oer-particle-physics.github.io/hugo-styles/docs/authoring/>

Hugo, Go and Node.js are needed. CI pins the Hugo version in
`reusable-pages.yml` (`hugo-version`), so use the same version locally.

```bash
hugo server     # live preview
hugo            # build into public/
```

## Deploy

`reusable-pages.yml` builds the versioned site with
`scripts/build-versioned-site.py`, runs lychee, and deploys with
`actions/deploy-pages`.

## Pitfalls

- Theme updates arrive as automated PRs that refresh `_vendor/` and `go.mod`.
  Review them like dependency bumps.
- The site is versioned, and the build fetches all branches and tags. Changes
  to the build scripts can affect old versions of the site too.
- *(as of 2026-10-28)* The Pages source is still "Deploy from a branch"
  (`gh-pages`, `build_type: legacy`), while `pages.yml` also deploys with
  `actions/deploy-pages`. Every push therefore triggers two deploys: a Jekyll
  build of the Hugo sources, and the real Hugo build. Whichever finishes last
  is served. The fix is to switch the Pages source to "GitHub Actions" in the
  repo settings (an admin action, audit check `pages-source-mismatch`).
