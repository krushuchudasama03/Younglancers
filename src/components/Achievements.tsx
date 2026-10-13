import React from 'react';
import { SITE_CONFIG } from '../config';
import { Trophy, CheckCircle } from 'lucide-react';

export const Achievements: React.FC = () => {
  return (
    <section id="achievements" style={{ padding: '100px 0', borderTop: '1px solid var(--border-subtle)' }}>
      <div className="container">
        {/* Header */}
        <div style={{ maxWidth: '820px', marginBottom: '56px' }}>
          <div className="kicker-badge" style={{ marginBottom: '16px' }}>
            <span className="kicker-dot" />
            <span>COMPETITIONS & DISTINCTIONS</span>
          </div>
          <h2 style={{ fontSize: 'clamp(32px, 5vw, 56px)', color: '#ffffff', marginBottom: '18px' }}>
            Honors & Track Record.
          </h2>
          <p style={{ fontSize: '18px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
            Demonstrated excellence in regional robotics engineering, competitive parliamentary debate, and Model United Nations diplomacy at age {SITE_CONFIG.age}.
          </p>
        </div>

        {/* Achievements Grid */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            gap: '24px',
          }}
        >
          {SITE_CONFIG.achievements.map((item) => {
            const isRobotics = item.category === 'Robotics & STEM';
            const iconColor = isRobotics ? 'var(--accent-cyan)' : '#818cf8';

            return (
              <div
                key={item.id}
                className="glass-panel"
                style={{
                  padding: '32px 28px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  position: 'relative',
                  overflow: 'hidden',
                }}
              >
                <div>
                  {/* Category Pill and Year */}
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      marginBottom: '20px',
                    }}
                  >
                    <div
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '6px',
                        padding: '4px 10px',
                        borderRadius: '9999px',
                        background: 'rgba(255, 255, 255, 0.05)',
                        border: '1px solid rgba(255, 255, 255, 0.08)',
                        fontSize: '11px',
                        fontFamily: 'var(--font-mono)',
                        color: iconColor,
                      }}
                    >
                      <Trophy size={13} color={iconColor} />
                      <span>{item.badge}</span>
                    </div>
                    <span
                      style={{
                        fontFamily: 'var(--font-mono)',
                        fontSize: '12px',
                        color: 'var(--text-muted)',
                      }}
                    >
                      {item.year}
                    </span>
                  </div>

                  {/* Title and Organization */}
                  <h3
                    style={{
                      fontSize: '22px',
                      color: '#ffffff',
                      marginBottom: '8px',
                      lineHeight: 1.3,
                    }}
                  >
                    {item.title}
                  </h3>
                  <div
                    style={{
                      fontSize: '13px',
                      fontFamily: 'var(--font-mono)',
                      color: 'var(--text-muted)',
                      marginBottom: '16px',
                    }}
                  >
                    {item.organization}
                  </div>

                  {/* Description */}
                  <p
                    style={{
                      fontSize: '14.5px',
                      color: 'var(--text-secondary)',
                      lineHeight: 1.6,
                      marginBottom: '20px',
                    }}
                  >
                    {item.description}
                  </p>
                </div>

                {/* Significance Footer */}
                <div
                  style={{
                    paddingTop: '16px',
                    borderTop: '1px solid var(--border-subtle)',
                    fontSize: '13px',
                    color: 'var(--text-secondary)',
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '8px',
                  }}
                >
                  <CheckCircle size={15} color={iconColor} style={{ marginTop: '2px', flexShrink: 0 }} />
                  <span>
                    <strong style={{ color: '#ffffff' }}>Demonstrated skill:</strong> {item.significance}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};
