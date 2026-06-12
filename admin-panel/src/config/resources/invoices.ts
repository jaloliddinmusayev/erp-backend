import type { ResourceConfig } from "./types";
import { invoiceColumns } from "@/features/invoices/columns";
import * as invoicesApi from "@/lib/api/modules/invoices";
import type { Invoice } from "@/types/api";

export const invoicesResource: ResourceConfig<Invoice> = {
  key: "invoices",
  labelKey: "modules.invoices",
  labelSingularKey: "modules.invoice",
  basePath: "/invoices",
  permissions: { read: "invoices:read", write: "invoices:write" },
  list: invoicesApi.listInvoices,
  get: invoicesApi.getInvoice,
  create: invoicesApi.createInvoice,
  update: invoicesApi.updateInvoice,
  columns: invoiceColumns,
  searchKey: "search",
  supportsCreate: true,
  supportsEdit: true,
  supportsView: true,
};
