import React, { useState } from 'react';
import { User, KeyRound, LogIn, ShieldCheck, LogOut, UserPlus, Info, Eye, EyeOff } from 'lucide-react';

interface StoredUser {
  name: string;
  passHash: string;
  createdAt: number;
}

const USERS_KEY = 'younglancers_users_v1';
const SESSION_KEY = 'younglancers_session_v1';

async function hashPassword(password: string): Promise<string> {
  const bytes = new TextEncoder().encode(password);
  const digest = await crypto.subtle.digest('SHA-256', bytes);
  return Array.from(new Uint8Array(digest))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

function loadUsers(): StoredUser[] {
  try {
    return JSON.parse(localStorage.getItem(USERS_KEY) || '[]');
  } catch {
    return [];
  }
}

function saveUsers(users: StoredUser[]) {
  localStorage.setItem(USERS_KEY, JSON.stringify(users));
}

export const Portal: React.FC = () => {
  const [current, setCurrent] = useState<StoredUser | null>(() => {
    try {
      return JSON.parse(localStorage.getItem(SESSION_KEY) || 'null');
    } catch {
      return null;
    }
  });
  const [mode, setMode] = useState<'signup' | 'login'>('signup');
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [status, setStatus] = useState<{ type: 'ok' | 'error'; msg: string } | null>(null);

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus(null);
    const cleanName = name.trim();
    if (cleanName.length < 2) {
      setStatus({ type: 'error', msg: 'Please use a name of at least 2 characters.' });
      return;
    }
    if (password.length < 4) {
      setStatus({ type: 'error', msg: 'Password must be at least 4 characters.' });
      return;
    }
    const users = loadUsers();
    if (users.some((u) => u.name.toLowerCase() === cleanName.toLowerCase())) {
      setStatus({ type: 'error', msg: 'That name is already registered — try logging in instead.' });
      setMode('login');
      return;
    }
    const user: StoredUser = { name: cleanName, passHash: await hashPassword(password), createdAt: Date.now() };
    users.push(user);
    saveUsers(users);
    localStorage.setItem(SESSION_KEY, JSON.stringify(user));
    setCurrent(user);
    setPassword('');
    setStatus({ type: 'ok', msg: `Welcome to Younglancers, ${cleanName}! Your account is ready.` });
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus(null);
    const users = loadUsers();
    const h = await hashPassword(password);
    const matched = users.find((u) => u.name.toLowerCase() === name.trim().toLowerCase() && u.passHash === h);
    if (!matched) {
      setStatus({ type: 'error', msg: 'Name or password is incorrect.' });
      return;
    }
    localStorage.setItem(SESSION_KEY, JSON.stringify(matched));
    setCurrent(matched);
    setPassword('');
    setStatus({ type: 'ok', msg: `Welcome back, ${matched.name}.` });
  };

  const handleLogout = () => {
    localStorage.removeItem(SESSION_KEY);
    setCurrent(null);
    setName('');
    setPassword('');
    setStatus(null);
  };

  const inputStyle: React.CSSProperties = {
    width: '100%',
    padding: '12px 14px 12px 42px',
    borderRadius: '10px',
    backgroundColor: 'rgba(255, 255, 255, 0.03)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    color: '#ffffff',
    fontSize: '14px',
    fontFamily: 'var(--font-sans)',
    outline: 'none',
    boxSizing: 'border-box',
  };

  return (
    <section id="access" style={{ padding: '100px 0', borderTop: '1px solid var(--border-subtle)' }}>
      <div className="container">
        {/* Section Header */}
        <div style={{ maxWidth: '820px', marginBottom: '56px' }}>
          <div className="kicker-badge" style={{ marginBottom: '16px' }}>
            <span className="kicker-dot" />
            <span>MEMBER ACCESS</span>
          </div>
          <h2 style={{ fontSize: 'clamp(32px, 5vw, 56px)', color: '#ffffff', marginBottom: '20px' }}>
            Join the Younglancers circle.
          </h2>
          <p style={{ fontSize: '18px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
            All we ask for is <strong style={{ color: '#ffffff' }}>your name and a password</strong> — nothing else. No
            phone number, no email gate. It lives only inside your own browser.
          </p>
        </div>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            gap: '36px',
            alignItems: 'start',
          }}
        >
          {/* Auth Card */}
          <div className="glass-panel" style={{ padding: '36px 34px', border: '1px solid var(--border-active)' }}>
            {current ? (
              /* ------ LOGGED-IN STATE ------ */
              <div style={{ textAlign: 'left' }}>
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    paddingBottom: '20px',
                    marginBottom: '24px',
                    borderBottom: '1px solid var(--border-subtle)',
                  }}
                >
                  <div
                    style={{
                      width: '52px',
                      height: '52px',
                      borderRadius: '50%',
                      background: 'rgba(16, 185, 129, 0.12)',
                      border: '1px solid rgba(16, 185, 129, 0.3)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '20px',
                      fontWeight: 700,
                      color: '#10b981',
                      fontFamily: 'var(--font-display)',
                    }}
                  >
                    {current.name.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <div style={{ fontSize: '18px', fontWeight: 700, color: '#ffffff' }}>{current.name}</div>
                    <div style={{ fontSize: '12px', fontFamily: 'var(--font-mono)', color: 'var(--accent-emerald)' }}>
                      Verified member • Joined {new Date(current.createdAt).toLocaleDateString()}
                    </div>
                  </div>
                </div>

                <div style={{ display: 'grid', gap: '14px', marginBottom: '26px' }}>
                  <div style={{ padding: '16px 18px', borderRadius: '12px', background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.05)' }}>
                    <div style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '6px' }}>
                      Member Status
                    </div>
                    <div style={{ fontSize: '15px', color: '#ffffff', display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <ShieldCheck size={16} color="#10b981" /> Active — no expiry, no tracking
                    </div>
                  </div>
                  <div style={{ padding: '16px 18px', borderRadius: '12px', background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.05)' }}>
                    <div style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '6px' }}>
                      What You Get
                    </div>
                    <div style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                      Priority replies from the crew, early access to new demos (the next Sentinel Shield build is
                      coming), and member pricing on combined website + deck packages.
                    </div>
                  </div>
                </div>

                <button
                  onClick={handleLogout}
                  className="btn-secondary"
                  style={{ width: '100%', padding: '12px 20px', display: 'inline-flex', justifyContent: 'center' }}
                >
                  <LogOut size={16} />
                  <span>Sign Out</span>
                </button>
              </div>
            ) : (
              /* ------ SIGNUP / LOGIN STATE ------ */
              <div>
                {/* Mode Switch Tabs */}
                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: '1fr 1fr',
                    gap: '6px',
                    padding: '6px',
                    borderRadius: '12px',
                    background: 'rgba(255, 255, 255, 0.03)',
                    border: '1px solid rgba(255, 255, 255, 0.06)',
                    marginBottom: '26px',
                  }}
                >
                  <button
                    onClick={() => { setMode('signup'); setStatus(null); }}
                    style={{
                      padding: '10px',
                      borderRadius: '8px',
                      border: mode === 'signup' ? '1px solid var(--accent-cyan)' : '1px solid transparent',
                      background: mode === 'signup' ? 'rgba(56, 189, 248, 0.12)' : 'transparent',
                      color: mode === 'signup' ? '#ffffff' : 'var(--text-secondary)',
                      fontSize: '14px',
                      fontWeight: 600,
                      cursor: 'pointer',
                      display: 'inline-flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '8px',
                    }}
                  >
                    <UserPlus size={15} /> Create Account
                  </button>
                  <button
                    onClick={() => { setMode('login'); setStatus(null); }}
                    style={{
                      padding: '10px',
                      borderRadius: '8px',
                      border: mode === 'login' ? '1px solid var(--accent-cyan)' : '1px solid transparent',
                      background: mode === 'login' ? 'rgba(56, 189, 248, 0.12)' : 'transparent',
                      color: mode === 'login' ? '#ffffff' : 'var(--text-secondary)',
                      fontSize: '14px',
                      fontWeight: 600,
                      cursor: 'pointer',
                      display: 'inline-flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '8px',
                    }}
                  >
                    <LogIn size={15} /> Log In
                  </button>
                </div>

                {/* THE FORM — exactly 2 fields: name & password */}
                <form
                  onSubmit={mode === 'signup' ? handleSignup : handleLogin}
                  style={{ display: 'grid', gap: '18px' }}
                >
                  <div>
                    <label
                      htmlFor="portal-name"
                      style={{
                        display: 'block',
                        fontSize: '12px',
                        fontFamily: 'var(--font-mono)',
                        color: 'var(--accent-cyan)',
                        textTransform: 'uppercase',
                        letterSpacing: '0.1em',
                        marginBottom: '8px',
                      }}
                    >
                      {mode === 'signup' ? '1. Your Name' : 'Name'}
                    </label>
                    <div style={{ position: 'relative' }}>
                      <User size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)' }} />
                      <input
                        id="portal-name"
                        type="text"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        placeholder="e.g., Priya Sharma"
                        autoComplete="off"
                        required
                        style={inputStyle}
                      />
                    </div>
                  </div>

                  <div>
                    <label
                      htmlFor="portal-password"
                      style={{
                        display: 'block',
                        fontSize: '12px',
                        fontFamily: 'var(--font-mono)',
                        color: 'var(--accent-cyan)',
                        textTransform: 'uppercase',
                        letterSpacing: '0.1em',
                        marginBottom: '8px',
                      }}
                    >
                      {mode === 'signup' ? '2. Your Password' : 'Password'}
                    </label>
                    <div style={{ position: 'relative' }}>
                      <KeyRound size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)' }} />
                      <input
                        id="portal-password"
                        type={showPassword ? 'text' : 'password'}
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="Just name + password — that's it"
                        autoComplete="new-password"
                        required
                        style={{ ...inputStyle, paddingRight: '42px' }}
                      />
                      <button
                        type="button"
                        aria-label={showPassword ? 'Hide password' : 'Show password'}
                        onClick={() => setShowPassword((v) => !v)}
                        style={{
                          position: 'absolute',
                          right: '10px',
                          top: '50%',
                          transform: 'translateY(-50%)',
                          background: 'none',
                          border: 'none',
                          color: 'var(--text-muted)',
                          cursor: 'pointer',
                          padding: '4px',
                          display: 'flex',
                        }}
                      >
                        {showPassword ? <EyeOff size={17} /> : <Eye size={17} />}
                      </button>
                    </div>
                  </div>

                  {/* Status messages */}
                  {status && (
                    <div
                      style={{
                        padding: '12px 16px',
                        borderRadius: '10px',
                        fontSize: '13.5px',
                        lineHeight: 1.5,
                        border: `1px solid ${status.type === 'ok' ? 'rgba(16, 185, 129, 0.35)' : 'rgba(239, 68, 68, 0.35)'}`,
                        background: status.type === 'ok' ? 'rgba(16, 185, 129, 0.08)' : 'rgba(239, 68, 68, 0.08)',
                        color: status.type === 'ok' ? '#6ee7b7' : '#fca5a5',
                      }}
                    >
                      {status.msg}
                    </div>
                  )}

                  <button
                    type="submit"
                    className="btn-primary"
                    style={{ width: '100%', padding: '14px', fontSize: '15px', boxSizing: 'border-box' }}
                  >
                    {mode === 'signup' ? (
                      <>
                        <UserPlus size={17} />
                        <span>Create My Account</span>
                      </>
                    ) : (
                      <>
                        <LogIn size={17} />
                        <span>Log In</span>
                      </>
                    )}
                  </button>

                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '8px',
                      fontSize: '12px',
                      color: 'var(--text-muted)',
                      fontFamily: 'var(--font-mono)',
                      lineHeight: 1.5,
                    }}
                  >
                    <Info size={14} style={{ flexShrink: 0, marginTop: '1px' }} />
                    <span>
                      Only 2 fields by design — no phone number, no email. Passwords are hashed locally
                      (SHA-256) and never leave your browser. Because there is no server, clearing browser data
                      also clears member accounts.
                    </span>
                  </div>
                </form>
              </div>
            )}
          </div>

          {/* Side info column */}
          <div style={{ display: 'grid', gap: '20px' }}>
            <div style={{ padding: '24px', borderRadius: '14px', backgroundColor: 'rgba(255, 255, 255, 0.02)', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
              <h4 style={{ fontSize: '17px', color: '#ffffff', marginBottom: '8px' }}>Why just name & password?</h4>
              <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: 1.65 }}>
                We follow the same principle you'll find in our security work (Sentinel Shield): ask for the minimum
                data you actually need. Two fields, zero friction — and your password is stored as a hash inside your
                own device, not on any server.
              </p>
            </div>
            <div style={{ padding: '24px', borderRadius: '14px', backgroundColor: 'rgba(255, 255, 255, 0.02)', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
              <h4 style={{ fontSize: '17px', color: '#ffffff', marginBottom: '8px' }}>No numbers. Ever.</h4>
              <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: 1.65 }}>
                Creating an account does not ask for phone numbers, verification, or OTPs. The site stays fully static
                (GitHub Pages compatible), so there is literally no database or backend collecting anything.
              </p>
            </div>
            <div style={{ padding: '24px', borderRadius: '14px', backgroundColor: 'rgba(255, 255, 255, 0.02)', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
              <h4 style={{ fontSize: '17px', color: '#ffffff', marginBottom: '8px' }}>Work with us directly</h4>
              <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: 1.65 }}>
                Members can still reach the crew instantly via the{' '}
                <a href="#contact" style={{ color: 'var(--accent-cyan)', textDecoration: 'none' }}>
                  Contact
                </a>{' '}
                section — through direct email with your inquiry pre-filled.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
