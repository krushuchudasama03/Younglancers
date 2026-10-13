import React, { useEffect, useRef } from 'react';

interface Particle {
  x: number;
  y: number;
  originX: number;
  originY: number;
  vx: number;
  vy: number;
  radius: number;
  baseRadius: number;
  density: number;
  phase: number;
}

export const InteractiveThreads: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d', { alpha: true });
    if (!ctx) return;

    // Check user preference for reduced motion
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    let animationFrameId: number;
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    // Mouse coordinates and state
    const mouse = {
      x: -1000,
      y: -1000,
      radius: 170, // Interaction radius
      isActive: false
    };

    // Calculate particle count depending on viewport area & mobile check
    const isMobile = window.innerWidth < 768;
    const baseCount = isMobile ? 38 : 72;
    const connectionDistance = isMobile ? 110 : 160;

    let particles: Particle[] = [];

    const initParticles = () => {
      particles = [];
      for (let i = 0; i < baseCount; i++) {
        const x = Math.random() * width;
        const y = Math.random() * height;
        const baseRadius = Math.random() * 1.5 + 1.0;
        particles.push({
          x,
          y,
          originX: x,
          originY: y,
          vx: (Math.random() - 0.5) * 0.45,
          vy: (Math.random() - 0.5) * 0.45,
          radius: baseRadius,
          baseRadius,
          density: Math.random() * 25 + 15,
          phase: Math.random() * Math.PI * 2
        });
      }
    };

    initParticles();

    // Resize handler with debounce / RAF
    const handleResize = () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
      initParticles();
    };

    window.addEventListener('resize', handleResize, { passive: true });

    // Mouse listeners
    const handleMouseMove = (e: MouseEvent) => {
      mouse.x = e.clientX;
      mouse.y = e.clientY;
      mouse.isActive = true;
    };

    const handleMouseLeave = () => {
      mouse.x = -1000;
      mouse.y = -1000;
      mouse.isActive = false;
    };

    // Touch support for tablets/mobile with subtle displacement
    const handleTouchMove = (e: TouchEvent) => {
      if (e.touches.length > 0) {
        mouse.x = e.touches[0].clientX;
        mouse.y = e.touches[0].clientY;
        mouse.isActive = true;
      }
    };

    const handleTouchEnd = () => {
      mouse.x = -1000;
      mouse.y = -1000;
      mouse.isActive = false;
    };

    window.addEventListener('mousemove', handleMouseMove, { passive: true });
    window.addEventListener('mouseleave', handleMouseLeave, { passive: true });
    window.addEventListener('touchmove', handleTouchMove, { passive: true });
    window.addEventListener('touchend', handleTouchEnd, { passive: true });

    let lastTime = performance.now();

    const render = (time: number) => {
      const delta = Math.min((time - lastTime) / 1000, 0.1);
      lastTime = time;

      ctx.clearRect(0, 0, width, height);

      // If user prefers reduced motion, draw static elegant web
      if (prefersReducedMotion) {
        for (let i = 0; i < particles.length; i++) {
          const p = particles[i];
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
          ctx.fillStyle = 'rgba(56, 189, 248, 0.25)';
          ctx.fill();

          for (let j = i + 1; j < particles.length; j++) {
            const p2 = particles[j];
            const dx = p.x - p2.x;
            const dy = p.y - p2.y;
            const dist = Math.hypot(dx, dy);
            if (dist < connectionDistance) {
              ctx.beginPath();
              ctx.moveTo(p.x, p.y);
              ctx.lineTo(p2.x, p2.y);
              ctx.strokeStyle = `rgba(56, 189, 248, ${0.12 * (1 - dist / connectionDistance)})`;
              ctx.lineWidth = 0.75;
              ctx.stroke();
            }
          }
        }
        return;
      }

      // Dynamic animation step
      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];

        // Organic ambient sway
        p.phase += delta * 0.8;
        const swayX = Math.cos(p.phase) * 0.2;
        const swayY = Math.sin(p.phase) * 0.2;

        p.x += p.vx + swayX;
        p.y += p.vy + swayY;

        // Bounce gently off boundaries
        if (p.x < 0) {
          p.x = 0;
          p.vx = -p.vx;
        } else if (p.x > width) {
          p.x = width;
          p.vx = -p.vx;
        }

        if (p.y < 0) {
          p.y = 0;
          p.vy = -p.vy;
        } else if (p.y > height) {
          p.y = height;
          p.vy = -p.vy;
        }

        // Mouse displacement & inertia
        if (mouse.isActive) {
          const dx = mouse.x - p.x;
          const dy = mouse.y - p.y;
          const distance = Math.hypot(dx, dy);

          if (distance < mouse.radius) {
            const forceDirectionX = dx / distance;
            const forceDirectionY = dy / distance;
            const maxDistance = mouse.radius;
            const force = (maxDistance - distance) / maxDistance;
            // Repel / fluid warp effect
            const directionX = forceDirectionX * force * p.density * 0.8;
            const directionY = forceDirectionY * force * p.density * 0.8;

            p.x -= directionX * 0.15;
            p.y -= directionY * 0.15;
            p.radius = p.baseRadius * (1 + force * 0.9);
          } else {
            p.radius += (p.baseRadius - p.radius) * 0.05;
          }
        } else {
          p.radius += (p.baseRadius - p.radius) * 0.05;
        }

        // Draw particle node
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(56, 189, 248, 0.4)';
        ctx.fill();

        // Connect threads between neighboring points
        for (let j = i + 1; j < particles.length; j++) {
          const p2 = particles[j];
          const dx = p.x - p2.x;
          const dy = p.y - p2.y;
          const dist = Math.hypot(dx, dy);

          if (dist < connectionDistance) {
            // Factor in mouse proximity to brighten nearby active threads
            let threadAlpha = (1 - dist / connectionDistance) * 0.22;
            let strokeColor = 'rgba(56, 189, 248,';

            if (mouse.isActive) {
              const mouseDist = Math.hypot(mouse.x - (p.x + p2.x) / 2, mouse.y - (p.y + p2.y) / 2);
              if (mouseDist < mouse.radius) {
                const mouseFactor = 1 - mouseDist / mouse.radius;
                threadAlpha += mouseFactor * 0.35;
                // Shift slightly to electric icy cyan
                strokeColor = 'rgba(125, 211, 252,';
              }
            }

            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.strokeStyle = `${strokeColor} ${Math.min(threadAlpha, 0.65)})`;
            ctx.lineWidth = 0.85;
            ctx.stroke();
          }
        }
      }

      animationFrameId = requestAnimationFrame(render);
    };

    animationFrameId = requestAnimationFrame(render);

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseleave', handleMouseLeave);
      window.removeEventListener('touchmove', handleTouchMove);
      window.removeEventListener('touchend', handleTouchEnd);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        pointerEvents: 'none',
        zIndex: 0,
        opacity: 0.85
      }}
      aria-hidden="true"
    />
  );
};
