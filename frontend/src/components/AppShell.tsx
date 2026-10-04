import { useState, useEffect } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { SunIcon, MoonIcon } from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';
import { logoutUser } from '../lib/firebase';

export default function AppShell() {
  const location = useLocation();
  const { user } = useAuth();
  
  const [isDark, setIsDark] = useState(() => {
    const savedTheme = localStorage.getItem('vendly-theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    return savedTheme === 'dark' || (!savedTheme && systemPrefersDark);
  });

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDark]);

  const toggleTheme = () => {
    setIsDark((prev) => {
      const newValue = !prev;
      localStorage.setItem('vendly-theme', newValue ? 'dark' : 'light');
      return newValue;
    });
  };

  return (
    <div className="min-h-screen flex flex-col transition-colors duration-200">
      <header className="bg-brand text-white shrink-0 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-8">
            <Link to="/" className="flex items-center gap-2 font-bold text-xl tracking-tight active:scale-95 transition-transform">
              <div className="bg-white text-brand w-8 h-8 rounded flex items-center justify-center font-black shadow-sm">V</div>
              Vendly
            </Link>
            
            <nav className="hidden md:flex gap-4">
              <Link 
                to="/" 
                className={`flex items-center gap-2 px-4 py-2 rounded-btn text-sm font-bold transition-all duration-200 active:scale-95 shadow-sm border ${
                  location.pathname === '/' || location.pathname.startsWith('/events') 
                    ? 'bg-white text-brand border-white shadow-inner'
                    : 'bg-black/10 text-white border-transparent hover:bg-white/20 hover:border-white/30'
                }`}
              >
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
                  <path fillRule="evenodd" d="M2 4.75C2 3.784 2.784 3 3.75 3h12.5c.966 0 1.75.784 1.75 1.75v10.5A1.75 1.75 0 0116.25 17H3.75A1.75 1.75 0 012 15.25V4.75zm1.75-.25a.25.25 0 00-.25.25v10.5c0 .138.112.25.25.25h12.5a.25.25 0 00.25-.25V4.75a.25.25 0 00-.25-.25H3.75zM6 8a1 1 0 11-2 0 1 1 0 012 0zm0 4a1 1 0 11-2 0 1 1 0 012 0zm4-4a1 1 0 11-2 0 1 1 0 012 0zm0 4a1 1 0 11-2 0 1 1 0 012 0zm4-4a1 1 0 11-2 0 1 1 0 012 0zm0 4a1 1 0 11-2 0 1 1 0 012 0z" clipRule="evenodd" />
                </svg>
                Events
              </Link>
            </nav>
          </div>
          
          <div className="flex items-center gap-5">
            <button 
              onClick={toggleTheme} 
              className="p-1.5 rounded-full hover:bg-black/10 active:scale-95 transition-all flex items-center justify-center"
              aria-label="Toggle Dark Mode"
            >
              {isDark ? (
                <SunIcon className="w-5 h-5 text-brand-tint hover:text-white" />
              ) : (
                <MoonIcon className="w-5 h-5 text-brand-tint hover:text-white" />
              )}
            </button>

            <div className="flex items-center gap-3 border-l border-brand-tint/30 pl-5 relative group">
              <span className="text-sm font-medium hidden sm:block text-brand-tint truncate max-w-[150px]">
                {user?.displayName || user?.email || 'User'}
              </span>
              {user?.photoURL ? (
                <img src={user.photoURL} alt="Profile" className="w-8 h-8 rounded-full border border-white/20 shadow-sm" />
              ) : (
                <div className="w-8 h-8 rounded-full bg-brand-tint text-brand flex items-center justify-center text-sm font-bold shadow-sm">
                  {(user?.displayName?.[0] || user?.email?.[0] || 'U').toUpperCase()}
                </div>
              )}
              
              <div className="absolute right-0 top-full mt-2 w-48 bg-white rounded-card shadow-lg border border-line opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
                <button 
                  onClick={logoutUser}
                  className="w-full text-left px-4 py-3 text-sm text-status-declined hover:bg-slate-50 font-medium"
                >
                  Sign out
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
    </div>
  );
}
