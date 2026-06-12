"use client";

import { Sparkles } from "lucide-react";
import { useT } from "@/lib/i18n";

export function AuthBrandPanel() {
  const t = useT();

  return (
    <div className="relative hidden w-1/2 flex-col justify-between overflow-hidden bg-gradient-to-br from-indigo-600 via-indigo-700 to-violet-800 p-10 text-white lg:flex">
      <div className="absolute -left-20 -top-20 h-64 w-64 rounded-full bg-white/10 blur-3xl" />
      <div className="absolute -bottom-16 right-0 h-48 w-48 rounded-full bg-violet-400/20 blur-2xl" />
      <div className="relative flex items-center gap-3">
        <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-white/20 backdrop-blur">
          <Sparkles className="h-6 w-6" />
        </div>
        <div>
          <p className="text-lg font-bold tracking-tight">Triad ERP</p>
          <p className="text-sm text-indigo-200">{t("auth.brandSubtitle")}</p>
        </div>
      </div>
      <div className="relative space-y-4">
        <h2 className="text-3xl font-bold leading-tight tracking-tight">
          {t("auth.brandHeadline")}
        </h2>
        <p className="max-w-md text-indigo-100">{t("auth.brandDescription")}</p>
      </div>
      <p className="relative text-sm text-indigo-300">
        © {new Date().getFullYear()} Triad
      </p>
    </div>
  );
}
