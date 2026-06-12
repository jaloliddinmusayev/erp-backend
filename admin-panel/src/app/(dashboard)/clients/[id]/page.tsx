"use client";

import { use } from "react";
import { ResourceDetailPage } from "@/components/crud/resource-detail-page";
import { clientsResource } from "@/config/resources/clients";
import { StatusBadge } from "@/components/shared/status-badge";
import type { Client } from "@/types/api";

export default function ClientDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  return (
    <ResourceDetailPage
      config={clientsResource}
      id={Number(id)}
      getFields={(c: Client) => [
        { label: "fields.code", value: c.code },
        { label: "fields.name", value: c.name },
        { label: "fields.contactPerson", value: c.contact_person ?? "—" },
        { label: "fields.phone", value: c.phone ?? "—" },
        { label: "fields.email", value: c.email ?? "—" },
        { label: "fields.address", value: c.address ?? "—" },
        { label: "fields.notes", value: c.notes ?? "—" },
        {
          label: "fields.status",
          value: <StatusBadge status={c.is_active ? "active" : "inactive"} />,
        },
      ]}
    />
  );
}
