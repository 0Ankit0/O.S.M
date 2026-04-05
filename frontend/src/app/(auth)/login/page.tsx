import { LoginPageGuard } from '@/components/auth/login-page-guard';
import { getEnabledProviders } from '@/lib/oauth';

export default async function LoginPage() {
  const enabledProviders = await getEnabledProviders();
  return <LoginPageGuard enabledProviders={enabledProviders} />;
}
