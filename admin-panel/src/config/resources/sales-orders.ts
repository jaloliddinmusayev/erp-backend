import type { ResourceConfig } from "./types";
import { salesOrderColumns } from "@/features/sales-orders/columns";
import * as salesOrdersApi from "@/lib/api/modules/sales-orders";
import type { SalesOrder } from "@/types/api";

export const salesOrdersResource: ResourceConfig<SalesOrder> = {
  key: "sales-orders",
  label: "Sales Orders",
  labelSingular: "Sales Order",
  basePath: "/sales-orders",
  permissions: { read: "sales_orders:read", write: "sales_orders:write" },
  list: salesOrdersApi.listSalesOrders,
  get: salesOrdersApi.getSalesOrder,
  create: salesOrdersApi.createSalesOrder,
  update: salesOrdersApi.updateSalesOrder,
  columns: salesOrderColumns,
  searchKey: "search",
  supportsCreate: true,
  supportsEdit: true,
  supportsView: true,
};
