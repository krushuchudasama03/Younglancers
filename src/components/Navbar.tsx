import React, { useState, useEffect } from 'react';
import { Menu, X, ArrowUpRight, Sparkles } from 'lucide-react';

export const Navbar: React.FC = () => {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [activeSection, setActiveSection] = useState('home');

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 30);

      const sections = ['home', 'services', 'work', 'team', 'achievements', 'about', 'access', 'contact'];
      for (const sectionId of sections) {
        const el = document.getElementById(sectionId);
        if (el) {
          const rect = el.getBoundingClientRect();
          if (rect.top <= 200 && rect.bottom >= 200) {
            setActiveSection(sectionId);
            break;
          }
        }
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navLinks = [
    { name: 'Home', href: '#home', id: 'home' },
    { name: 'Services', href: '#services', id: 'services' },
    { name: 'Our Work', href: '#work', id: 'work' },
    { name: 'Team', href: '#team', id: 'team' },
    { name: 'Achievements', href: '#achievements', id: 'achievements' },
    { name: 'About', href: '#about', id: 'about' },
    { name: 'Access', href: '#access', id: 'access' },
    { name: 'Contact', href: '#contact', id: 'contact' },
  ];

  return (
    <header
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 100,
        transition: 'all 0.3s ease',
        padding: scrolled ? '14px 0' : '24px 0',
        backgroundColor: scrolled ? 'rgba(7, 8, 10, 0.85)' : 'transparent',
        backdropFilter: scrolled ? 'blur(16px)' : 'none',
        WebkitBackdropFilter: scrolled ? 'blur(16px)' : 'none',
        borderBottom: scrolled ? '1px solid rgba(255, 255, 255, 0.08)' : '1px solid transparent',
      }}
    >
      <div className="container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        {/* Brand Wordmark */}
        <a
          href="#home"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            textDecoration: 'none',
            color: '#ffffff',
          }}
        >
          <div
            style={{
              width: '32px',
              height: '32px',
              borderRadius: '8px',
              background: 'linear-gradient(135deg, #1e293b, #0f172a)',
              border: '1px solid rgba(56, 189, 248, 0.3)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Sparkles size={16} color="#38bdf8" />
          </div>
          <div>
            <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '16px', letterSpacing: '-0.02em' }}>
              Younglancers<span style={{ color: 'var(--accent-cyan)' }}>.</span>
            </div>
            <div style={{ fontSize: '10.5px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', marginTop: '-2px' }}>
              Young Creators Crew
            </div>
          </div>
        </a>

        {/* Desktop Navigation Links */}
        <nav
          style={{
            display: 'none',
            alignItems: 'center',
            gap: '6px',
            background: 'rgba(255, 255, 255, 0.03)',
            padding: '5px 8px',
            borderRadius: '9999px',
            border: '1px solid rgba(255, 255, 255, 0.08)',
          }}
          className="desktop-nav-menu"
        >
          <style>{`
            @media (min-width: 1080px) {
              .desktop-nav-menu { display: flex !important; }
              .mobile-toggle-btn { display: none !important; }
              .desktop-cta-btn { display: inline-flex !important; }
            }
          `}</style>
          {navLinks.map((link) => {
            const isActive = activeSection === link.id;
            return (
              <a
                key={link.id}
                href={link.href}
                style={{
                  textDecoration: 'none',
                  fontSize: '13px',
                  fontWeight: 500,
                  padding: '7px 15px',
                  borderRadius: '9999px',
                  color: isActive ? '#ffffff' : 'var(--text-secondary)',
                  backgroundColor: isActive ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
                  transition: 'all 0.2s ease',
                  position: 'relative',
                }}
              >
                {link.name}
              </a>
            );
          })}
        </nav>

        {/* Desktop Quick Action */}
        <div style={{ display: 'none', alignItems: 'center', gap: '14px' }} className="desktop-cta-btn">
          <a
            href="#contact"
            className="btn-primary"
            style={{
              padding: '9px 18px',
              fontSize: '13px',
              borderRadius: '9999px',
            }}
          >
            <span>Let's Talk</span>
            <ArrowUpRight size={14} />
          </a>
        </div>

        {/* Mobile Toggle Button */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="mobile-toggle-btn"
          aria-label="Toggle navigation menu"
          aria-expanded={mobileMenuOpen}
          style={{
            background: 'rgba(255, 255, 255, 0.06)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            color: '#ffffff',
            padding: '8px',
            borderRadius: '8px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div
          style={{
            position: 'absolute',
            top: '100%',
            left: 0,
            right: 0,
            backgroundColor: 'rgba(7, 8, 10, 0.98)',
            borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
            padding: '24px',
            display: 'flex',
            flexDirection: 'column',
            gap: '16px',
            backdropFilter: 'blur(20px)',
          }}
        >
          {navLinks.map((link) => (
            <a
              key={link.id}
              href={link.href}
              onClick={() => setMobileMenuOpen(false)}
              style={{
                textDecoration: 'none',
                color: '#f8fafc',
                fontSize: '16px',
                fontWeight: 500,
                padding: '8px 0',
                borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <span>{link.name}</span>
              <ArrowUpRight size={16} color="var(--text-muted)" />
            </a>
          ))}
          <div style={{ paddingTop: '8px' }}>
            <a
              href="#contact"
              onClick={() => setMobileMenuOpen(false)}
              className="btn-primary"
              style={{ width: '100%', boxSizing: 'border-box' }}
            >
              <span>Let's Talk</span>
              <ArrowUpRight size={16} />
            </a>
          </div>
        </div>
      )}
    </header>
  );
};
