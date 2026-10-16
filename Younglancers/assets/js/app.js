/**
 * PixelForge Main Application Logic
 * Clean, modular, zero-dependency ES6 vanilla implementation
 */
(function () {
  'use strict';

  // Config constants
  var CONFIG = {
    brandName: 'PixelForge',
    repoName: 'Younglancers',
    email: 'krushuchudasama03@gmail.com',
    founder: 'Krushnrajsinh Chudasama',
    team: ['Krushnrajsinh Chudasama', 'Rishi', 'Yuvi']
  };

  // -------------------------------------------------------------
  // 1. Navigation & Scroll Progress Indicator
  // -------------------------------------------------------------
  var progressBar = document.getElementById('scroll-progress');
  var header = document.getElementById('main-header');
  var mobileMenuBtn = document.getElementById('mobile-menu-toggle');
  var mobileNav = document.getElementById('mobile-nav');

  function updateScrollState() {
    var scrollY = window.scrollY || window.pageYOffset;
    var docHeight = document.documentElement.scrollHeight - window.innerHeight;
    
    if (progressBar && docHeight > 0) {
      var progress = Math.min(100, Math.max(0, (scrollY / docHeight) * 100));
      progressBar.style.width = progress + '%';
    }

    if (header) {
      if (scrollY > 25) {
        header.classList.add('scrolled');
      } else {
        header.classList.remove('scrolled');
      }
    }

    // Active Section Spy
    var sections = ['work', 'services', 'presentations', 'web-engineering', 'estimator', 'team', 'achievements', 'about', 'portal', 'contact'];
    var currentSection = '';

    for (var i = 0; i < sections.length; i++) {
      var el = document.getElementById(sections[i]);
      if (el) {
        var rect = el.getBoundingClientRect();
        if (rect.top <= 240 && rect.bottom >= 240) {
          currentSection = sections[i];
          break;
        }
      }
    }

    if (currentSection) {
      document.querySelectorAll('.nav-link').forEach(function (link) {
        var href = link.getAttribute('href');
        if (href === '#' + currentSection) {
          link.classList.add('active');
        } else {
          link.classList.remove('active');
        }
      });
    }
  }

  window.addEventListener('scroll', updateScrollState, { passive: true });

  if (mobileMenuBtn && mobileNav) {
    mobileMenuBtn.addEventListener('click', function () {
      var isOpen = mobileNav.classList.toggle('open');
      mobileMenuBtn.setAttribute('aria-expanded', isOpen);
    });

    mobileNav.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        mobileNav.classList.remove('open');
        mobileMenuBtn.setAttribute('aria-expanded', 'false');
      });
    });
  }

  // -------------------------------------------------------------
  // 2. Portfolio Project Filter & Interactive Demos
  // -------------------------------------------------------------
  var filterButtons = document.querySelectorAll('.filter-pill');
  var projectCards = document.querySelectorAll('.project-card');

  filterButtons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      filterButtons.forEach(function (b) { b.classList.remove('active'); });
      btn.classList.add('active');

      var category = btn.getAttribute('data-filter');

      projectCards.forEach(function (card) {
        var cardCat = card.getAttribute('data-category');
        if (category === 'all' || cardCat === category) {
          card.style.display = 'flex';
          card.style.animation = 'fadeInUp 0.35s ease';
        } else {
          card.style.display = 'none';
        }
      });
    });
  });

  // Modal Demo Previewer (Embedded in-page iframe preview)
  var demoModal = document.getElementById('demo-modal');
  var demoIframe = document.getElementById('demo-modal-iframe');
  var demoModalTitle = document.getElementById('demo-modal-title');
  var demoModalExternal = document.getElementById('demo-modal-external');
  var demoModalClose = document.getElementById('demo-modal-close');

  function openDemoModal(url, title) {
    if (!demoModal || !demoIframe) {
      window.open(url, '_blank', 'noopener,noreferrer');
      return;
    }
    demoIframe.src = url;
    if (demoModalTitle) demoModalTitle.textContent = title;
    if (demoModalExternal) demoModalExternal.href = url;
    demoModal.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function closeDemoModal() {
    if (!demoModal) return;
    demoModal.classList.remove('open');
    if (demoIframe) demoIframe.src = 'about:blank';
    document.body.style.overflow = '';
  }

  if (demoModalClose) {
    demoModalClose.addEventListener('click', closeDemoModal);
  }

  if (demoModal) {
    demoModal.addEventListener('click', function (e) {
      if (e.target === demoModal) closeDemoModal();
    });
  }

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && demoModal && demoModal.classList.contains('open')) {
      closeDemoModal();
    }
  });

  // Attach demo open handlers
  document.querySelectorAll('[data-demo-url]').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      var url = btn.getAttribute('data-demo-url');
      var title = btn.getAttribute('data-demo-title') || 'Live Demo';
      var mode = btn.getAttribute('data-demo-mode'); // 'tab' or 'modal'

      if (mode === 'tab') {
        window.open(url, '_blank', 'noopener,noreferrer');
      } else {
        openDemoModal(url, title);
      }
    });
  });

  // -------------------------------------------------------------
  // 3. Presentation Master Deck Interactive Viewer
  // -------------------------------------------------------------
  var deckSlides = [
    {
      kicker: '01 / EXECUTIVE INVESTOR PITCH',
      title: 'Decentralized Neural Fabric Architecture',
      subtitle: 'Achieving 2.4x throughput per watt across distributed edge inference clusters.',
      metrics: [
        { label: 'ENERGY EFFICIENCY', val: '4.8 TFLOPS/W' },
        { label: 'NETWORK LATENCY', val: '< 0.38 ms' },
        { label: 'CLUSTER PARITY', val: '99.98%' }
      ],
      themeBg: '#ffffff',
      accent: '#2563eb',
      badge: 'Dark Cinematic'
    },
    {
      kicker: '02 / SCIENTIFIC SYMPOSIUM & RESEARCH',
      title: 'Targeted In-Vivo RNA Base Editing',
      subtitle: 'Comparative safety profile and off-target screening across 1,200 mammalian sequences.',
      metrics: [
        { label: 'AFFINITY RATE', val: '96.2%' },
        { label: 'OFF-TARGETS', val: '0 DETECTED' },
        { label: 'COHORT SIZE', val: 'n = 450' }
      ],
      themeBg: '#f8fafc',
      accent: '#059669',
      badge: 'Scientific Editorial'
    },
    {
      kicker: '03 / ENTERPRISE ROADMAP & STRATEGY',
      title: 'Global Enterprise Adoption Roadmap',
      subtitle: 'Systematic pipeline transition targeting Tier-1 financial institutions across 2026-2028.',
      metrics: [
        { label: 'TAM TARGET', val: '$24.6B' },
        { label: 'ENTERPRISE MOAT', val: '8 PATENTS' },
        { label: 'PILOT PARTNERS', val: '14 SIGNED' }
      ],
      themeBg: '#fcf8f5',
      accent: '#ea580c',
      badge: 'Executive Modern'
    }
  ];

  var currentSlideIdx = 0;
  var deckKicker = document.getElementById('deck-kicker');
  var deckTitle = document.getElementById('deck-title');
  var deckSubtitle = document.getElementById('deck-subtitle');
  var deckMetrics = document.getElementById('deck-metrics');
  var deckFrame = document.getElementById('deck-frame');
  var deckDots = document.querySelectorAll('.deck-dot');

  function renderSlide(index) {
    if (!deckFrame) return;
    currentSlideIdx = index;
    var s = deckSlides[index];

    if (deckKicker) {
      deckKicker.textContent = s.kicker;
      deckKicker.style.color = s.accent;
    }
    if (deckTitle) deckTitle.textContent = s.title;
    if (deckSubtitle) deckSubtitle.textContent = s.subtitle;

    if (deckMetrics) {
      deckMetrics.innerHTML = s.metrics.map(function (m) {
        return '<div class="deck-metric-box">' +
          '<div class="metric-label">' + m.label + '</div>' +
          '<div class="metric-val" style="color:' + s.accent + '">' + m.val + '</div>' +
          '</div>';
      }).join('');
    }

    deckDots.forEach(function (dot, i) {
      dot.classList.toggle('active', i === index);
    });

    deckFrame.style.borderColor = s.accent;
  }

  deckDots.forEach(function (dot, i) {
    dot.addEventListener('click', function () {
      renderSlide(i);
    });
  });

  // -------------------------------------------------------------
  // 4. Web Engineering Interactive Viewport Switcher
  // -------------------------------------------------------------
  var webSites = {
    sentinel: {
      url: 'sentinel-shield.app',
      tagline: 'Sentinel Shield — Cybersecurity Workspace',
      desc: 'Our complete live security tool: real-time phishing detection, local password strength analysis, Ask Sentinel assistant, and Manifest V3 Chrome extension hub.',
      accent: '#059669',
      badge: 'Shipped Product UI',
      actionUrl: './demos/sentinel-shield.html'
    },
    jarvis: {
      url: 'jarvis-hud.local',
      tagline: 'JARVIS v7 / v8 — Touchless Scientific HUD',
      desc: 'Hand-gesture-driven OpenGL 3D visualization platform: MediaPipe tracking, holographic widgets, exploded molecular models, and virtual chemistry lab.',
      accent: '#2563eb',
      badge: 'Software Source Demo',
      actionUrl: './demos/jarvis-viewer.html?version=v7'
    },
    pixelforge: {
      url: 'younglancers.github.io',
      tagline: 'PixelForge — Tangible Human Craftsmanship',
      desc: 'The website you are experiencing now: woven square grid thread canvas, client-side member portal, interactive scope estimator, and zero-build GitHub Pages deployment.',
      accent: '#6366f1',
      badge: 'Deployed & Production Ready',
      actionUrl: '#home'
    }
  };

  var webTabBtns = document.querySelectorAll('.web-tab-btn');
  var webUrlEl = document.getElementById('web-view-url');
  var webTaglineEl = document.getElementById('web-view-tagline');
  var webDescEl = document.getElementById('web-view-desc');
  var webBadgeEl = document.getElementById('web-view-badge');
  var webLaunchBtn = document.getElementById('web-view-launch');

  function renderWebSite(key) {
    var item = webSites[key];
    if (!item) return;

    webTabBtns.forEach(function (btn) {
      btn.classList.toggle('active', btn.getAttribute('data-site') === key);
    });

    if (webUrlEl) webUrlEl.textContent = 'https://' + item.url;
    if (webTaglineEl) webTaglineEl.textContent = item.tagline;
    if (webDescEl) webDescEl.textContent = item.desc;
    if (webBadgeEl) {
      webBadgeEl.textContent = item.badge;
      webBadgeEl.style.color = item.accent;
    }
    if (webLaunchBtn) {
      webLaunchBtn.setAttribute('data-demo-url', item.actionUrl);
      webLaunchBtn.setAttribute('data-demo-title', item.tagline);
    }
  }

  webTabBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var key = btn.getAttribute('data-site');
      renderWebSite(key);
    });
  });

  // -------------------------------------------------------------
  // 5. Interactive Scope & Turnaround Estimator
  // -------------------------------------------------------------
  var estimatorBoxes = document.querySelectorAll('.estimator-check');
  var estTurnaround = document.getElementById('est-turnaround');
  var estDeliverables = document.getElementById('est-deliverables');
  var estApplyBtn = document.getElementById('est-apply-btn');

  function calculateEstimate() {
    var checked = [];
    var days = 0;
    var deliverables = [];

    estimatorBoxes.forEach(function (box) {
      if (box.checked) {
        var name = box.getAttribute('data-name');
        var d = parseInt(box.getAttribute('data-days'), 10) || 2;
        var deliv = box.getAttribute('data-deliverable');

        checked.push(name);
        days = Math.max(days, d);
        if (deliv) deliverables.push(deliv);
      }
    });

    if (checked.length === 0) {
      if (estTurnaround) estTurnaround.textContent = 'Select items above';
      if (estDeliverables) estDeliverables.innerHTML = '<span class="text-muted">Choose your desired deliverables to see timeline & specs</span>';
      return;
    }

    // Add compound time buffer if multiple large deliverables selected
    if (checked.length > 2) days += 2;

    if (estTurnaround) {
      estTurnaround.textContent = days + ' - ' + (days + 3) + ' Days Turnaround';
    }

    if (estDeliverables) {
      estDeliverables.innerHTML = deliverables.map(function (item) {
        return '<div class="deliverable-chip"><span>✓</span> ' + item + '</div>';
      }).join('');
    }
  }

  estimatorBoxes.forEach(function (box) {
    box.addEventListener('change', calculateEstimate);
  });

  if (estApplyBtn) {
    estApplyBtn.addEventListener('click', function () {
      var selected = [];
      estimatorBoxes.forEach(function (box) {
        if (box.checked) selected.push(box.getAttribute('data-name'));
      });

      var briefInput = document.getElementById('custom-note-input');
      if (briefInput && selected.length > 0) {
        briefInput.value = 'Interested in scope: ' + selected.join(' + ') + '.\nLooking forward to aligning on specifications and timeline.';
      }

      var contactSection = document.getElementById('contact');
      if (contactSection) {
        contactSection.scrollIntoView({ behavior: 'smooth' });
      }
    });
  }

  // -------------------------------------------------------------
  // 6. Privacy-First Local Member Portal ("PixelForge Circle")
  // -------------------------------------------------------------
  var USERS_KEY = 'pixelforge_users_v2';
  var SESSION_KEY = 'pixelforge_session_v2';

  async function hashPassword(pwd) {
    var encoder = new TextEncoder();
    var data = encoder.encode(pwd);
    var hashBuffer = await crypto.subtle.digest('SHA-256', data);
    var hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(function (b) { return b.toString(16).padStart(2, '0'); }).join('');
  }

  function getStoredUsers() {
    try {
      return JSON.parse(localStorage.getItem(USERS_KEY) || '[]');
    } catch (e) {
      return [];
    }
  }

  function saveStoredUsers(users) {
    localStorage.setItem(USERS_KEY, JSON.stringify(users));
  }

  function getCurrentSession() {
    try {
      return JSON.parse(localStorage.getItem(SESSION_KEY) || 'null');
    } catch (e) {
      return null;
    }
  }

  var portalForm = document.getElementById('portal-form');
  var portalModeBtns = document.querySelectorAll('.portal-mode-btn');
  var portalStatus = document.getElementById('portal-status');
  var portalLoggedInView = document.getElementById('portal-logged-in');
  var portalLoggedOutView = document.getElementById('portal-logged-out');
  var portalUserName = document.getElementById('portal-user-name');
  var portalUserInitial = document.getElementById('portal-user-initial');
  var portalLogoutBtn = document.getElementById('portal-logout-btn');
  var portalSubmitBtn = document.getElementById('portal-submit-btn');

  var currentMode = 'signup';

  function updatePortalUI() {
    var session = getCurrentSession();
    if (session) {
      if (portalLoggedInView) portalLoggedInView.style.display = 'block';
      if (portalLoggedOutView) portalLoggedOutView.style.display = 'none';
      if (portalUserName) portalUserName.textContent = session.name;
      if (portalUserInitial) portalUserInitial.textContent = session.name.charAt(0).toUpperCase();
    } else {
      if (portalLoggedInView) portalLoggedInView.style.display = 'none';
      if (portalLoggedOutView) portalLoggedOutView.style.display = 'block';
    }
  }

  portalModeBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      currentMode = btn.getAttribute('data-mode');
      portalModeBtns.forEach(function (b) { b.classList.toggle('active', b === btn); });

      if (portalSubmitBtn) {
        portalSubmitBtn.innerHTML = currentMode === 'signup'
          ? '<span>Create Member Account</span> →'
          : '<span>Sign In to Circle</span> →';
      }
      if (portalStatus) {
        portalStatus.textContent = '';
        portalStatus.className = 'portal-status-msg';
      }
    });
  });

  if (portalForm) {
    portalForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      var nameInput = document.getElementById('portal-name');
      var passInput = document.getElementById('portal-pass');

      var nameVal = (nameInput ? nameInput.value : '').trim();
      var passVal = (passInput ? passInput.value : '').trim();

      if (!portalStatus) return;

      if (nameVal.length < 2) {
        portalStatus.textContent = 'Please enter a name with at least 2 characters.';
        portalStatus.className = 'portal-status-msg error';
        return;
      }
      if (passVal.length < 4) {
        portalStatus.textContent = 'Password must be at least 4 characters.';
        portalStatus.className = 'portal-status-msg error';
        return;
      }

      var users = getStoredUsers();
      var passHash = await hashPassword(passVal);

      if (currentMode === 'signup') {
        var exists = users.some(function (u) { return u.name.toLowerCase() === nameVal.toLowerCase(); });
        if (exists) {
          portalStatus.textContent = 'That name is already registered in this browser. Please switch to Sign In.';
          portalStatus.className = 'portal-status-msg error';
          return;
        }

        var newUser = { name: nameVal, passHash: passHash, createdAt: Date.now() };
        users.push(newUser);
        saveStoredUsers(users);
        localStorage.setItem(SESSION_KEY, JSON.stringify(newUser));

        if (passInput) passInput.value = '';
        updatePortalUI();

        if (window.pixelConfetti) window.pixelConfetti();
      } else {
        var match = users.find(function (u) {
          return u.name.toLowerCase() === nameVal.toLowerCase() && u.passHash === passHash;
        });

        if (!match) {
          portalStatus.textContent = 'Name or password does not match. Please verify.';
          portalStatus.className = 'portal-status-msg error';
          return;
        }

        localStorage.setItem(SESSION_KEY, JSON.stringify(match));
        if (passInput) passInput.value = '';
        updatePortalUI();

        if (window.pixelConfetti) window.pixelConfetti();
      }
    });
  }

  if (portalLogoutBtn) {
    portalLogoutBtn.addEventListener('click', function () {
      localStorage.removeItem(SESSION_KEY);
      updatePortalUI();
    });
  }

  updatePortalUI();

  // -------------------------------------------------------------
  // 7. Contact Collaboration & Mailto Generator
  // -------------------------------------------------------------
  var inquiryTabs = document.querySelectorAll('.inquiry-pill');
  var customNoteInput = document.getElementById('custom-note-input');
  var contactSubmitBtn = document.getElementById('contact-submit-btn');
  var copyEmailBtn = document.getElementById('copy-email-btn');
  var copyStatusText = document.getElementById('copy-status-text');

  var selectedInquiry = 'Presentation Design';

  inquiryTabs.forEach(function (tab) {
    tab.addEventListener('click', function () {
      inquiryTabs.forEach(function (t) { t.classList.remove('active'); });
      tab.classList.add('active');
      selectedInquiry = tab.getAttribute('data-inquiry') || 'Presentation Design';
    });
  });

  function triggerDirectEmail() {
    var note = customNoteInput ? customNoteInput.value.trim() : '';
    var subject = encodeURIComponent('Inquiry: ' + selectedInquiry + ' — PixelForge');
    
    var bodyContent = 'Hi Krushnrajsinh,\n\n' +
      'I came across PixelForge and would like to discuss a project with the crew.\n\n' +
      'Project Scope: ' + selectedInquiry + '\n' +
      'Details / Requirements:\n' +
      (note ? note : '[Please briefly describe your presentation or website needs here]') + '\n\n' +
      'Looking forward to hearing from you!\n';

    var mailtoUrl = 'mailto:' + CONFIG.email + '?subject=' + subject + '&body=' + encodeURIComponent(bodyContent);
    window.location.href = mailtoUrl;
  }

  if (contactSubmitBtn) {
    contactSubmitBtn.addEventListener('click', triggerDirectEmail);
  }

  if (copyEmailBtn) {
    copyEmailBtn.addEventListener('click', function () {
      navigator.clipboard.writeText(CONFIG.email).then(function () {
        if (copyStatusText) {
          copyStatusText.textContent = 'Copied to clipboard!';
          copyStatusText.style.color = '#059669';
          setTimeout(function () {
            copyStatusText.textContent = 'Copy Address';
            copyStatusText.style.color = '';
          }, 2400);
        }

        if (window.pixelConfetti) {
          var rect = copyEmailBtn.getBoundingClientRect();
          window.pixelConfetti(rect.left + rect.width / 2, rect.top + rect.height / 2, 35);
        }
      });
    });
  }

})();
