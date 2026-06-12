import { LanguageSwitcher } from "@/components/layout/language-switcher";
import { AuthBrandPanel } from "@/components/layout/auth-brand-panel";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen">
      <AuthBrandPanel />
      <div className="relative flex flex-1 flex-col bg-page-gradient">
        <div className="absolute right-4 top-4 z-10 lg:right-8 lg:top-8">
          <LanguageSwitcher />
        </div>
        {children}
      </div>
    </div>
  );
}
