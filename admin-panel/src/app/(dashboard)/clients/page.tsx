"use client";

import { ResourceListPage } from "@/components/crud/resource-list-page";
import { clientsResource } from "@/config/resources/clients";

export default function ClientsPage() {
  return <ResourceListPage config={clientsResource} />;
}
