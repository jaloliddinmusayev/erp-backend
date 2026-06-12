"use client";

import { useCallback } from "react";
import { useLocaleStore, type Locale } from "./locale-store";
import { translate, type TKey, type TranslateParams } from "./translate";

export { useLocaleStore, LOCALES, LOCALE_TAGS, LOCALE_LABELS } from "./locale-store";
export type { Locale } from "./locale-store";
export { translate, getLocale, tGlobal } from "./translate";
export type { MessageKey, TKey, TranslateParams } from "./translate";

/** Reactive current locale. */
export function useLocale(): Locale {
  return useLocaleStore((s) => s.locale);
}

/** Returns a `t(key, params?)` translator bound to the current locale. */
export function useT() {
  const locale = useLocaleStore((s) => s.locale);
  return useCallback(
    (key: TKey, params?: TranslateParams) => translate(locale, key, params),
    [locale],
  );
}

/** Inline translated text — handy for column headers and config-driven labels. */
export function T({ k, params }: { k: TKey; params?: TranslateParams }) {
  const t = useT();
  return <>{t(k, params)}</>;
}
