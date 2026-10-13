export interface ProjectItem {
  id: string;
  title: string;
  category: 'presentation' | 'web';
  badge: string;
  description: string;
  tags: string[];
  features: string[];
  deliverables: string[];
  demoType: 'live-ui' | 'deck' | 'code';
  demoUrl: string;
  slides?: {
    slideNumber: number;
    title: string;
    subtitle: string;
    highlights: string[];
    layout: 'editorial' | 'data-grid' | 'hero-stat' | 'case-split';
    theme: 'dark-cinematic' | 'editorial-ivory' | 'executive-blue' | 'research-clean';
  }[];
  browserPreview?: {
    url: string;
    headline: string;
    subheadline: string;
    colorScheme: string;
    highlights: string[];
  };
}

export interface AchievementItem {
  id: string;
  year: string;
  title: string;
  organization: string;
  category: 'Robotics & STEM' | 'Debate & MUN' | 'Leadership';
  badge: string;
  description: string;
  significance: string;
}

export interface TeamMember {
  id: string;
  name: string;
  role: string;
  headline: string;
  bio: string;
  skills: string[];
  accent: 'cyan' | 'indigo' | 'emerald';
  icon: 'code' | 'slides' | 'slides2';
}

const BASE_URL = import.meta.env.BASE_URL;

