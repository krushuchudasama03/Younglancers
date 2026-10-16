/**
 * PixelForge Micro-Confetti Utility
 * Zero-dependency celebratory canvas effect
 */
window.pixelConfetti = (function () {
  'use strict';

  var canvas = null;
  var ctx = null;
  var particles = [];
  var animationId = null;

  var colors = ['#2563eb', '#3b82f6', '#059669', '#10b981', '#ea580c', '#f59e0b', '#6366f1'];

  function createParticle(originX, originY) {
    var angle = Math.random() * Math.PI * 2;
    var velocity = Math.random() * 8 + 4;
    return {
      x: originX,
      y: originY,
      vx: Math.cos(angle) * velocity,
      vy: Math.sin(angle) * velocity - 3,
      size: Math.random() * 6 + 4,
      color: colors[Math.floor(Math.random() * colors.length)],
      alpha: 1,
      decay: Math.random() * 0.02 + 0.015,
      rotation: Math.random() * 360,
      vRotation: (Math.random() - 0.5) * 12
    };
  }

  function ensureCanvas() {
    if (!canvas) {
      canvas = document.createElement('canvas');
      canvas.id = 'confetti-canvas';
      canvas.style.position = 'fixed';
      canvas.style.top = '0';
      canvas.style.left = '0';
      canvas.style.width = '100vw';
      canvas.style.height = '100vh';
      canvas.style.pointerEvents = 'none';
      canvas.style.zIndex = '9999';
      document.body.appendChild(canvas);
      ctx = canvas.getContext('2d');
    }
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }

  function render() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    for (var i = particles.length - 1; i >= 0; i--) {
      var p = particles[i];
      p.x += p.vx;
      p.y += p.vy;
      p.vy += 0.22; // gravity
      p.vx *= 0.98; // air resistance
      p.rotation += p.vRotation;
      p.alpha -= p.decay;

      if (p.alpha <= 0) {
        particles.splice(i, 1);
        continue;
      }

      ctx.save();
      ctx.translate(p.x, p.y);
      ctx.rotate((p.rotation * Math.PI) / 180);
      ctx.globalAlpha = Math.max(0, p.alpha);
      ctx.fillStyle = p.color;
      ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 0.6);
      ctx.restore();
    }

    if (particles.length > 0) {
      animationId = requestAnimationFrame(render);
    } else {
      cancelAnimationFrame(animationId);
      animationId = null;
    }
  }

  return function (originX, originY, count) {
    ensureCanvas();
    var x = originX !== undefined ? originX : window.innerWidth / 2;
    var y = originY !== undefined ? originY : window.innerHeight * 0.7;
    var total = count || 45;

    for (var i = 0; i < total; i++) {
      particles.push(createParticle(x, y));
    }

    if (!animationId) {
      animationId = requestAnimationFrame(render);
    }
  };
})();
