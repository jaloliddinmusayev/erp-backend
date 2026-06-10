"use client";

import { ResourceListPage } from "@/components/crud/resource-list-page";
import { invoicesResource } from "@/config/resources/invoices";

export default function InvoicesPage() {
  return <ResourceListPage config={invoicesResource} />;
}
