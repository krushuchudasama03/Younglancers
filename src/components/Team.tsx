import React from 'react';
import { SITE_CONFIG } from '../config';
import { Code2, Presentation, Sparkles } from 'lucide-react';

const ACCENTS = {
  cyan: { color: '#38bdf8', bg: 'rgba(56, 189, 248, 0.1)', border: 'rgba(56, 189, 248, 0.25)' },
  indigo: { color: '#818cf8', bg: 'rgba(129, 140, 248, 0.12)', border: 'rgba(129, 140, 248, 0.25)' },
  emerald: { color: '#10b981', bg: 'rgba(16, 185, 129, 0.12)', border: 'rgba(16, 185, 129, 0.25)' },
} as const;

export const Team: React.FC = () => {
  return (
    <section id="team" style={{ padding: '100px 0', borderTop: '1px solid var(--border-subtle)' }}>
      <div className="container">
        {/* Section Header */}
        <div style={{ maxWidth: '820px', marginBottom: '56px' }}>
          <div className="kicker-badge" style={{ marginBottom: '16px' }}>
            <span className="kicker-dot" />
            <span>THE YOUNGLANCERS CREW</span>
          </div>
          <h2 style={{ fontSize: 'clamp(32px, 5vw, 56px)', color: '#ffffff', marginBottom: '20px' }}>
            Small team. Clear roles.
          </h2>
          <p style={{ fontSize: '18px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
            Three young creators with segregated responsibilities — websites, security software, and presentation
            design. Here is exactly who does what.
          </p>
        </div>

        {/* Members Grid */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '24px',
          }}
        >
          {SITE_CONFIG.team.map((member, idx) => {
            const accent = ACCENTS[member.accent];
            const Icon = member.icon === 'code' ? Code2 : Presentation;
            return (
              <div
                key={member.id}
                className="glass-panel"
                style={{
                  padding: '30px 28px',
                  display: 'flex',
                  flexDirection: 'column',
                  position: 'relative',
                  overflow: 'hidden',
                }}
              >
                {/* Member rank marker — subtle, not RGB */}
                <div
                  style={{
                    position: 'absolute',
                    top: '-36px',
                    right: '-30px',
                    width: '140px',
                    height: '140px',
                    borderRadius: '50%',
                    background: accent.color,
                    opacity: 0.05,
                    filter: 'blur(36px)',
                    pointerEvents: 'none',
                  }}
                />

                <div
                  style={{
                    width: '44px',
                    height: '44px',
                    borderRadius: '12px',
                    background: accent.bg,
                    border: `1px solid ${accent.border}`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    marginBottom: '18px',
                  }}
                >
                  {member.icon === 'code' ? <Icon size={22} color={accent.color} /> : <Icon size={22} color={accent.color} />}
                </div>

                <div
                  style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: '11px',
                    color: accent.color,
                    textTransform: 'uppercase',
                    letterSpacing: '0.1em',
                    marginBottom: '6px',
                  }}
                >
                  Member {String(idx + 1).padStart(2, '0')}
                </div>

                <h3 style={{ fontSize: '20px', color: '#ffffff', marginBottom: '4px' }}>{member.name}</h3>
                <div
                  style={{
                    fontSize: '13px',
                    fontWeight: 600,
                    color: accent.color,
                    marginBottom: '8px',
                  }}
                >
                  {member.role}
                </div>
                <div style={{ fontSize: '13px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', marginBottom: '14px' }}>
                  {member.headline}
                </div>
                <p
                  style={{
                    fontSize: '14px',
                    color: 'var(--text-secondary)',
                    lineHeight: 1.65,
                    marginBottom: '20px',
                    flexGrow: 1,
                  }}
                >
                  {member.bio}
                </p>

                {/* Skill tags */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {member.skills.map((skill, i) => (
                    <span
                      key={i}
                      style={{
                        fontSize: '11.5px',
                        color: 'var(--text-secondary)',
                        background: 'rgba(255, 255, 255, 0.04)',
                        border: '1px solid rgba(255, 255, 255, 0.06)',
                        padding: '3px 10px',
                        borderRadius: '6px',
                      }}
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            );
          })}
        </div>

        {/* Team footnote */}
        <div
          style={{
            marginTop: '32px',
            padding: '18px 24px',
            borderRadius: '12px',
            background: 'rgba(255, 255, 255, 0.02)',
            border: '1px solid rgba(255, 255, 255, 0.05)',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            fontSize: '13.5px',
            color: 'var(--text-secondary)',
          }}
        >
          <Sparkles size={16} color="#38bdf8" />
          <span>
            Want a deck from <strong style={{ color: '#ffffff' }}>Rishi</strong> or{' '}
            <strong style={{ color: '#ffffff' }}>Yuvi</strong>, or a website from{' '}
            <strong style={{ color: '#ffffff' }}>Krushnrajsinh</strong>? Head to{' '}
            <a href="#contact" style={{ color: 'var(--accent-cyan)', textDecoration: 'none' }}>
              Contact
            </a>{' '}
            and pick your scope.
          </span>
        </div>
      </div>
    </section>
  );
};
