"use client";

import { ResourceListPage } from "@/components/crud/resource-list-page";
import { warehousesResource } from "@/config/resources/warehouses";

export default function WarehousesPage() {
  return <ResourceListPage config={warehousesResource} />;
}