export const SITE_CONFIG = {
  // CENTRAL IDENTIFIER & CONTACT (EASILY EDITABLE)
  brandName: 'Younglancers',
  tagline: 'Young creators. Real deliverables.',
  professionalIdentity: 'Young creators building websites, decks & security tools',
  fullName: 'Krushnrajsinh Chudasama',
  founderName: 'Krushnrajsinh Chudasama',
  email: 'krushuchudasama03@gmail.com',

  age: 15,
  location: 'India • Worldwide Remote',

  // AVAILABILITY TOGGLE
  isAvailableForWork: true,
  availabilityText: 'Open for Q4 / 2026 Projects',

  // HERO CONTENT
  hero: {
    kicker: 'YOUNGLANCERS • A TEAM OF YOUNG CREATORS',
    headingLine1: 'Designing ideas.',
    headingLine2: 'Building real things.',
    supportingText:
      "Younglancers is a team of young creators led by Krushnrajsinh. We design presentations, build websites, and ship real software — like Sentinel Shield, our cyber-safety platform you can try live.",
    primaryCta: "Let's Work Together",
    secondaryCta: 'Explore Our Work',
  },

  // ABOUT CONTENT
  about: {
    statement:
      "Younglancers is a small team of young makers. Krushnrajsinh (Co-Founder & Chief Website Developer) also designs presentations; Rishi and Yuvi are our presentation designers, with Rishi emerging in coding too.\n\nEverything we show here is real work — the security tools, the AI system, and the decks are things we actually built.",
    philosophyPoints: [
      {
        num: '01',
        title: 'Real Work, Real Demos',
        desc: 'Every project on this site is something we actually built. Click "Show Demo" and you see the real UI — not a mockup or stock render.',
      },
      {
        num: '02',
        title: 'Structure Before Style',
        desc: 'Presentations and websites that succeed are built on logic, hierarchy, and purpose — not decorative clutter.',
      },
      {
        num: '03',
        title: 'Bespoke & Tailored',
        desc: 'No recycled templates. Each deck layout and web component is engineered from first principles for your specific topic.',
      },
      {
        num: '04',
        title: 'Direct Collaboration',
        desc: 'Work directly with the Younglancers crew — Krushnrajsinh on websites, and Rishi / Yuvi on presentation design. Swift, focused communication.',
      },
    ],
  },

  // TEAM (SEGREGATED SECTION)
  team: [
    {
      id: 'krushnrajsinh',
      name: 'Krushnrajsinh Chudasama',
      role: 'Co-Founder & Chief Website Developer',
      headline: 'Builds the websites — and the decks too.',
      bio: 'Co-founder of Younglancers. Chief website developer of the team: crafted every interface you see here, including Sentinel Shield and this portfolio. Also an expert in making PowerPoint decks — investor-style narratives, data hierarchies, and clean slide systems.',
      skills: ['Website Development', 'React & TypeScript', 'Chief Developer', 'PPT Design Expertise'],
      accent: 'cyan',
      icon: 'code',
    },
    {
      id: 'rishi',
      name: 'Rishi',
      role: 'Presentation Designer & Emerging Developer',
      headline: 'PPT design first — now learning to code.',
      bio: 'Rishi designs the polished, clean presentation decks at Younglancers, from academic symposiums to product pitches. He is also emerging in coding — leveling up on programming alongside his design craft.',
      skills: ['PPT Design', 'Emerging in Coding', 'Creative Layouts'],
      accent: 'indigo',
      icon: 'slides',
    },
    {
      id: 'yuvi',
      name: 'Yuvi',
      role: 'Presentation Designer',
      headline: 'Slides that carry the story.',
      bio: 'Yuvi crafts presentation decks that communicate clearly — disciplined typography, thoughtful pacing, and layouts that keep complex information easy to absorb.',
      skills: ['PPT Design', 'Visual Storytelling', 'Slide Systems'],
      accent: 'emerald',
      icon: 'slides2',
    },
  ] as TeamMember[],

  // ACHIEVEMENTS
  achievements: [
    {
      id: 'wsro-regional',
      year: '2024 - 2025',
      title: 'WSRO Regional Winner',
      organization: 'World STEM & Robotics Olympiad',
      category: 'Robotics & STEM',
      badge: 'Regional Champion',
      description:
        'Secured 1st place in the regional chapter of the World STEM & Robotics Olympiad, engineering innovative hardware prototypes and high-impact technical presentation decks.',
      significance:
        'Demonstrated advanced technical problem-solving, structural mechanics, and clear scientific communication.',
    },
    {
      id: 'cyber-shield',
      year: '2025 - 2026',
      title: 'Sentinel Shield / Cyber Shield Suite',
      organization: 'Self-started Product Build',
      category: 'Leadership',
      badge: 'Shipped Product',
      description:
        'Built a complete cyber-safety platform: live phishing-pattern analysis with a risk verdict, local password analysis, an AI-styled guidance assistant, and a Chrome extension that flags risky pages while browsing.',
      significance:
        'A full working product — the UI you can demo in a new tab is powered by the shipped code.',
    },
    {
      id: 'mun-delegate',
      year: '2024',
      title: 'Model United Nations (MUN) Delegate',
      organization: 'Inter-School & Regional MUN Conferences',
      category: 'Debate & MUN',
      badge: 'Diplomacy & Public Speaking',
      description:
        'Represented nation-state delegations across intense multilateral committee debates, authoring working papers, crisis directives, and policy resolutions.',
      significance:
        'Honed rhetoric, negotiation tactics, rapid information synthesis, and persuasive storytelling.',
    },
    {
      id: 'sahodaya-debate',
      year: '2024',
      title: 'Sahodaya Inter-School Debate',
      organization: 'Sahodaya School Complex',
      category: 'Debate & MUN',
      badge: 'Debate Distinction',
      description:
        'Awarded top standing in high-stakes parliamentary and extempore debate rounds on contemporary socio-economic, ethical, and technological governance topics.',
      significance:
        'Proven ability to dissect multifaceted arguments under strict time constraints.',
    },
  ] as AchievementItem[],

  // SERVICES
  services: {
    presentation: {
      headline: 'Complex information. Beautifully presented.',
      supporting:
        'Rishi and Yuvi design the decks; Krushnrajsinh supports with PPT expertise and the underlying narrative structure. From raw information to refined slides.',
      cta: 'Discuss a Presentation',
      disciplines: [
        {
          title: 'Executive & Business Pitch Decks',
          desc: 'High-stakes presentations structured to captivate investors, partners, and leadership.',
        },
        {
          title: 'Academic & Research Presentations',
          desc: 'Dense studies, methodology diagrams, and findings translated into digestible visual slides.',
        },
        {
          title: 'Educational & Keynote Slides',
          desc: 'Lecture structures, seminar talks, and workshop decks with intentional pacing.',
        },
        {
          title: 'Data Visualization & Custom Charts',
          desc: 'Comparative metric tables and infographics that make raw numbers immediately clear.',
        },
      ],
      deliverables: [
        'Fully editable Microsoft PowerPoint (.pptx) master files',
        'Custom typography palettes and slide master layouts',
        'Exported high-res PDF presentation decks',
        'Light & Dark visual themes upon request',
      ],
    },
    website: {
      headline: 'Websites that feel as good as they function.',
      supporting:
        'Led by Krushnrajsinh, our chief website developer. Polished interfaces, thoughtful navigation, responsive layouts, and real shipped products behind every demo.',
      cta: 'Discuss a Website',
      disciplines: [
        {
          title: 'Modern Bespoke Interfaces',
          desc: 'Tailored frontend architectures with precision spacing, typography, and a composed dark aesthetic.',
        },
        {
          title: 'Smooth Motion & Micro-interactions',
          desc: 'Fluid motion, magnetic buttons, canvas visualizers, and state transitions that elevate engagement.',
        },
        {
          title: 'Responsive Across Every Device',
          desc: 'Optimized for smartphones, tablets, laptops, and ultra-wide monitors.',
        },
        {
          title: 'Clean, Maintainable Codebase',
          desc: 'Component-driven structure with TypeScript, React, and modular styling — GitHub-ready handover.',
        },
      ],
      deliverables: [
        'Full production codebase repository handover',
        'Responsive, cross-browser verified layouts',
        'Zero-dependency or optimized lightweight libraries',
        'Live deployment guidance (GitHub Pages / Vercel / Netlify)',
      ],
    },
  },

  // PORTFOLIO — REAL SHIPPED WORK (ALL FILES INSIDE THIS REPO, public/demos/)
  portfolio: [
    {
      id: 'sentinel-shield',
      title: 'Sentinel Shield • Cyber Safety Platform',
      category: 'web',
      badge: 'Live UI Demo',
      description:
        'Our complete cyber-safety workspace: a calm notebook-style UI for checking websites against phishing patterns, analyzing passwords locally, an "Ask Sentinel" assistant, and a built-in Chrome extension hub. The demo opens the whole real UI — the actual shipped file.',
      tags: ['Cyber Security', 'Live Web UI', 'Chrome Extension', 'Real Product'],
      features: ['Website Phishing Check', 'Password Strength Analyzer', 'On-Device, No Tracking', 'Ask Sentinel Assistant'],
      deliverables: ['Sentinel Shield notebook (single-file app)', 'Chrome extension module', 'Password & phishing pattern datasets'],
      demoType: 'live-ui',
      demoUrl: `${BASE_URL}demos/sentinel-shield.html`,
      browserPreview: {
        url: 'sentinel-shield.app',
        headline: 'Your security notebook',
        subheadline: 'A calm workspace for checking links, testing passwords, and getting clear answers.',
        colorScheme: 'Paper & Sage — calm notebook aesthetic',
        highlights: ['Overview Dashboard', 'Website Check', 'Password Lab', 'Assistant + Extension'],
      },
    },
    {
      id: 'cyber-shield-deck',
      title: 'Welcome to Cyber Shield • Deck',
      category: 'presentation',
      badge: 'Live Deck Demo',
      description:
        'The real presentation for our Cyber Shield platform — 10 slides covering the aim, the problem of website trust, layered protection signals, password analysis, AI guidance, the Chrome extension, and the modular system architecture. The demo plays the actual deck content.',
      tags: ['PowerPoint (.PPTX)', 'Real Deck', 'Digital Safety', 'Narrative Structure'],
      features: ['10 Real Slides', 'Signal-by-Signal Story', 'Clear Risk Verdict Narrative', 'Dark Cinematic Theme'],
      deliverables: ['Native .pptx master deck', 'Slide-by-slide narrative', 'Matching product UI screenshots'],
      demoType: 'deck',
      demoUrl: `${BASE_URL}demos/cyber-shield-deck.html`,
      slides: [
        {
          slideNumber: 1,
          title: 'Welcome to Cyber Shield',
          subtitle: 'Check. Verify. Stay Safe.',
          highlights: ['Cyber Shield · Digital Safety', 'Security-focused platform', 'Safer digital decisions'],
          layout: 'editorial',
          theme: 'dark-cinematic',
        },
        {
          slideNumber: 2,
          title: 'Our aim: make every click a safer decision',
          subtitle: 'Confidence through layered checks instead of guesswork.',
          highlights: ['Verify', 'Understand', 'Protect'],
          layout: 'case-split',
          theme: 'executive-blue',
        },
        {
          slideNumber: 4,
          title: 'Why website trust is difficult',
          subtitle: 'One careless click can expose personal information or credentials.',
          highlights: ['Fake sites imitate brands', 'Suspicious URLs hide redirects', 'Fast verdicts needed'],
          layout: 'hero-stat',
          theme: 'dark-cinematic',
        },
        {
          slideNumber: 8,
          title: 'AI guidance + protection while browsing',
          subtitle: 'Technical findings become clear next steps.',
          highlights: ['Cyber Shield AI assistant', 'Security badge in browser', 'Explain every warning'],
          layout: 'case-split',
          theme: 'executive-blue',
        },
        {
          slideNumber: 10,
          title: 'Cyber Shield: check before you trust',
          subtitle: 'Detect. Verify. Understand. Protect.',
          highlights: ['Layered guidance', 'Safer behavior one click at a time', 'Takeaway'],
          layout: 'editorial',
          theme: 'dark-cinematic',
        },
      ],
    },
    {
      id: 'jarvis-v7',
      title: 'JARVIS v7 • Touchless AI Visualization',
      category: 'web',
      badge: 'Source Demo',
      description:
        'An AI-powered, hand-gesture-driven scientific visualization system: real OpenGL 3D rendering, MediaPipe hand/face tracking, a holographic HUD, exploded anatomy & molecule views, a virtual chemistry lab, and an optional conversational voice brain. Demo shows the live source in a viewer.',
      tags: ['OpenGL', 'MediaPipe', 'Python', 'Gesture Control'],
      features: ['Hand-gesture control + dwell-select', 'Real 3D lighting & transparent glass models', 'Virtual chemistry lab', '4 HUD themes + full keyboard fallback'],
      deliverables: ['Full jarvis_v7.py source (in this repo)', 'Dependencies & install guide', 'Optional AI brain module'],
      demoType: 'code',
      demoUrl: `${BASE_URL}demos/jarvis-viewer.html?version=v7`,
    },
    {
      id: 'jarvis-v8',
      title: 'JARVIS v8 • Continued System',
      category: 'web',
      badge: 'Source Demo',
      description:
        'The continuation of the JARVIS visualization system — the latest stable iteration we ship, kept alongside v7 in this repository. Demo shows the live source in a viewer with a version switch between v7 and v8.',
      tags: ['Python', 'Real-time Rendering', 'Voice AI', 'Long-term Project'],
      features: ['Same proven render core', 'Snapshot of the shipped build', 'Side-by-side version comparison', 'Zero required paid APIs'],
      deliverables: ['Full jarvis_v8.py source (in this repo)', 'Version diff capability via the viewer', 'Run instructions'],
      demoType: 'code',
      demoUrl: `${BASE_URL}demos/jarvis-viewer.html?version=v8`,
    },
  ] as ProjectItem[],

  // CONTACT OPTIONS
  inquiryOptions: [
    { id: 'presentation', label: 'PowerPoint Presentation', subject: 'Inquiry: PowerPoint Presentation Design' },
    { id: 'website', label: 'Website Development', subject: 'Inquiry: Website Design & Development' },
    { id: 'both', label: 'Both (Website & Presentation)', subject: 'Inquiry: Comprehensive Website & Presentation Package' },
    { id: 'other', label: 'Other / Custom Project', subject: 'Inquiry: Custom Creative Collaboration' },
  ],
};
