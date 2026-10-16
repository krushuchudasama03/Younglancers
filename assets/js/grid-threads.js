/**
 * PixelForge Interactive Thread Grid
 * 
 * Simulates a woven square grid of elastic threads on a refined light theme.
 * Nodes at grid intersections deform elastically with cursor proximity and
 * return to their home positions using damped harmonic spring physics.
 * 
 * Supports high-DPI displays, prefers-reduced-motion, and mobile touch.
 */
(function () {
  'use strict';

  var canvas = document.getElementById('grid-canvas');
  if (!canvas) return;

  var ctx = canvas.getContext('2d', { alpha: true });
  if (!ctx) return;

  var prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var width = 0;
  var height = 0;
  var dpr = window.devicePixelRatio || 1;
  var animationId = null;

  // Grid node definitions
  var nodes = [];
  var cols = 0;
  var rows = 0;
  var spacing = 46; // Base grid cell size in pixels

  // Mouse / Touch interaction state
  var mouse = {
    x: -2000,
    y: -2000,
    targetX: -2000,
    targetY: -2000,
    radius: 175,
    maxForce: 24,
    active: false,
    lastMove: 0
  };

  // Node Constructor
  function Node(x, y, col, row) {
    this.baseX = x;
    this.baseY = y;
    this.x = x;
    this.y = y;
    this.vx = 0;
    this.vy = 0;
    this.col = col;
    this.row = row;
    this.damping = 0.88;
    this.tension = 0.045;
    this.phase = Math.random() * Math.PI * 2;
  }

  Node.prototype.update = function (delta, time) {
    if (prefersReducedMotion) return;

    // Organic micro-breathing ambient motion (subtle human textile feel)
    var ambientX = Math.cos(time * 0.0012 + this.row * 0.15) * 0.45;
    var ambientY = Math.sin(time * 0.0014 + this.col * 0.15) * 0.45;

    // Mouse interactive displacement
    if (mouse.active) {
      var dx = mouse.x - this.x;
      var dy = mouse.y - this.y;
      var dist = Math.hypot(dx, dy);

      if (dist < mouse.radius && dist > 0) {
        var force = (1 - dist / mouse.radius);
        // Elastic pull / distortion towards cursor with spring rebound
        var angle = Math.atan2(dy, dx);
        var push = force * mouse.maxForce;

        // Displace along the vector
        this.vx += Math.cos(angle) * push * 0.18;
        this.vy += Math.sin(angle) * push * 0.18;
      }
    }

    // Spring physics pulling back to resting grid anchor
    var homeDx = (this.baseX + ambientX) - this.x;
    var homeDy = (this.baseY + ambientY) - this.y;

    this.vx += homeDx * this.tension;
    this.vy += homeDy * this.tension;

    this.vx *= this.damping;
    this.vy *= this.damping;

    this.x += this.vx;
    this.y += this.vy;
  };

  function initGrid() {
    width = window.innerWidth;
    height = window.innerHeight;

    canvas.width = Math.floor(width * dpr);
    canvas.height = Math.floor(height * dpr);
    canvas.style.width = width + 'px';
    canvas.style.height = height + 'px';

    ctx.scale(dpr, dpr);

    // Dynamic grid spacing based on viewport width
    var isMobile = width < 768;
    spacing = isMobile ? 54 : 46;
    mouse.radius = isMobile ? 130 : 180;
    mouse.maxForce = isMobile ? 18 : 28;

    cols = Math.ceil(width / spacing) + 2;
    rows = Math.ceil(height / spacing) + 2;

    nodes = [];
    var offsetX = (width - (cols - 1) * spacing) / 2;
    var offsetY = (height - (rows - 1) * spacing) / 2;

    for (var r = 0; r < rows; r++) {
      nodes[r] = [];
      for (var c = 0; c < cols; c++) {
        var x = offsetX + c * spacing;
        var y = offsetY + r * spacing;
        nodes[r][c] = new Node(x, y, c, r);
      }
    }
  }

  function drawGrid(time) {
    ctx.clearRect(0, 0, width, height);

    var baseThreadColor = 'rgba(15, 23, 42, 0.055)';
    var activeThreadColor = 'rgba(37, 99, 235, ';
    var baseDotColor = 'rgba(15, 23, 42, 0.12)';
    var activeDotColor = 'rgba(37, 99, 235, 0.65)';

    // 1. Draw Horizontal Threads with smooth curve through deformed nodes
    for (var r = 0; r < rows; r++) {
      for (var c = 0; c < cols - 1; c++) {
        var n1 = nodes[r][c];
        var n2 = nodes[r][c + 1];

        // Check if segment is near cursor
        var midX = (n1.x + n2.x) * 0.5;
        var midY = (n1.y + n2.y) * 0.5;
        var dist = mouse.active ? Math.hypot(mouse.x - midX, mouse.y - midY) : 9999;

        ctx.beginPath();
        ctx.moveTo(n1.x, n1.y);

        // Subtle curve tension
        var cpX = (n1.x + n2.x) * 0.5;
        var cpY = (n1.y + n2.y) * 0.5;
        ctx.quadraticCurveTo(cpX, cpY, n2.x, n2.y);

        if (dist < mouse.radius) {
          var glow = (1 - dist / mouse.radius);
          ctx.strokeStyle = activeThreadColor + (0.08 + glow * 0.38) + ')';
          ctx.lineWidth = 1 + glow * 1.2;
        } else {
          ctx.strokeStyle = baseThreadColor;
          ctx.lineWidth = 0.85;
        }
        ctx.stroke();
      }
    }

    // 2. Draw Vertical Threads
    for (var c = 0; c < cols; c++) {
      for (var r = 0; r < rows - 1; r++) {
        var n1 = nodes[r][c];
        var n2 = nodes[r + 1][c];

        var midX = (n1.x + n2.x) * 0.5;
        var midY = (n1.y + n2.y) * 0.5;
        var dist = mouse.active ? Math.hypot(mouse.x - midX, mouse.y - midY) : 9999;

        ctx.beginPath();
        ctx.moveTo(n1.x, n1.y);

        var cpX = (n1.x + n2.x) * 0.5;
        var cpY = (n1.y + n2.y) * 0.5;
        ctx.quadraticCurveTo(cpX, cpY, n2.x, n2.y);

        if (dist < mouse.radius) {
          var glow = (1 - dist / mouse.radius);
          ctx.strokeStyle = activeThreadColor + (0.08 + glow * 0.38) + ')';
          ctx.lineWidth = 1 + glow * 1.2;
        } else {
          ctx.strokeStyle = baseThreadColor;
          ctx.lineWidth = 0.85;
        }
        ctx.stroke();
      }
    }

    // 3. Draw Grid Intersection Knots / Nodes
    for (var r = 0; r < rows; r++) {
      for (var c = 0; c < cols; c++) {
        var n = nodes[r][c];
        n.update(16, time);

        var dist = mouse.active ? Math.hypot(mouse.x - n.x, mouse.y - n.y) : 9999;
        var isNear = dist < mouse.radius;

        ctx.beginPath();
        if (isNear) {
          var factor = 1 - dist / mouse.radius;
          var radius = 1.6 + factor * 2.4;
          ctx.arc(n.x, n.y, radius, 0, Math.PI * 2);
          ctx.fillStyle = activeDotColor;
          ctx.fill();

          // Subtle soft halo on nearest nodes
          if (factor > 0.45) {
            ctx.beginPath();
            ctx.arc(n.x, n.y, radius + 4, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(37, 99, 235, ' + (factor * 0.15) + ')';
            ctx.fill();
          }
        } else {
          // Regular subtle intersection dot
          ctx.arc(n.x, n.y, 1.1, 0, Math.PI * 2);
          ctx.fillStyle = baseDotColor;
          ctx.fill();
        }
      }
    }
  }

  var lastTime = 0;
  function animate(now) {
    // Ease mouse towards target position
    if (mouse.active) {
      mouse.x += (mouse.targetX - mouse.x) * 0.18;
      mouse.y += (mouse.targetY - mouse.y) * 0.18;

      // Inactivity timeout to fade mouse influence
      if (now - mouse.lastMove > 3200) {
        mouse.active = false;
      }
    }

    drawGrid(now);
    animationId = requestAnimationFrame(animate);
  }

  // Event Listeners
  function onMouseMove(e) {
    mouse.targetX = e.clientX;
    mouse.targetY = e.clientY;
    mouse.active = true;
    mouse.lastMove = performance.now();
  }

  function onTouchMove(e) {
    if (e.touches.length > 0) {
      mouse.targetX = e.touches[0].clientX;
      mouse.targetY = e.touches[0].clientY;
      mouse.active = true;
      mouse.lastMove = performance.now();
    }
  }

  function onMouseLeave() {
    mouse.active = false;
  }

  var resizeTimeout;
  function onResize() {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(function () {
      initGrid();
    }, 150);
  }

  window.addEventListener('mousemove', onMouseMove, { passive: true });
  window.addEventListener('mouseleave', onMouseLeave, { passive: true });
  window.addEventListener('touchmove', onTouchMove, { passive: true });
  window.addEventListener('touchend', onMouseLeave, { passive: true });
  window.addEventListener('resize', onResize, { passive: true });

  // Initialize and kick off loop
  initGrid();
  animationId = requestAnimationFrame(animate);
})();
