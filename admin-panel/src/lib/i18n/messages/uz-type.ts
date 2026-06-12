import type { uz } from "./uz";

/** Recursively maps the uz dictionary shape so en/ru must provide every key. */
type DeepMessages<T> = {
  [K in keyof T]: T[K] extends string ? string : DeepMessages<T[K]>;
};

export type Messages = DeepMessages<typeof uz>;
