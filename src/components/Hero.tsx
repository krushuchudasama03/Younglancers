import React, { useState } from 'react';
import { SITE_CONFIG } from '../config';
import { ArrowRight, Code2, Award, Users } from 'lucide-react';

export const Hero: React.FC = () => {
  const [hoveredCard, setHoveredCard] = useState<number | null>(null);

  return (
    <section
      id="home"
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        paddingTop: '130px',
        paddingBottom: '80px',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      <div className="container" style={{ width: '100%' }}>
        {/* Availability Badge */}
        <div style={{ marginBottom: '28px' }}>
          <div className="kicker-badge">
            <span className="kicker-dot" />
            <span>{SITE_CONFIG.hero.kicker}</span>
            <span style={{ color: 'rgba(255, 255, 255, 0.2)', margin: '0 4px' }}>•</span>
            <span style={{ color: 'var(--text-secondary)' }}>{SITE_CONFIG.availabilityText}</span>
          </div>
        </div>

        {/* Hero Main Typography Grid */}
        <div style={{ maxWidth: '1020px' }}>
          <h1
            style={{
              fontSize: 'clamp(42px, 7.5vw, 92px)',
              fontWeight: 800,
              letterSpacing: '-0.04em',
              lineHeight: 1.05,
              color: '#ffffff',
              marginBottom: '32px',
            }}
          >
            <span style={{ display: 'block' }}>{SITE_CONFIG.hero.headingLine1}</span>
            <span
              style={{
                display: 'block',
                background: 'linear-gradient(135deg, #ffffff 40%, rgba(148, 163, 184, 0.65) 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              {SITE_CONFIG.hero.headingLine2}
            </span>
          </h1>

          <p
            style={{
              fontSize: 'clamp(17px, 2vw, 21px)',
              lineHeight: 1.6,
              color: 'var(--text-secondary)',
              maxWidth: '740px',
              marginBottom: '42px',
              fontWeight: 400,
            }}
          >
            {SITE_CONFIG.hero.supportingText}
          </p>

          {/* Action CTAs */}
          <div
            style={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: '16px',
              alignItems: 'center',
              marginBottom: '64px',
            }}
          >
            <a href="#contact" className="btn-primary">
              <span>{SITE_CONFIG.hero.primaryCta}</span>
              <ArrowRight size={16} />
            </a>
            <a href="#work" className="btn-secondary">
              <span>{SITE_CONFIG.hero.secondaryCta}</span>
            </a>
          </div>
        </div>

        {/* Dynamic Service & Credibility Cards */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(290px, 1fr))',
            gap: '20px',
            marginTop: '20px',
          }}
        >
          {/* Card 1: The Team */}
          <div
            className="glass-panel"
            onMouseEnter={() => setHoveredCard(1)}
            onMouseLeave={() => setHoveredCard(null)}
            style={{
              padding: '28px',
              position: 'relative',
              overflow: 'hidden',
              transform: hoveredCard === 1 ? 'translateY(-4px)' : 'none',
              borderColor: hoveredCard === 1 ? 'var(--border-active)' : 'var(--border-subtle)',
            }}
          >
            <div
              style={{
                width: '44px',
                height: '44px',
                borderRadius: '12px',
                background: 'rgba(56, 189, 248, 0.1)',
                border: '1px solid rgba(56, 189, 248, 0.25)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '18px',
              }}
            >
              <Users size={22} color="#38bdf8" />
            </div>
            <div
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '11px',
                color: 'var(--accent-cyan)',
                textTransform: 'uppercase',
                letterSpacing: '0.1em',
                marginBottom: '6px',
              }}
            >
              Service Crew 01
            </div>
            <h3 style={{ fontSize: '20px', color: '#ffffff', marginBottom: '10px' }}>
              Website Development
            </h3>
            <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              Led by our Co-Founder & Chief Website Developer, Krushnrajsinh — bespoke interfaces and shipped products.
            </p>
          </div>

          {/* Card 2: Website Development */}
          <div
            className="glass-panel"
            onMouseEnter={() => setHoveredCard(2)}
            onMouseLeave={() => setHoveredCard(null)}
            style={{
              padding: '28px',
              position: 'relative',
              overflow: 'hidden',
              transform: hoveredCard === 2 ? 'translateY(-4px)' : 'none',
              borderColor: hoveredCard === 2 ? 'var(--border-active)' : 'var(--border-subtle)',
            }}
          >
            <div
              style={{
                width: '44px',
                height: '44px',
                borderRadius: '12px',
                background: 'rgba(99, 102, 241, 0.12)',
                border: '1px solid rgba(99, 102, 241, 0.25)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '18px',
              }}
            >
              <Code2 size={22} color="#818cf8" />
            </div>
            <div
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '11px',
                color: '#818cf8',
                textTransform: 'uppercase',
                letterSpacing: '0.1em',
                marginBottom: '6px',
              }}
            >
              Service Crew 02
            </div>
            <h3 style={{ fontSize: '20px', color: '#ffffff', marginBottom: '10px' }}>
              Presentation Design
            </h3>
            <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              Rishi & Yuvi craft the decks — with PPT expertise from Krushnrajsinh backing every narrative structure.
            </p>
          </div>

          {/* Card 3: Honors & Competitions */}
          <div
            className="glass-panel"
            onMouseEnter={() => setHoveredCard(3)}
            onMouseLeave={() => setHoveredCard(null)}
            style={{
              padding: '28px',
              position: 'relative',
              overflow: 'hidden',
              transform: hoveredCard === 3 ? 'translateY(-4px)' : 'none',
              borderColor: hoveredCard === 3 ? 'rgba(16, 185, 129, 0.4)' : 'var(--border-subtle)',
            }}
          >
            <div
              style={{
                width: '44px',
                height: '44px',
                borderRadius: '12px',
                background: 'rgba(16, 185, 129, 0.12)',
                border: '1px solid rgba(16, 185, 129, 0.25)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '18px',
              }}
            >
              <Award size={22} color="#10b981" />
            </div>
            <div
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '11px',
                color: '#10b981',
                textTransform: 'uppercase',
                letterSpacing: '0.1em',
                marginBottom: '6px',
              }}
            >
              Track Record & Honors
            </div>
            <h3 style={{ fontSize: '20px', color: '#ffffff', marginBottom: '10px' }}>
              Robotics Winner & MUN Delegate
            </h3>
            <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              WSRO Regional Winner, Sahodaya Debate distinction, and high-impact Model UN diplomacy.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};
