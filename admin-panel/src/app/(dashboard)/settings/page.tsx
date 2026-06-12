"use client";

import { useTheme } from "next-themes";
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
    <div className="space-y-6">
      <PageHeader title={t("nav.settings")} description={t("settings.description")} />

      <Card>
        <CardHeader><CardTitle>{t("settings.profile")}</CardTitle></CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-2">
          <div><Label className="text-muted-foreground">{t("fields.fullName")}</Label><p className="mt-1 font-medium">{user?.full_name}</p></div>
          <div><Label className="text-muted-foreground">{t("fields.email")}</Label><p className="mt-1 font-medium">{user?.email}</p></div>
          <div><Label className="text-muted-foreground">{t("fields.role")}</Label><p className="mt-1 font-medium">{user?.role.name}</p></div>
          <div><Label className="text-muted-foreground">{t("settings.tenantId")}</Label><p className="mt-1 font-medium">{user?.company_id}</p></div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>{t("settings.appearance")}</CardTitle></CardHeader>
        <CardContent className="grid gap-6 sm:grid-cols-2">
          <div>
            <Label>{t("settings.theme")}</Label>
            <Select value={theme} onValueChange={setTheme}>
              <SelectTrigger className="mt-1.5 w-48"><SelectValue /></SelectTrigger>
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
              <SelectTrigger className="mt-1.5 w-48"><SelectValue /></SelectTrigger>
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
