# PixelForge ✦ (Repository: `Younglancers`)

> **"Designing ideas. Building real things."**  
> A trio of young creators building bespoke websites, high-stakes pitch decks, and shipped security software.

Website Brand: **PixelForge**  
GitHub Repository Name: **`Younglancers`** (Exact case: Capital `Y`, `Younglancers`, no space)

---

## 🌟 What's New in this Build

1. **Aesthetic Minimalist Light Theme**:
   - High-contrast, clean porcelain canvas (`#fafbfc`), crisp slate typography, and restrained tactile accents (Royal Cobalt `#2563eb`, Emerald `#059669`, and Amber `#ea580c`).
   - Human-crafted feel — zero generic AI templates or robotic filler text.
2. **Interactive Elastic Thread Grid Canvas**:
   - Subtle background woven square thread grid that flexes with harmonic spring physics and glows when interacting with cursor or touch.
3. **Zero 404 Errors on GitHub Pages**:
   - **Direct Branch Ready**: No GitHub Actions workflows or build steps required.
   - **Relative Path Architecture**: All assets and demo links use `./`, ensuring that local files, custom domains, and GitHub Pages URLs (`https://<username>.github.io/Younglancers/`) work seamlessly without 404 errors.
4. **All Shipped Demos Included**:
   - `demos/sentinel-shield.html`: Live interactive cybersecurity workspace (phishing link detector, offline password strength analyzer, Ask Sentinel assistant, Chrome extension hub).
   - `demos/cyber-shield-deck.html`: Interactive 10-slide master PowerPoint deck demo.
   - `demos/jarvis-viewer.html?version=v7`: Touchless 3D OpenGL & MediaPipe scientific HUD source code viewer.
   - `demos/jarvis-viewer.html?version=v8`: Continued evolution of JARVIS with side-by-side version comparison.
5. **Interactive In-Page Features**:
   - **Embedded Lightbox Demo Previewer**: Test any demo right inside the page without leaving.
   - **Interactive Slide Flow Viewer**: Inspect 3 master deck slide archetypes with live metrics and themes.
   - **Web Engineering Viewport Switcher**: Toggle between live product showcases.
   - **Interactive Project Scope & Turnaround Estimator**: Calculate project delivery timelines and apply scope directly to the contact brief.
   - **Member Circle**: Client-side privacy-first member portal with SHA-256 local hashing and zero tracking.
   - **Direct Contact Protocol**: Pre-addressed `mailto:krushuchudasama03@gmail.com` generator and 1-click email copy with celebratory micro-confetti.

---

## 👥 The PixelForge Crew

- **Krushnrajsinh Chudasama** (Age 15, India • Worldwide Remote):
  - *Co-Founder & Chief Website Developer* (and PPT design expert).
  - Engineered Sentinel Shield, the JARVIS HUD viewer, and PixelForge's responsive interface. Also an expert in high-stakes PowerPoint presentations — investor narratives, data visualization, and structural typography.
  - Email: [`krushuchudasama03@gmail.com`](mailto:krushuchudasama03@gmail.com)
- **Rishi**:
  - *Presentation Designer & Emerging Developer*.
  - Designs clean, compelling slide decks for conferences, academic symposiums, and product pitches. Actively expanding his toolkit into code.
- **Yuvi**:
  - *Presentation Designer*.
  - Crafts presentation decks that communicate clearly — disciplined typography, thoughtful pacing, and layouts that keep complex information easy to absorb.

---

## 🏆 Honors & Track Record

- **WSRO Regional Winner** (World STEM & Robotics Olympiad 2024–2025, Regional Champion)
- **Sentinel Shield / Cyber Shield Suite** (2025–2026, Shipped Working Product)
- **Model United Nations (MUN) Delegate** (2024, Multilateral Diplomacy & Public Speaking)
- **Sahodaya Inter-School Debate** (2024, Debate Distinction)

---

## 🚀 How to Publish to GitHub (Zero 404 Direct Branch Setup)

### Step 1: Open Terminal in this folder
```bash
cd "c:\Users\hp\Downloads\Younglancers"
```

### Step 2: Initialize Git and Commit
```bash
git init
git add .
git commit -m "feat: launch PixelForge aesthetic light website with interactive thread grid and live demos"
git branch -M main
```

### Step 3: Link to your GitHub Repository `Younglancers`
*(Replace `<your-github-username>` with your actual GitHub username)*
```bash
git remote add origin https://github.com/<your-github-username>/Younglancers.git
git push -u origin main --force
```

### Step 4: Enable GitHub Pages (Direct Branch)
1. Go to your repository on GitHub: `https://github.com/<your-github-username>/Younglancers`
2. Click **Settings** (top tab).
3. In the left sidebar, click **Pages** (under *Code and automation*).
4. Under **Build and deployment**:
   - **Source**: Select `Deploy from a branch`.
   - **Branch**: Select `main`.
   - **Folder**: Select `/ (root)`.
   - Click **Save**.
5. Wait 30 seconds — your website is instantly LIVE at:
   ```
   https://<your-github-username>.github.io/Younglancers/
   ```
   **Zero 404 errors!**

---

## 📂 Project Structure

```
Younglancers/
├── index.html                  # Main entrance point (relative paths, zero-build required)
├── .gitignore                  # Clean repository ignore list
├── .nojekyll                   # Instructs GitHub Pages to serve all files verbatim
├── package.json                # Optional local dev scripts
├── README.md                   # Full documentation & deployment guide
├── favicon.svg                 # Website icon
├── icons.svg                   # Sprite assets
├── assets/
│   ├── css/
│   │   ├── style.css           # Core aesthetic light theme design system
│   │   └── components.css      # Hero, work cards, deck viewer, estimator, modals
│   └── js/
│       ├── confetti.js         # Zero-dependency micro-confetti effect
│       ├── grid-threads.js     # Woven square grid elastic thread canvas simulation
│       └── app.js              # Application logic, filters, modal, member portal, mailto
└── demos/
    ├── sentinel-shield.html    # Full shipped cybersecurity workspace
    ├── cyber-shield-deck.html  # Full 10-slide master presentation deck demo
    ├── jarvis-viewer.html      # Interactive source viewer with v7 / v8 version switcher
    ├── jarvis_v7.py            # Complete JARVIS v7 Python source
    └── jarvis_v8.py            # Complete JARVIS v8 Python source
```

---

© 2026 PixelForge. Handcrafted by Krushnrajsinh Chudasama, Rishi, and Yuvi.
