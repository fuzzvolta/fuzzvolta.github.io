# diegomotion.net

Static portfolio site of Diego Salas (Diegomotion). Hosted on GitHub Pages; long videos on Cloudflare R2.

- `_src/` — build system: `build.py`, Jinja templates, `content.json` (editorial content), `videos.json`, `content/` (extracted source model + asset manifest), `static/` (css, js, fonts).
- Everything else at the root is **generated output**; edit `_src/` and rebuild, never the HTML directly.
- Rebuild: `python3 _src/build.py` (needs `jinja2`). Preview: `python3 -m http.server 8000` in the repo root.
- Images live in `assets/img` (WebP), animated GIFs were converted to `assets/loop/*.mp4`, short videos in `assets/video`, posters in `assets/poster`.
