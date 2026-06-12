import { uz } from "./messages/uz";
import { en } from "./messages/en";
import { ru } from "./messages/ru";
import { useLocaleStore, type Locale } from "./locale-store";
import type { Messages } from "./messages/uz-type";

const MESSAGES: Record<Locale, Messages> = { uz, en, ru };

type DotPaths<T> = {
  [K in keyof T & string]: T[K] extends string ? K : `${K}.${DotPaths<T[K]>}`;
}[keyof T & string];

/** All valid translation keys, e.g. "common.save" */
export type MessageKey = DotPaths<typeof uz>;

/** A MessageKey with autocomplete, but any string allowed (raw-text fallback). */
export type TKey = MessageKey | (string & {});

export type TranslateParams = Record<string, string | number>;

function lookup(dict: Messages, key: string): string | undefined {
  let current: unknown = dict;
  for (const part of key.split(".")) {
    if (current !== null && typeof current === "object" && part in current) {
      current = (current as Record<string, unknown>)[part];
    } else {
      return undefined;
    }
  }
  return typeof current === "string" ? current : undefined;
}

export function translate(locale: Locale, key: TKey, params?: TranslateParams): string {
  const template = lookup(MESSAGES[locale], key) ?? lookup(MESSAGES.uz, key) ?? key;
  if (!params) return template;
  return template.replace(/\{(\w+)\}/g, (match, name) =>
    name in params ? String(params[name]) : match,
  );
}

export function getLocale(): Locale {
  return useLocaleStore.getState().locale;
}

/** Translate outside React render (toasts, error helpers). Uses the current store locale. */
export function tGlobal(key: TKey, params?: TranslateParams): string {
  return translate(getLocale(), key, params);
}
