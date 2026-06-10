import type { ResourceConfig } from "./types";
import { warehouseColumns } from "@/features/warehouses/columns";
import * as warehousesApi from "@/lib/api/modules/warehouses";
import type { Warehouse } from "@/types/api";

export const warehousesResource: ResourceConfig<Warehouse> = {
  key: "warehouses",
  label: "Warehouses",
  labelSingular: "Warehouse",
  basePath: "/warehouses",
  permissions: { read: "warehouses:read", write: "warehouses:write" },
  list: warehousesApi.listWarehouses,
  create: warehousesApi.createWarehouse,
  columns: warehouseColumns,
  supportsCreate: true,
  supportsEdit: false,
  supportsView: false,
};
