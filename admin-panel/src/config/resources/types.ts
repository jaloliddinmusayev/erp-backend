import type { ColumnDef } from "@tanstack/react-table";
import type { ZodType } from "zod";
import type { Permission } from "../permissions";
import type { FormFieldConfig } from "@/components/forms/resource-form";
import type { ListParams } from "@/lib/api/client";

export interface ResourceConfig<TList, TDetail = TList> {
  key: string;
  label: string;
  labelSingular: string;
  basePath: string;
  permissions: { read: Permission; write: Permission };
  list: (params: ListParams) => Promise<TList[]>;
  get?: (id: number) => Promise<TDetail>;
  create?: (body: Record<string, unknown>) => Promise<TDetail>;
  update?: (id: number, body: Record<string, unknown>) => Promise<TDetail>;
  columns: ColumnDef<TList, unknown>[];
  createSchema?: ZodType;
  updateSchema?: ZodType;
  createFields?: FormFieldConfig<Record<string, unknown>>[];
  updateFields?: FormFieldConfig<Record<string, unknown>>[];
  searchKey?: string;
  supportsEdit?: boolean;
  supportsCreate?: boolean;
  supportsView?: boolean;
}
