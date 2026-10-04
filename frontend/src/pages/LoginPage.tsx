import { useNavigate } from 'react-router-dom';
import { loginWithGoogle } from '../lib/firebase';
import { useAuth } from '../contexts/AuthContext';
import { useEffect, useState } from 'react';

export default function LoginPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [error, setError] = useState('');

  // If already logged in, redirect to dashboard
  useEffect(() => {
    if (user) {
      navigate('/');
    }
  }, [user, navigate]);

  const handleLogin = async () => {
    try {
      setError('');
      await loginWithGoogle();
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Failed to sign in. Make sure your Firebase domain is authorized.');
    }
  };

  return (
    <div className="min-h-screen bg-surface flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-md bg-white rounded-card shadow-lg border border-line p-8 text-center space-y-6">
        <div className="flex justify-center mb-2">
          <div className="bg-brand text-white w-12 h-12 rounded-lg flex items-center justify-center font-bold text-xl shadow-sm">
            V
          </div>
        </div>
        
        <div>
          <h1 className="text-2xl font-bold text-ink">Welcome to Vendly</h1>
          <p className="text-muted text-sm mt-2">Sign in to manage your events, track vendor payments, and automate confirmations.</p>
        </div>

        {error && (
          <div className="bg-red-50 text-status-declined text-sm p-3 rounded-md border border-red-100">
            {error}
          </div>
        )}

        <button 
          onClick={handleLogin}
          className="w-full py-3 px-4 rounded-btn bg-white border border-line text-ink font-semibold flex items-center justify-center gap-3 hover:bg-slate-50 transition-colors shadow-sm active:scale-95"
        >
          <svg className="w-5 h-5" viewBox="0 0 24 24">
            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
            <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
          </svg>
          Sign in with Google
        </button>

        <p className="text-xs text-muted">
          By signing in, you agree to our Terms of Service and Privacy Policy.
        </p>
      </div>
    </div>
  );
}
