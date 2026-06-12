"use client";

import { useTheme } from "next-themes";
import { User, Palette, Building2, Mail, Shield } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useAuthStore } from "@/stores/auth-store";
import { LOCALES, LOCALE_LABELS, useLocaleStore, useT, type Locale } from "@/lib/i18n";

export default function SettingsPage() {
  const { theme, setTheme } = useTheme();
  const user = useAuthStore((s) => s.user);
  const t = useT();
  const locale = useLocaleStore((s) => s.locale);
  const setLocale = useLocaleStore((s) => s.setLocale);

  return (
    <div className="space-y-8">
      <PageHeader title={t("nav.settings")} description={t("settings.description")} />

      <Card className="shadow-sm">
        <CardHeader className="flex flex-row items-center gap-3 space-y-0">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <User className="h-4 w-4" />
          </div>
          <CardTitle>{t("settings.profile")}</CardTitle>
        </CardHeader>
        <CardContent>
          <dl className="grid gap-4 sm:grid-cols-2">
            <div className="flex items-start gap-3 rounded-xl bg-muted/40 p-4">
              <User className="mt-0.5 h-4 w-4 text-muted-foreground" />
              <div>
                <dt className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  {t("fields.fullName")}
                </dt>
                <dd className="mt-0.5 font-medium">{user?.full_name}</dd>
              </div>
            </div>
            <div className="flex items-start gap-3 rounded-xl bg-muted/40 p-4">
              <Mail className="mt-0.5 h-4 w-4 text-muted-foreground" />
              <div>
                <dt className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  {t("fields.email")}
                </dt>
                <dd className="mt-0.5 font-medium">{user?.email}</dd>
              </div>
            </div>
            <div className="flex items-start gap-3 rounded-xl bg-muted/40 p-4">
              <Shield className="mt-0.5 h-4 w-4 text-muted-foreground" />
              <div>
                <dt className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  {t("fields.role")}
                </dt>
                <dd className="mt-0.5 font-medium">{user?.role.name}</dd>
              </div>
            </div>
            <div className="flex items-start gap-3 rounded-xl bg-muted/40 p-4">
              <Building2 className="mt-0.5 h-4 w-4 text-muted-foreground" />
              <div>
                <dt className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  {t("settings.tenantId")}
                </dt>
                <dd className="mt-0.5 font-medium tabular-nums">{user?.company_id}</dd>
              </div>
            </div>
          </dl>
        </CardContent>
      </Card>

      <Card className="shadow-sm">
        <CardHeader className="flex flex-row items-center gap-3 space-y-0">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-violet-500/10 text-violet-600 dark:text-violet-400">
            <Palette className="h-4 w-4" />
          </div>
          <CardTitle>{t("settings.appearance")}</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-6 sm:grid-cols-2">
          <div>
            <Label>{t("settings.theme")}</Label>
            <Select value={theme} onValueChange={setTheme}>
              <SelectTrigger className="mt-1.5 w-full max-w-xs">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="light">{t("settings.light")}</SelectItem>
                <SelectItem value="dark">{t("settings.dark")}</SelectItem>
                <SelectItem value="system">{t("settings.system")}</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label>{t("settings.language")}</Label>
            <Select value={locale} onValueChange={(v) => setLocale(v as Locale)}>
              <SelectTrigger className="mt-1.5 w-full max-w-xs">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {LOCALES.map((l) => (
                  <SelectItem key={l} value={l}>{LOCALE_LABELS[l]}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
