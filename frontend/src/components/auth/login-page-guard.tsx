'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

import { useAuthStore } from '@/store/auth-store';
import { LoginForm } from '@/components/auth/login-form';
import type { OAuthProvider } from '@/lib/oauth';

interface LoginPageGuardProps {
  enabledProviders: OAuthProvider[];
}

export function LoginPageGuard({ enabledProviders }: LoginPageGuardProps) {
  const router = useRouter();
  const { _hasHydrated, isAuthenticated } = useAuthStore();

  useEffect(() => {
    if (!_hasHydrated) return;

    const hasStoredSession =
      typeof window !== 'undefined' &&
      !!(localStorage.getItem('access_token') || localStorage.getItem('refresh_token'));

    if (isAuthenticated || hasStoredSession) {
      const next =
        typeof window !== 'undefined'
          ? new URLSearchParams(window.location.search).get('next')
          : null;
      const redirectTo =
        next && next.startsWith('/') && !next.startsWith('/login') ? next : '/dashboard';
      router.replace(redirectTo);
    }
  }, [_hasHydrated, isAuthenticated, router]);

  if (!_hasHydrated) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-blue-600" />
      </div>
    );
  }

  if (isAuthenticated) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-blue-600" />
      </div>
    );
  }

  return <LoginForm enabledProviders={enabledProviders} />;
}
