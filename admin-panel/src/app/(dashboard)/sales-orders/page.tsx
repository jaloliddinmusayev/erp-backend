"use client";

import { ResourceListPage } from "@/components/crud/resource-list-page";
import { salesOrdersResource } from "@/config/resources/sales-orders";

export default function SalesOrdersPage() {
  return <ResourceListPage config={salesOrdersResource} />;
}
