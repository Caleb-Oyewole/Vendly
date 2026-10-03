import { useState, useEffect } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { SunIcon, MoonIcon } from '@heroicons/react/24/outline';

export default function AppShell() {
  const location = useLocation();
  
  // 1. Lazy initialize state: This runs once BEFORE the first render.
  const [isDark, setIsDark] = useState(() => {
    const savedTheme = localStorage.getItem('vendly-theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    return savedTheme === 'dark' || (!savedTheme && systemPrefersDark);
  });

  // 2. Synchronize DOM to state: This runs when isDark changes, avoiding setState loops.
  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDark]);

  // 3. Toggle handler: Just updates React state and localStorage.
  const toggleTheme = () => {
    setIsDark((prev) => {
      const newValue = !prev;
      localStorage.setItem('vendly-theme', newValue ? 'dark' : 'light');
      return newValue;
    });
  };

  return (
    <div className="min-h-screen flex flex-col transition-colors duration-200">
      {/* Top Navigation - Restored to solid bg-brand */}
      <header className="bg-brand text-white shrink-0 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-8">
            
            {/* IMPROVED AFFORDANCE: Logo depresses on click */}
            <Link to="/" className="flex items-center gap-2 font-bold text-xl tracking-tight active:scale-95 transition-transform">
              <div className="bg-white text-brand w-8 h-8 rounded flex items-center justify-center font-black shadow-sm">V</div>
              Vendly
            </Link>
            
            <nav className="hidden md:flex gap-4">
              {/* HIGH AFFORDANCE "EVENTS" BUTTON: Shaped like a pill, reacts to hover and click */}
              <Link 
                to="/" 
                className={`flex items-center gap-2 px-4 py-2 rounded-btn text-sm font-bold transition-all duration-200 active:scale-95 shadow-sm border ${
                  location.pathname === '/' || location.pathname.startsWith('/events') 
                    ? 'bg-white text-brand border-white shadow-inner' // Active State: Solid white pill
                    : 'bg-black/10 text-white border-transparent hover:bg-white/20 hover:border-white/30' // Inactive State: Translucent pill
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
            {/* IMPROVED AFFORDANCE: Dark Mode Toggle Button depresses on click */}
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

            {/* IMPROVED AFFORDANCE: User Profile highlights on hover */}
            <div className="flex items-center gap-2 border-l border-brand-tint/30 pl-5">
              <span className="text-sm font-medium hidden sm:block text-brand-tint">Demo Organizer</span>
              <div className="w-8 h-8 rounded-full bg-brand-tint text-brand flex items-center justify-center text-sm font-bold shadow-sm cursor-pointer hover:ring-2 hover:ring-white/50 transition-all">
                DO
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
    </div>
  );
}
