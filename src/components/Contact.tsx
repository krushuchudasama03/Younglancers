import React, { useState } from 'react';
import { SITE_CONFIG } from '../config';
import { Mail, Copy, Check, Send, ArrowRight } from 'lucide-react';
import confetti from 'canvas-confetti';

export const Contact: React.FC = () => {
  const [copied, setCopied] = useState(false);
  const [selectedInquiry, setSelectedInquiry] = useState(SITE_CONFIG.inquiryOptions[0].id);
  const [customNote, setCustomNote] = useState('');

  const activeInquiryObj = SITE_CONFIG.inquiryOptions.find((o) => o.id === selectedInquiry) || SITE_CONFIG.inquiryOptions[0];

  const handleCopyEmail = () => {
    navigator.clipboard.writeText(SITE_CONFIG.email).then(() => {
      setCopied(true);
      confetti({
        particleCount: 40,
        spread: 60,
        origin: { y: 0.8 },
        colors: ['#38bdf8', '#ffffff', '#818cf8'],
      });
      setTimeout(() => setCopied(false), 2600);
    });
  };

  // Generate populated mailto link with pre-filled recipient and subject/body
  const generateMailtoUrl = () => {
    const subject = encodeURIComponent(`${activeInquiryObj.subject} — ${SITE_CONFIG.fullName}`);
    const bodyContent = `Hi Krushnrajsinh,

I came across your portfolio and would like to discuss a project with you.

Project Scope: ${activeInquiryObj.label}
Details / Requirements:
${customNote.trim() ? customNote : '[Please briefly describe your presentation or website needs here]'}

Looking forward to hearing from you!`;

    const body = encodeURIComponent(bodyContent);
    return `mailto:${SITE_CONFIG.email}?subject=${subject}&body=${body}`;
  };

  const handleOpenEmail = () => {
    const url = generateMailtoUrl();
    window.location.href = url;
  };

  return (
    <section id="contact" style={{ padding: '110px 0', borderTop: '1px solid var(--border-subtle)' }}>
      <div className="container">
        {/* Contact Header */}
        <div style={{ maxWidth: '820px', marginBottom: '56px' }}>
          <div className="kicker-badge" style={{ marginBottom: '16px' }}>
            <span className="kicker-dot" />
            <span>START A COLLABORATION</span>
          </div>
          <h2 style={{ fontSize: 'clamp(36px, 6vw, 68px)', color: '#ffffff', marginBottom: '20px' }}>
            Have an idea? Let's build it.
          </h2>
          <p style={{ fontSize: '19px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
            Tell me what you're working on. Whether you need a presentation or a website, let's discuss how I can help.
          </p>
        </div>

        {/* Contact Interaction Card */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            gap: '36px',
            alignItems: 'start',
          }}
        >
          {/* Main Direct Action Card */}
          <div
            className="glass-panel"
            style={{
              padding: '40px 36px',
              border: '1px solid var(--border-active)',
              boxShadow: '0 24px 60px rgba(0, 0, 0, 0.7)',
              position: 'relative',
              overflow: 'hidden',
            }}
          >
            {/* Top Badge */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                paddingBottom: '20px',
                marginBottom: '28px',
                borderBottom: '1px solid var(--border-subtle)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Mail size={18} color="var(--accent-cyan)" />
                <span style={{ fontSize: '13px', fontWeight: 600, color: '#ffffff' }}>
                  Direct Email Protocol
                </span>
              </div>
              <span
                style={{
                  fontSize: '11px',
                  fontFamily: 'var(--font-mono)',
                  color: 'var(--accent-emerald)',
                  background: 'rgba(16, 185, 129, 0.1)',
                  padding: '3px 8px',
                  borderRadius: '9999px',
                }}
              >
                Zero Middlemen
              </span>
            </div>

            {/* Inquiries Selector */}
            <div style={{ marginBottom: '24px' }}>
              <label
                style={{
                  display: 'block',
                  fontSize: '12px',
                  fontFamily: 'var(--font-mono)',
                  color: 'var(--accent-cyan)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.1em',
                  marginBottom: '12px',
                }}
              >
                1. Select Your Inquiry Discipline
              </label>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '8px' }}>
                {SITE_CONFIG.inquiryOptions.map((opt) => (
                  <button
                    key={opt.id}
                    onClick={() => setSelectedInquiry(opt.id)}
                    type="button"
                    style={{
                      padding: '10px 12px',
                      borderRadius: '8px',
                      fontSize: '12.5px',
                      fontWeight: 500,
                      cursor: 'pointer',
                      border: selectedInquiry === opt.id ? '1px solid var(--accent-cyan)' : '1px solid rgba(255, 255, 255, 0.08)',
                      backgroundColor: selectedInquiry === opt.id ? 'rgba(56, 189, 248, 0.12)' : 'rgba(255, 255, 255, 0.02)',
                      color: selectedInquiry === opt.id ? '#ffffff' : 'var(--text-secondary)',
                      transition: 'all 0.2s ease',
                      textAlign: 'left',
                    }}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Optional Project Brief Input */}
            <div style={{ marginBottom: '32px' }}>
              <label
                htmlFor="custom-note-input"
                style={{
                  display: 'block',
                  fontSize: '12px',
                  fontFamily: 'var(--font-mono)',
                  color: 'var(--text-muted)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.1em',
                  marginBottom: '10px',
                }}
              >
                2. Project Brief / Topic (Optional)
              </label>
              <textarea
                id="custom-note-input"
                rows={3}
                value={customNote}
                onChange={(e) => setCustomNote(e.target.value)}
                placeholder="E.g., 12-slide investor pitch deck for clean energy startup, or portfolio website with dark aesthetic..."
                style={{
                  width: '100%',
                  padding: '12px 14px',
                  borderRadius: '10px',
                  backgroundColor: 'rgba(255, 255, 255, 0.03)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  color: '#ffffff',
                  fontSize: '14px',
                  fontFamily: 'var(--font-sans)',
                  resize: 'vertical',
                  boxSizing: 'border-box',
                }}
              />
            </div>

            {/* User Requested: Prominent CONTACT ME button that immediately opens default email client with address pre-filled */}
            <div style={{ display: 'grid', gap: '14px', marginBottom: '28px' }}>
              <button
                onClick={handleOpenEmail}
                type="button"
                className="btn-primary"
                style={{
                  width: '100%',
                  padding: '16px 28px',
                  fontSize: '16px',
                  fontWeight: 700,
                  letterSpacing: '0.04em',
                  boxSizing: 'border-box',
                  background: 'linear-gradient(135deg, #ffffff 0%, #e2e8f0 100%)',
                  boxShadow: '0 8px 30px rgba(56, 189, 248, 0.25)',
                }}
              >
                <Send size={18} />
                <span>CONTACT ME</span>
                <ArrowRight size={18} />
              </button>
              <div
                style={{
                  fontSize: '12px',
                  color: 'var(--text-muted)',
                  textAlign: 'center',
                  fontFamily: 'var(--font-mono)',
                }}
              >
                ⚡ Instantly opens your email client with {SITE_CONFIG.email} pre-addressed.
              </div>
            </div>

            {/* Selectable Email Display & Copy Button */}
            <div
              style={{
                padding: '16px 20px',
                borderRadius: '12px',
                backgroundColor: 'rgba(255, 255, 255, 0.02)',
                border: '1px solid rgba(255, 255, 255, 0.06)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: '12px',
              }}
            >
              <div>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                  DIRECT ADDRESS
                </div>
                <div
                  style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: '15px',
                    color: '#ffffff',
                    fontWeight: 600,
                    userSelect: 'all',
                    marginTop: '2px',
                  }}
                >
                  {SITE_CONFIG.email}
                </div>
              </div>

              <button
                onClick={handleCopyEmail}
                type="button"
                className="btn-secondary"
                style={{
                  padding: '8px 16px',
                  fontSize: '13px',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '8px',
                }}
              >
                {copied ? <Check size={14} color="var(--accent-emerald)" /> : <Copy size={14} />}
                <span>{copied ? 'Copied to Clipboard!' : 'Copy Email'}</span>
              </button>
            </div>
          </div>

          {/* Right: Direct Collaboration Guarantees */}
          <div style={{ display: 'grid', gap: '20px' }}>
            <div
              style={{
                padding: '24px',
                borderRadius: '14px',
                backgroundColor: 'rgba(255, 255, 255, 0.02)',
                border: '1px solid rgba(255, 255, 255, 0.05)',
              }}
            >
              <h4 style={{ fontSize: '17px', color: '#ffffff', marginBottom: '8px' }}>
                Prompt Response Guarantee
              </h4>
              <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                Every email sent is answered directly by Krushnrajsinh within 12-24 hours. We can arrange a quick video or text brief to align on your presentation topics or website goals.
              </p>
            </div>

            <div
              style={{
                padding: '24px',
                borderRadius: '14px',
                backgroundColor: 'rgba(255, 255, 255, 0.02)',
                border: '1px solid rgba(255, 255, 255, 0.05)',
              }}
            >
              <h4 style={{ fontSize: '17px', color: '#ffffff', marginBottom: '8px' }}>
                Confidentiality & Content Privacy
              </h4>
              <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                Client data, business decks, financial metrics, and intellectual property remain 100% confidential. No materials are shared or published without explicit permission.
              </p>
            </div>

            <div
              style={{
                padding: '24px',
                borderRadius: '14px',
                backgroundColor: 'rgba(255, 255, 255, 0.02)',
                border: '1px solid rgba(255, 255, 255, 0.05)',
              }}
            >
              <h4 style={{ fontSize: '17px', color: '#ffffff', marginBottom: '8px' }}>
                Full Asset Handover
              </h4>
              <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                Upon delivery, you receive completely editable PowerPoint master files (.pptx), vector icons, and clean production GitHub repositories with total ownership.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
