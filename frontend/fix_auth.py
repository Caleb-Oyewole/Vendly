import os

with open('src/contexts/AuthContext.tsx', 'r') as f:
    content = f.read()

content = content.replace("import { onAuthStateChanged } from 'firebase/auth';\\nimport type { User } from 'firebase/auth';", "import { onAuthStateChanged } from 'firebase/auth';\\nimport type { User } from 'firebase/auth';")

with open('src/contexts/AuthContext.tsx', 'w') as f:
    f.write("""import { createContext, useContext, useEffect, useState } from 'react';
import { onAuthStateChanged } from 'firebase/auth';
import type { User } from 'firebase/auth';
import { auth } from '../lib/firebase';
import Skeleton from '../components/states/Skeleton';

interface AuthContextType {
  user: User | null;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType>({ user: null, loading: true });

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  if (loading) {
    return <div className="h-screen w-screen flex items-center justify-center bg-surface"><Skeleton rows={3} /></div>;
  }

  return (
    <AuthContext.Provider value={{ user, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
""")
