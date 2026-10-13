import React, { useEffect, useState } from 'react';
import { InteractiveThreads } from './components/InteractiveThreads';
import { Navbar } from './components/Navbar';
import { Hero } from './components/Hero';
import { PresentationService } from './components/PresentationService';
import { WebsiteService } from './components/WebsiteService';
import { Portfolio } from './components/Portfolio';
import { Team } from './components/Team';
import { Achievements } from './components/Achievements';
import { About } from './components/About';
import { Portal } from './components/Portal';
import { Contact } from './components/Contact';
import { Footer } from './components/Footer';

export const App: React.FC = () => {
  const [scrollProgress, setScrollProgress] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      const totalScroll = document.documentElement.scrollHeight - window.innerHeight;
      if (totalScroll > 0) {
        const currentProgress = (window.scrollY / totalScroll) * 100;
        setScrollProgress(currentProgress);
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div style={{ position: 'relative', minHeight: '100vh', backgroundColor: 'var(--bg-primary)' }}>
      {/* Scroll Progress Indicator Bar */}
      <div
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          height: '2.5px',
          width: `${scrollProgress}%`,
          backgroundColor: 'var(--accent-cyan)',
          zIndex: 1000,
          transition: 'width 0.1s ease-out',
        }}
        aria-hidden="true"
      />

      {/* Signature Interactive Cursor Thread Canvas */}
      <InteractiveThreads />

      {/* Navigation */}
      <Navbar />

      {/* Main Content Sections — clearly segregated */}
      <main style={{ position: 'relative', zIndex: 1 }}>
        <Hero />
        <div id="services">
          <PresentationService />
          <WebsiteService />
        </div>
        <Portfolio />
        <Team />
        <Achievements />
        <About />
        <Portal />
        <Contact />
      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
};

export default App;
