import React, { useState } from 'react';
import { SITE_CONFIG } from '../config';
import { CheckCircle2, ArrowRight } from 'lucide-react';

export const PresentationService: React.FC = () => {
  const [activeSlideIndex, setActiveSlideIndex] = useState(0);
  const service = SITE_CONFIG.services.presentation;

  const mockDeckSlides = [
    {
      num: '01 / EXECUTIVE SUMMARY',
      category: 'Dark Cinematic • Investor Deck',
      title: 'Decentralized Neural Fabric Architecture',
      subtitle: 'Achieving 2.4x throughput per watt across distributed edge inference clusters.',
      metrics: [
        { label: 'ENERGY EFFICIENCY', val: '4.8 TFLOPS/W' },
        { label: 'NETWORK LATENCY', val: '< 0.38 ms' },
        { label: 'CLUSTER PARITY', val: '99.98%' }
      ],
      themeBg: '#090d16',
      accentColor: '#38bdf8'
    },
    {
      num: '02 / METHODOLOGY & RESEARCH',
      category: 'Academic & Scientific Symposium',
      title: 'Targeted In-Vivo RNA Base Editing',
      subtitle: 'Comparative safety profile and off-target screening across 1,200 mammalian sequences.',
      metrics: [
        { label: 'AFFINITY RATE', val: '96.2%' },
        { label: 'OFF-TARGETS', val: '0 DETECTED' },
        { label: 'COHORT SIZE', val: 'n = 450' }
      ],
      themeBg: '#0e1117',
      accentColor: '#10b981'
    },
    {
      num: '03 / MARKET EXPANSION',
      category: 'Editorial Modern Business',
      title: 'Global Enterprise Adoption Roadmap',
      subtitle: 'Systematic pipeline transition targeting Tier-1 financial institutions across 2026-2028.',
      metrics: [
        { label: 'TAM TARGET', val: '$24.6B' },
        { label: 'ENTERPRISE MOAT', val: '8 PATENTS' },
        { label: 'PILOT PARTNERS', val: '14 SIGNED' }
      ],
      themeBg: '#13111c',
      accentColor: '#a78bfa'
    }
  ];

  const currentSlide = mockDeckSlides[activeSlideIndex];

  return (
    <section id="services-presentation" style={{ padding: '100px 0', borderTop: '1px solid var(--border-subtle)' }}>
      <div className="container">
        {/* Section Header */}
        <div style={{ maxWidth: '820px', marginBottom: '56px' }}>
          <div className="kicker-badge" style={{ marginBottom: '16px' }}>
            <span className="kicker-dot" />
            <span>PRIMARY SERVICE 01 • PRESENTATION DESIGN</span>
          </div>
          <h2 style={{ fontSize: 'clamp(32px, 5vw, 56px)', color: '#ffffff', marginBottom: '20px' }}>
            {service.headline}
          </h2>
          <p style={{ fontSize: '18px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
            {service.supporting}
          </p>
        </div>

        {/* Presentation Studio & Interactive Slide Gallery */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            gap: '32px',
            alignItems: 'center',
            marginBottom: '64px',
          }}
        >
          {/* Interactive Slide Viewer Showcase */}
          <div
            className="glass-panel"
            style={{
              padding: '24px',
              border: '1px solid var(--border-active)',
              boxShadow: '0 20px 50px rgba(0, 0, 0, 0.6)',
              position: 'relative',
            }}
          >
            {/* Slide Header Toolbar */}
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
                <span
                  style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: '11px',
                    color: 'var(--text-muted)',
                    marginLeft: '8px',
                  }}
                >
                  Master_Deck_Preview.pptx (16:9 HD)
                </span>
              </div>
              <span
                style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: '11px',
                  color: currentSlide.accentColor,
                  fontWeight: 600,
                }}
              >
                {currentSlide.num}
              </span>
            </div>

            {/* The Actual Slide Frame */}
            <div
              style={{
                backgroundColor: currentSlide.themeBg,
                border: '1px solid rgba(255, 255, 255, 0.08)',
                borderRadius: '12px',
                padding: '36px 32px',
                minHeight: '340px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                transition: 'all 0.4s ease',
                position: 'relative',
                overflow: 'hidden',
              }}
            >
              {/* Subtle background glow */}
              <div
                style={{
                  position: 'absolute',
                  top: '-40px',
                  right: '-40px',
                  width: '180px',
                  height: '180px',
                  borderRadius: '50%',
                  background: currentSlide.accentColor,
                  opacity: 0.1,
                  filter: 'blur(40px)',
                  pointerEvents: 'none',
                }}
              />

              <div>
                <div
                  style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: '11.5px',
                    color: currentSlide.accentColor,
                    textTransform: 'uppercase',
                    letterSpacing: '0.14em',
                    marginBottom: '12px',
                  }}
                >
                  {currentSlide.category}
                </div>
                <h3
                  style={{
                    fontSize: 'clamp(22px, 3vw, 30px)',
                    color: '#ffffff',
                    lineHeight: 1.25,
                    marginBottom: '14px',
                  }}
                >
                  {currentSlide.title}
                </h3>
                <p style={{ fontSize: '14.5px', color: 'var(--text-secondary)', lineHeight: 1.6, maxWidth: '520px' }}>
                  {currentSlide.subtitle}
                </p>
              </div>

              {/* Data Visualization / Metrics Row */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(3, 1fr)',
                  gap: '14px',
                  marginTop: '32px',
                  paddingTop: '20px',
                  borderTop: '1px solid rgba(255, 255, 255, 0.08)',
                }}
              >
                {currentSlide.metrics.map((m, idx) => (
                  <div key={idx} style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '10px 14px', borderRadius: '8px' }}>
                    <div style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', color: 'var(--text-muted)' }}>
                      {m.label}
                    </div>
                    <div style={{ fontFamily: 'var(--font-display)', fontSize: '17px', fontWeight: 700, color: '#ffffff', marginTop: '4px' }}>
                      {m.val}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Slide Navigation Controls */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginTop: '18px',
              }}
            >
              <div style={{ display: 'flex', gap: '8px' }}>
                {mockDeckSlides.map((_, i) => (
                  <button
                    key={i}
                    onClick={() => setActiveSlideIndex(i)}
                    aria-label={`Slide ${i + 1}`}
                    style={{
                      height: '8px',
                      width: activeSlideIndex === i ? '28px' : '8px',
                      borderRadius: '4px',
                      backgroundColor: activeSlideIndex === i ? 'var(--accent-cyan)' : 'rgba(255, 255, 255, 0.2)',
                      border: 'none',
                      cursor: 'pointer',
                      transition: 'all 0.3s ease',
                    }}
                  />
                ))}
              </div>
              <span style={{ fontSize: '12px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>                  Click dots to see real deck aesthetics
              </span>
            </div>
          </div>

          {/* Service Capabilities Breakdown */}
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
                Included With Every Deck
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
              href={`mailto:${SITE_CONFIG.email}?subject=${encodeURIComponent('Inquiry: PowerPoint Presentation Design')}`}
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
