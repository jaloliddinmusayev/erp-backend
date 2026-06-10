"use client";

import { ResourceListPage } from "@/components/crud/resource-list-page";
import { usersResource } from "@/config/resources/users";

export default function UsersPage() {
  return <ResourceListPage config={usersResource} />;
}
