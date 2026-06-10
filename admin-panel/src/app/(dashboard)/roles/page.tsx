"use client";

import { ResourceListPage } from "@/components/crud/resource-list-page";
import { rolesResource } from "@/config/resources/roles";

export default function RolesPage() {
  return <ResourceListPage config={rolesResource} />;
}
