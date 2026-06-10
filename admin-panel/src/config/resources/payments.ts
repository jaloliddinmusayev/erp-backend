import type { ResourceConfig } from "./types";
import { paymentColumns } from "@/features/payments/columns";
import * as paymentsApi from "@/lib/api/modules/payments";
import type { Payment } from "@/types/api";

export const paymentsResource: ResourceConfig<Payment> = {
  key: "payments",
  label: "Payments",
  labelSingular: "Payment",
  basePath: "/payments",
  permissions: { read: "payments:read", write: "payments:write" },
  list: paymentsApi.listPayments,
  get: paymentsApi.getPayment,
  create: paymentsApi.createPayment,
  columns: paymentColumns,
  searchKey: "search",
  supportsCreate: true,
  supportsEdit: false,
  supportsView: true,
};
