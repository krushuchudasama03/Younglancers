import React, { useState } from 'react';
import { SITE_CONFIG } from '../config';
import { CheckCircle2, Monitor, Smartphone, Globe, ArrowRight } from 'lucide-react';

export const WebsiteService: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'architecture' | 'fintech' | 'creative'>('architecture');
  const service = SITE_CONFIG.services.website;

  const demoSites = {
    architecture: {
      title: 'Sentinel Shield • Security Notebook',
      badge: 'Live Product UI',
      url: 'sentinel-shield.app',
      heroTagline: 'Your security notebook.',
      desc: 'The real shipped Younglancers product: website phishing checks, local password analysis, an on-device "Ask Sentinel" assistant, and a Chrome-extension hub. The full UI opens live in the Work section.',
      accent: '#10b981',
      previewBg: '#0b0d12'
    },
    fintech: {
      title: 'JARVIS v7 • Touchless Visualization HUD',
      badge: 'Software Source Demo',
      url: 'jarvis.local/hud',
      heroTagline: 'Hand-gesture 3D science HUD.',
      desc: 'Our AI-powered OpenGL visualization system: MediaPipe hand tracking, holographic reticle selection, exploded anatomy & molecule views, and an optional conversational voice brain.',
      accent: '#38bdf8',
      previewBg: '#070a10'
    },
    creative: {
      title: 'Younglancers • This Very Website',
      badge: 'Shipped & Deployed',
      url: 'younglancers.github.io',
      heroTagline: 'Young creators. Real demos. Zero noise.',
      desc: 'The site you are on right now: segregated sections, real project demos opening in new tabs, browser-based member signup, and a fully static GitHub Pages build crafted by Krushnrajsinh.',
      accent: '#818cf8',
      previewBg: '#0d0c16'
    }
  };

  const currentSite = demoSites[activeTab];

  return (
    <section id="services-web" style={{ padding: '100px 0', borderTop: '1px solid var(--border-subtle)' }}>
      <div className="container">
        {/* Section Header */}
        <div style={{ maxWidth: '820px', marginBottom: '56px' }}>
          <div className="kicker-badge" style={{ marginBottom: '16px' }}>
            <span className="kicker-dot" />
            <span>PRIMARY SERVICE 02 • WEBSITES & SOFTWARE</span>
          </div>
          <h2 style={{ fontSize: 'clamp(32px, 5vw, 56px)', color: '#ffffff', marginBottom: '20px' }}>
            {service.headline}
          </h2>
          <p style={{ fontSize: '18px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
            {service.supporting}
          </p>
        </div>

        {/* Browser Mockup Interactive Showcase */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            gap: '36px',
            alignItems: 'center',
            marginBottom: '64px',
          }}
        >
          {/* Left: Interactive Browser Shell */}
          <div
            className="glass-panel"
            style={{
              padding: '24px',
              border: '1px solid var(--border-active)',
              boxShadow: '0 20px 50px rgba(0, 0, 0, 0.6)',
              overflow: 'hidden',
            }}
          >
            {/* Browser Top Bar */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                paddingBottom: '16px',
                marginBottom: '16px',
                borderBottom: '1px solid var(--border-subtle)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#ef4444' }} />
                <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#eab308' }} />
                <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#22c55e' }} />
              </div>
              {/* URL Pill */}
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  background: 'rgba(255, 255, 255, 0.05)',
                  padding: '4px 14px',
                  borderRadius: '9999px',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  maxWidth: '260px',
                  width: '100%',
                  justifyContent: 'center',
                }}
              >
                <Globe size={12} color="var(--text-muted)" />
                <span
                  style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: '11px',
                    color: 'var(--text-secondary)',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                  }}
                >
                  https://{currentSite.url}
                </span>
              </div>
              <div style={{ display: 'flex', gap: '8px' }}>
                <Monitor size={15} color="var(--text-muted)" />
                <Smartphone size={15} color="var(--text-muted)" />
              </div>
            </div>

            {/* Browser Viewport Preview Area */}
            <div
              style={{
                backgroundColor: currentSite.previewBg,
                border: '1px solid rgba(255, 255, 255, 0.08)',
                borderRadius: '10px',
                padding: '36px 28px',
                minHeight: '320px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                position: 'relative',
                overflow: 'hidden',
              }}
            >
              {/* Internal simulated website navbar */}
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: '28px',
                  paddingBottom: '12px',
                  borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
                }}
              >
                <span style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '13px', color: '#fff' }}>
                  {currentSite.title.split('•')[0]}
                </span>
                <span
                  style={{
                    fontSize: '10px',
                    fontFamily: 'var(--font-mono)',
                    color: currentSite.accent,
                    background: 'rgba(255, 255, 255, 0.05)',
                    padding: '2px 8px',
                    borderRadius: '4px',
                  }}
                >
                  {currentSite.badge}
                </span>
              </div>

              {/* Viewport Content */}
              <div>
                <h3
                  style={{
                    fontSize: 'clamp(22px, 3.2vw, 28px)',
                    color: '#ffffff',
                    fontWeight: 700,
                    lineHeight: 1.25,
                    marginBottom: '12px',
                  }}
                >
                  {currentSite.heroTagline}
                </h3>
                <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: 1.6, maxWidth: '480px' }}>
                  {currentSite.desc}
                </p>
              </div>

              {/* Simulated UI action bar */}
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  marginTop: '28px',
                }}
              >
                <span
                  style={{
                    fontSize: '12px',
                    fontWeight: 600,
                    padding: '6px 14px',
                    borderRadius: '9999px',
                    backgroundColor: '#ffffff',
                    color: '#000000',
                  }}
                >
                  Real Project Preview
                </span>
                <span
                  style={{
                    fontSize: '11px',
                    color: 'var(--text-muted)',
                    fontFamily: 'var(--font-mono)',
                  }}
                >
                  Clean React + TypeScript
                </span>
              </div>
            </div>

            {/* Concept Switcher Buttons */}
            <div
              style={{
                display: 'flex',
                gap: '10px',
                marginTop: '18px',
                flexWrap: 'wrap',
              }}
            >
              <button
                onClick={() => setActiveTab('architecture')}
                style={{
                  flex: 1,
                  padding: '9px 12px',
                  borderRadius: '8px',
                  fontSize: '12.5px',
                  fontWeight: 500,
                  cursor: 'pointer',
                  border: activeTab === 'architecture' ? '1px solid var(--accent-cyan)' : '1px solid rgba(255, 255, 255, 0.08)',
                  backgroundColor: activeTab === 'architecture' ? 'rgba(56, 189, 248, 0.1)' : 'rgba(255, 255, 255, 0.02)',
                  color: activeTab === 'architecture' ? '#ffffff' : 'var(--text-secondary)',
                  transition: 'all 0.2s ease',
                }}
              >
                Sentinel Shield
              </button>
              <button
                onClick={() => setActiveTab('fintech')}
                style={{
                  flex: 1,
                  padding: '9px 12px',
                  borderRadius: '8px',
                  fontSize: '12.5px',
                  fontWeight: 500,
                  cursor: 'pointer',
                  border: activeTab === 'fintech' ? '1px solid var(--accent-cyan)' : '1px solid rgba(255, 255, 255, 0.08)',
                  backgroundColor: activeTab === 'fintech' ? 'rgba(56, 189, 248, 0.1)' : 'rgba(255, 255, 255, 0.02)',
                  color: activeTab === 'fintech' ? '#ffffff' : 'var(--text-secondary)',
                  transition: 'all 0.2s ease',
                }}
              >
                JARVIS HUD
              </button>
              <button
                onClick={() => setActiveTab('creative')}
                style={{
                  flex: 1,
                  padding: '9px 12px',
                  borderRadius: '8px',
                  fontSize: '12.5px',
                  fontWeight: 500,
                  cursor: 'pointer',
                  border: activeTab === 'creative' ? '1px solid var(--accent-cyan)' : '1px solid rgba(255, 255, 255, 0.08)',
                  backgroundColor: activeTab === 'creative' ? 'rgba(56, 189, 248, 0.1)' : 'rgba(255, 255, 255, 0.02)',
                  color: activeTab === 'creative' ? '#ffffff' : 'var(--text-secondary)',
                  transition: 'all 0.2s ease',
                }}
              >
                This Site
              </button>
            </div>
          </div>

          {/* Right: Technical Capabilities & Deliverables */}
          <div>
            <div style={{ display: 'grid', gap: '18px', marginBottom: '32px' }}>
              {service.disciplines.map((d, index) => (
                <div
                  key={index}
                  style={{
                    padding: '18px 22px',
                    borderRadius: '12px',
                    background: 'rgba(255, 255, 255, 0.02)',
                    border: '1px solid rgba(255, 255, 255, 0.05)',
                  }}
                >
                  <h4 style={{ fontSize: '16px', color: '#ffffff', marginBottom: '6px' }}>{d.title}</h4>
                  <p style={{ fontSize: '13.5px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>{d.desc}</p>
                </div>
              ))}
            </div>

            {/* Deliverables List */}
            <div style={{ marginBottom: '36px' }}>
              <div style={{ fontSize: '12px', fontFamily: 'var(--font-mono)', color: 'var(--accent-cyan)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '14px' }}>
                Engineering Standards
              </div>
              <div style={{ display: 'grid', gap: '10px' }}>
                {service.deliverables.map((deliv, idx) => (
                  <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '14px', color: 'var(--text-secondary)' }}>
                    <CheckCircle2 size={16} color="var(--accent-cyan)" />
                    <span>{deliv}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Dedicated Service CTA */}
            <a
              href={`mailto:${SITE_CONFIG.email}?subject=${encodeURIComponent('Inquiry: Website Design & Development')}`}
              className="btn-primary"
            >
              <span>{service.cta}</span>
              <ArrowRight size={16} />
            </a>
          </div>
        </div>
      </div>
    </section>
  );
};
