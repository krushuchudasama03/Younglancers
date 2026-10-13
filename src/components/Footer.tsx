import React from 'react';
import { SITE_CONFIG } from '../config';
import { ArrowUp, Sparkles } from 'lucide-react';

export const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <footer
      style={{
        padding: '64px 0 40px 0',
        borderTop: '1px solid var(--border-subtle)',
        backgroundColor: '#050608',
      }}
    >
      <div className="container">
        {/* Main Footer Row */}
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            justifyContent: 'space-between',
            alignItems: 'flex-start',
            gap: '40px',
            marginBottom: '48px',
          }}
        >
          {/* Identity Info */}
          <div style={{ maxWidth: '420px' }}>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                fontFamily: 'var(--font-display)',
                fontWeight: 700,
                fontSize: '18px',
                color: '#ffffff',
                marginBottom: '10px',
              }}
            >
              <Sparkles size={16} color="var(--accent-cyan)" />
              <span>Younglancers</span>
            </div>
            <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '16px' }}>
              {SITE_CONFIG.professionalIdentity} — building with Krushnrajsinh, Rishi & Yuvi.
            </p>
            <div style={{ fontSize: '13px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
              Direct: <span style={{ color: 'var(--accent-cyan)' }}>{SITE_CONFIG.email}</span>
            </div>
          </div>

          {/* Quick Section Navigation Links */}
          <div style={{ display: 'flex', gap: '48px', flexWrap: 'wrap' }}>
            <div>
              <div
                style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: '11px',
                  color: 'var(--text-muted)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.12em',
                  marginBottom: '14px',
                }}
              >
                Navigation
              </div>
              <ul style={{ listStyle: 'none', display: 'grid', gap: '8px', padding: 0 }}>
                <li>
                  <a href="#home" style={{ color: 'var(--text-secondary)', textDecoration: 'none', fontSize: '14px' }}>
                    Home
                  </a>
                </li>
                <li>
                  <a href="#services-presentation" style={{ color: 'var(--text-secondary)', textDecoration: 'none', fontSize: '14px' }}>
                    PowerPoint Services
                  </a>
                </li>
                <li>
                  <a href="#services-web" style={{ color: 'var(--text-secondary)', textDecoration: 'none', fontSize: '14px' }}>
                    Website Services
                  </a>
                </li>
                <li>
                  <a href="#work" style={{ color: 'var(--text-secondary)', textDecoration: 'none', fontSize: '14px' }}>
                    Our Work
                  </a>
                </li>
                <li>
                  <a href="#team" style={{ color: 'var(--text-secondary)', textDecoration: 'none', fontSize: '14px' }}>
                    Team
                  </a>
                </li>
                <li>
                  <a href="#achievements" style={{ color: 'var(--text-secondary)', textDecoration: 'none', fontSize: '14px' }}>
                    Achievements
                  </a>
                </li>
                <li>
                  <a href="#about" style={{ color: 'var(--text-secondary)', textDecoration: 'none', fontSize: '14px' }}>
                    About
                  </a>
                </li>
                <li>
                  <a href="#access" style={{ color: 'var(--text-secondary)', textDecoration: 'none', fontSize: '14px' }}>
                    Member Access
                  </a>
                </li>
              </ul>
            </div>

            {/* Back to top trigger */}
            <div>
              <div
                style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: '11px',
                  color: 'var(--text-muted)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.12em',
                  marginBottom: '14px',
                }}
              >
                Back To Top
              </div>
              <button
                onClick={scrollToTop}
                aria-label="Scroll back to top of page"
                className="btn-secondary"
                style={{
                  padding: '10px 18px',
                  fontSize: '13px',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '8px',
                }}
              >
                <ArrowUp size={15} />
                <span>Return to Top</span>
              </button>
            </div>
          </div>
        </div>

        {/* Bottom Copyright & Disclaimer */}
        <div
          style={{
            paddingTop: '32px',
            borderTop: '1px solid rgba(255, 255, 255, 0.05)',
            display: 'flex',
            flexWrap: 'wrap',
            justifyContent: 'space-between',
            alignItems: 'center',
            gap: '16px',
            fontSize: '12.5px',
            color: 'var(--text-muted)',
            fontFamily: 'var(--font-mono)',
          }}
        >
          <div>
            © {currentYear} {SITE_CONFIG.brandName}. All rights reserved.
          </div>
          <div>
            Handcrafted with React, TypeScript & Canvas. Zero generic templates.
          </div>
        </div>
      </div>
    </footer>
  );
};
