import React from 'react';
import { SITE_CONFIG } from '../config';

export const About: React.FC = () => {
  return (
    <section id="about" style={{ padding: '100px 0', borderTop: '1px solid var(--border-subtle)' }}>
      <div className="container">
        {/* Section Header */}
        <div style={{ maxWidth: '820px', marginBottom: '56px' }}>
          <div className="kicker-badge" style={{ marginBottom: '16px' }}>
            <span className="kicker-dot" />
            <span>DISCIPLINE & IDENTITY</span>
          </div>
          <h2 style={{ fontSize: 'clamp(32px, 5vw, 56px)', color: '#ffffff', marginBottom: '24px' }}>
            Who is Younglancers?
          </h2>
        </div>

        {/* Core Narrative Manifesto */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            gap: '48px',
            alignItems: 'start',
            marginBottom: '72px',
          }}
        >
          {/* Left: Main Personal Introduction (Exact words from prompt) */}
          <div
            className="glass-panel"
            style={{
              padding: '40px 36px',
              border: '1px solid var(--border-active)',
              position: 'relative',
            }}
          >
            <div
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '11px',
                color: 'var(--accent-cyan)',
                textTransform: 'uppercase',
                letterSpacing: '0.12em',
                marginBottom: '18px',
              }}
            >
              Younglancers • A Team Of Young Creators
            </div>

            <p
              style={{
                fontSize: 'clamp(18px, 2.2vw, 22px)',
                color: '#ffffff',
                lineHeight: 1.6,
                fontWeight: 500,
                marginBottom: '24px',
              }}
            >
              "Younglancers is a team of young makers led by Krushnrajsinh, our Co-Founder & Chief Website Developer — who also holds real expertise in PPT design. Rishi and Yuvi run presentation design, with Rishi also emerging in coding."
            </p>

            <p
              style={{
                fontSize: '16px',
                color: 'var(--text-secondary)',
                lineHeight: 1.7,
              }}
            >
              "Everything shown on this site is work we actually built — Sentinel Shield / Cyber Shield, the JARVIS visualization system, and the real decks. We care about the details that make the final result feel complete."
            </p>

            {/* Spec Tag row */}
            <div
              style={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: '10px',
                marginTop: '32px',
                paddingTop: '24px',
                borderTop: '1px solid var(--border-subtle)',
              }}
            >
              <span style={{ fontSize: '12px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                Real Product Demos
              </span>
              <span style={{ color: 'var(--border-hover)' }}>•</span>
              <span style={{ fontSize: '12px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                Website Dev / PPT Design
              </span>
              <span style={{ color: 'var(--border-hover)' }}>•</span>
              <span style={{ fontSize: '12px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                Direct 1-on-1 Turnaround
              </span>
            </div>
          </div>

          {/* Right: Working Principles Grid */}
          <div style={{ display: 'grid', gap: '20px' }}>
            {SITE_CONFIG.about.philosophyPoints.map((item) => (
              <div
                key={item.num}
                style={{
                  display: 'flex',
                  gap: '20px',
                  padding: '20px',
                  borderRadius: '12px',
                  background: 'rgba(255, 255, 255, 0.02)',
                  border: '1px solid rgba(255, 255, 255, 0.05)',
                }}
              >
                <div
                  style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: '15px',
                    fontWeight: 700,
                    color: 'var(--accent-cyan)',
                    paddingTop: '2px',
                  }}
                >
                  {item.num}
                </div>
                <div>
                  <h4 style={{ fontSize: '17px', color: '#ffffff', marginBottom: '6px' }}>{item.title}</h4>
                  <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};
