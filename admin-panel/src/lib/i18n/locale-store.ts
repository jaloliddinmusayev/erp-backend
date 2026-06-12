import { create } from "zustand";
import { persist } from "zustand/middleware";

export type Locale = "uz" | "en" | "ru";

export const LOCALES: Locale[] = ["uz", "en", "ru"];

export const LOCALE_TAGS: Record<Locale, string> = {
  uz: "uz-UZ",
  en: "en-US",
  ru: "ru-RU",
};

export const LOCALE_LABELS: Record<Locale, string> = {
  uz: "O'zbekcha",
  en: "English",
  ru: "Русский",
};

interface LocaleState {
  locale: Locale;
  setLocale: (locale: Locale) => void;
}

export const useLocaleStore = create<LocaleState>()(
  persist(
    (set) => ({
      locale: "uz",
      setLocale: (locale) => set({ locale }),
    }),
    { name: "erp-locale" },
  ),
);
