# Younglancers — Young Creators Portfolio

The official website of **Younglancers** — a small team of young creators:

| Member | Role |
| --- | --- |
| **Krushnrajsinh Chudasama** | Co-Founder & Chief Website Developer (also PPT design expertise) |
| **Rishi** | Presentation Designer & Emerging Developer |
| **Yuvi** | Presentation Designer |

Built with React 19, TypeScript, and Vite. All project demos are **real work** that ships inside this repository and opens as a full UI in a new tab when a visitor clicks **Show Demo** — no downloads, no external dependencies.

---

## 🚀 Real Project Demos (in `public/demos/`)

| File | What it is |
| --- | --- |
| `sentinel-shield.html` | **Sentinel Shield (Cyber Shield)** — the complete self-contained security notebook UI: website phishing check, password analysis, "Ask Sentinel" assistant, Chrome-extension hub. Runs fully offline in a browser. |
| `cyber-shield-deck.html` | **Welcome to Cyber Shield** — interactive viewer of the real 10-slide presentation, with keyboard/dot navigation. |
| `jarvis-viewer.html` | **JARVIS v7 / v8** — source-code viewer that loads `jarvis_v7.py` and `jarvis_v8.py` live, with a version switcher and download links. |

Clicking **Show Demo** on any portfolio card opens one of these files as a full standalone UI in a **new browser tab**.

## 🔐 Member Access (Signup)

The **Member Access** section asks for exactly **2 fields: Name + Password**. Nothing else — no phone number, no email.

- On a static site there is no database, so accounts are stored in the visitor's **own browser** (`localStorage`), passwords stored as **SHA-256 hashes** only.
- Works on GitHub Pages with zero backend; clearing browser data clears local accounts.

## 🖥️ Local Development

```bash
npm install
npm run dev      # http://localhost:5173
npm run build    # typecheck + production build into dist/
```

## 📦 Deploying to GitHub Pages

1. Create a GitHub repository (e.g. `younglancer`).
2. Update `base` in `vite.config.ts` to exactly match the repo name: `base: '/your-repo-name/'`.
3. Push everything (including `.github/workflows/`, `.nojekyll`, and `public/demos/`).
4. In the repo: **Settings → Pages → Source → GitHub Actions**.
5. The included workflow (`.github/workflows/deploy.yml`) builds and deploys automatically on every push to `main`.

Because all demo assets live under `public/demos/` and links are built with `import.meta.env.BASE_URL`, the site and demos work at *any* Pages sub-path.

## ✨ Site Features

- **Segregated sections**: Hero → Services (Presentation, Websites) → Our Work → Team → Achievements → About → Member Access → Contact, each with its own nav anchor.
- **Restraint over RGB**: one cyan accent family, soft shadows, no glow spam.
- **Interactive cursor threads** canvas (respects `prefers-reduced-motion`).
- **Direct email contact** with pre-filled inquiry scope.

All content is centralized in **`src/config.ts`** — edit names, roles, projects, and contact details in one place.
