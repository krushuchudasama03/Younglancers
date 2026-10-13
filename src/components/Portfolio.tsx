import React, { useState } from 'react';
import { SITE_CONFIG, type ProjectItem } from '../config';
import { Presentation, Globe, Terminal, ArrowUpRight, X, CheckCircle2, ExternalLink } from 'lucide-react';

export const Portfolio: React.FC = () => {
  const [activeFilter, setActiveFilter] = useState<'all' | 'presentation' | 'web'>('all');
  const [selectedProject, setSelectedProject] = useState<ProjectItem | null>(null);

  const filteredProjects = SITE_CONFIG.portfolio.filter((project) => {
    if (activeFilter === 'all') return true;
    return project.category === activeFilter;
  });

  const openDemo = (project: ProjectItem) => {
    window.open(project.demoUrl, '_blank', 'noopener,noreferrer');
  };

  const demoIcon = (p: ProjectItem) => {
    if (p.demoType === 'deck') return <Presentation size={16} color="var(--accent-cyan)" />;
    if (p.demoType === 'code') return <Terminal size={16} color="#10b981" />;
    return <Globe size={16} color="#818cf8" />;
  };

  const demoLabel = (p: ProjectItem) => {
    if (p.demoType === 'deck') return 'Show Deck Demo';
    if (p.demoType === 'code') return 'Show Source Demo';
    return 'Show Demo';
  };

  return (
    <section id="work" style={{ padding: '110px 0', borderTop: '1px solid var(--border-subtle)' }}>
      <div className="container">
        {/* Section Header with Filter Controls */}
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '24px',
            marginBottom: '54px',
          }}
        >
          <div style={{ maxWidth: '780px' }}>
            <div className="kicker-badge" style={{ marginBottom: '16px' }}>
              <span className="kicker-dot" />
              <span>REAL SHIPPED WORK • LIVE DEMOS</span>
            </div>
            <h2 style={{ fontSize: 'clamp(32px, 5vw, 56px)', color: '#ffffff', marginBottom: '18px' }}>
              Built by us. Running for real.
            </h2>
            <p style={{ fontSize: '18px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              No mockups here. Every card is a real Younglancers project — click "Show Demo" and{' '}
              <strong style={{ color: '#ffffff' }}>the actual product UI opens in a new tab</strong>, not a download.
            </p>
          </div>

          {/* Filter Pills */}
          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
            {(
              [
                ['all', `All Work (${SITE_CONFIG.portfolio.length})`],
                ['presentation', 'Presentations'],
                ['web', 'Web & Software'],
              ] as const
            ).map(([key, label]) => (
              <button
                key={key}
                onClick={() => setActiveFilter(key)}
                style={{
                  padding: '8px 18px',
                  borderRadius: '9999px',
                  fontSize: '13px',
                  fontWeight: 500,
                  cursor: 'pointer',
                  border: activeFilter === key ? '1px solid var(--accent-cyan)' : '1px solid var(--border-subtle)',
                  backgroundColor: activeFilter === key ? 'rgba(56, 189, 248, 0.12)' : 'rgba(255, 255, 255, 0.03)',
                  color: activeFilter === key ? '#ffffff' : 'var(--text-secondary)',
                  transition: 'all 0.2s ease',
                }}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* Project Cards Grid */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))',
            gap: '28px',
          }}
        >
          {filteredProjects.map((project) => {
            return (
              <div
                key={project.id}
                className="glass-panel"
                style={{
                  padding: '28px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  position: 'relative',
                  overflow: 'hidden',
                }}
              >
                {/* Visual Preview Shell */}
                <div
                  style={{
                    backgroundColor: '#0a0d14',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    borderRadius: '12px',
                    padding: '20px',
                    marginBottom: '22px',
                    minHeight: '180px',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    position: 'relative',
                    overflow: 'hidden',
                    cursor: 'pointer',
                  }}
                  onClick={() => setSelectedProject(project)}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      {demoIcon(project)}
                      <span
                        style={{
                          fontSize: '11px',
                          fontFamily: 'var(--font-mono)',
                          color:
                            project.demoType === 'deck'
                              ? 'var(--accent-cyan)'
                              : project.demoType === 'code'
                                ? '#10b981'
                                : '#818cf8',
                        }}
                      >
                        {project.badge}
                      </span>
                    </div>
                    <ExternalLink size={16} color="var(--text-muted)" />
                  </div>

                  <div style={{ marginTop: '24px' }}>
                    <div
                      style={{
                        fontFamily: 'var(--font-display)',
                        fontSize: '18px',
                        fontWeight: 700,
                        color: '#ffffff',
                        lineHeight: 1.3,
                      }}
                    >
                      {project.title}
                    </div>
                    <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '8px' }}>
                      {project.tags.join(' • ')}
                    </div>
                  </div>
                </div>

                {/* Card Details */}
                <div style={{ display: 'flex', flexDirection: 'column', flexGrow: 1 }}>
                  <p style={{ fontSize: '14.5px', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '20px' }}>
                    {project.description}
                  </p>

                  {/* Highlights */}
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '22px' }}>
                    {project.features.map((f, i) => (
                      <span
                        key={i}
                        style={{
                          fontSize: '11.5px',
                          color: 'var(--text-muted)',
                          background: 'rgba(255, 255, 255, 0.04)',
                          padding: '3px 10px',
                          borderRadius: '6px',
                          border: '1px solid rgba(255, 255, 255, 0.05)',
                        }}
                      >
                        {f}
                      </span>
                    ))}
                  </div>

                  {/* THE KEY ACTION: Show Demo opens the real UI in a new tab */}
                  <div
                    style={{
                      display: 'flex',
                      gap: '12px',
                      alignItems: 'center',
                      marginTop: 'auto',
                      paddingTop: '16px',
                      borderTop: '1px solid var(--border-subtle)',
                    }}
                  >
                    <button
                      onClick={() => openDemo(project)}
                      className="btn-primary"
                      style={{ padding: '11px 22px', fontSize: '13.5px' }}
                    >
                      <span>{demoLabel(project)}</span>
                      <ExternalLink size={14} />
                    </button>
                    <button
                      onClick={() => setSelectedProject(project)}
                      className="btn-secondary"
                      style={{ padding: '11px 18px', fontSize: '13px' }}
                    >
                      <span>Details</span>
                      <ArrowUpRight size={14} />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Footnote */}
        <div
          style={{
            marginTop: '36px',
            padding: '18px 24px',
            borderRadius: '12px',
            background: 'rgba(255, 255, 255, 0.02)',
            border: '1px solid rgba(255, 255, 255, 0.05)',
            fontSize: '13px',
            color: 'var(--text-secondary)',
            lineHeight: 1.6,
          }}
        >
          Every demo file ships inside{' '}
          <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-cyan)' }}>public/demos/</span> in this{' '}
          repository — so the demos work offline, on GitHub Pages, and on any mirror. No external hosting, no
          Signup-needed services, no surprises.
        </div>
      </div>

      {/* Project Details Modal */}
      {selectedProject && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.85)',
            backdropFilter: 'blur(16px)',
            zIndex: 200,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '24px',
          }}
          onClick={() => setSelectedProject(null)}
        >
          <div
            className="glass-panel"
            style={{
              maxWidth: '800px',
              width: '100%',
              maxHeight: '90vh',
              overflowY: 'auto',
              padding: '36px',
              position: 'relative',
              backgroundColor: '#0c0f16',
              border: '1px solid var(--border-active)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Close Button */}
            <button
              onClick={() => setSelectedProject(null)}
              aria-label="Close modal"
              style={{
                position: 'absolute',
                top: '24px',
                right: '24px',
                background: 'rgba(255, 255, 255, 0.08)',
                border: 'none',
                color: '#ffffff',
                padding: '8px',
                borderRadius: '50%',
                cursor: 'pointer',
              }}
            >
              <X size={20} />
            </button>

            <div style={{ marginBottom: '24px' }}>
              <div className="kicker-badge" style={{ marginBottom: '12px' }}>
                <span className="kicker-dot" />
                <span>{selectedProject.badge}</span>
              </div>
              <h3 style={{ fontSize: '28px', color: '#ffffff', marginBottom: '12px' }}>{selectedProject.title}</h3>
              <p style={{ fontSize: '16px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                {selectedProject.description}
              </p>
            </div>

            {/* Slides Preview if presentation */}
            {selectedProject.slides && (
              <div style={{ marginBottom: '28px' }}>
                <div
                  style={{
                    fontSize: '12px',
                    fontFamily: 'var(--font-mono)',
                    color: 'var(--accent-cyan)',
                    textTransform: 'uppercase',
                    letterSpacing: '0.1em',
                    marginBottom: '14px',
                  }}
                >
                  Deck Slide Flow Demonstration
                </div>
                <div style={{ display: 'grid', gap: '14px' }}>
                  {selectedProject.slides.map((s) => (
                    <div
                      key={s.slideNumber}
                      style={{
                        padding: '16px 20px',
                        borderRadius: '10px',
                        background: 'rgba(255, 255, 255, 0.03)',
                        border: '1px solid rgba(255, 255, 255, 0.07)',
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                        <span style={{ fontSize: '14px', fontWeight: 600, color: '#ffffff' }}>
                          Slide {s.slideNumber}: {s.title}
                        </span>
                        <span style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                          {s.layout}
                        </span>
                      </div>
                      <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                        {s.subtitle}
                      </p>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                        {s.highlights.map((h, i) => (
                          <span
                            key={i}
                            style={{
                              fontSize: '11px',
                              color: 'var(--accent-cyan)',
                              background: 'rgba(56, 189, 248, 0.08)',
                              padding: '2px 8px',
                              borderRadius: '4px',
                            }}
                          >
                            {h}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Browser Preview Details if web */}
            {selectedProject.browserPreview && (
              <div style={{ marginBottom: '28px' }}>
                <div
                  style={{
                    fontSize: '12px',
                    fontFamily: 'var(--font-mono)',
                    color: 'var(--accent-cyan)',
                    textTransform: 'uppercase',
                    letterSpacing: '0.1em',
                    marginBottom: '14px',
                  }}
                >
                  Product Surface Specifications
                </div>
                <div
                  style={{
                    padding: '20px',
                    borderRadius: '10px',
                    background: 'rgba(255, 255, 255, 0.03)',
                    border: '1px solid rgba(255, 255, 255, 0.07)',
                  }}
                >
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: '#818cf8', marginBottom: '8px' }}>
                    Live Endpoint Preview: {selectedProject.browserPreview.url}
                  </div>
                  <h4 style={{ fontSize: '18px', color: '#ffffff', marginBottom: '6px' }}>
                    {selectedProject.browserPreview.headline}
                  </h4>
                  <p style={{ fontSize: '13.5px', color: 'var(--text-secondary)', marginBottom: '12px' }}>
                    {selectedProject.browserPreview.subheadline}
                  </p>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {selectedProject.browserPreview.highlights.map((h, i) => (
                      <span
                        key={i}
                        style={{
                          fontSize: '11.5px',
                          color: '#818cf8',
                          background: 'rgba(129, 140, 248, 0.1)',
                          padding: '3px 10px',
                          borderRadius: '4px',
                        }}
                      >
                        {h}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Deliverables handover */}
            <div style={{ marginBottom: '28px' }}>
              <div
                style={{
                  fontSize: '12px',
                  fontFamily: 'var(--font-mono)',
                  color: 'var(--accent-cyan)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.1em',
                  marginBottom: '12px',
                }}
              >
                Included In The Repo
              </div>
              <div style={{ display: 'grid', gap: '8px' }}>
                {selectedProject.deliverables.map((d, i) => (
                  <div
                    key={i}
                    style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '13.5px', color: 'var(--text-secondary)' }}
                  >
                    <CheckCircle2 size={15} color="var(--accent-cyan)" />
                    <span>{d}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Modal Action CTAs */}
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
              <button
                onClick={() => setSelectedProject(null)}
                className="btn-secondary"
                style={{ padding: '10px 20px', fontSize: '13.5px' }}
              >
                Close
              </button>
              <button
                onClick={() => openDemo(selectedProject)}
                className="btn-primary"
                style={{ padding: '10px 20px', fontSize: '13.5px' }}
              >
                <span>Open Real Demo</span>
                <ExternalLink size={14} />
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
};
