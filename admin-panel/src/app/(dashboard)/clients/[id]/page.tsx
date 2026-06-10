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
        { label: "Kod", value: c.code },
        { label: "Nom", value: c.name },
        { label: "Mas'ul", value: c.contact_person ?? "—" },
        { label: "Telefon", value: c.phone ?? "—" },
        { label: "Email", value: c.email ?? "—" },
        { label: "Manzil", value: c.address ?? "—" },
        { label: "Izoh", value: c.notes ?? "—" },
        {
          label: "Holat",
          value: <StatusBadge status={c.is_active ? "active" : "inactive"} />,
        },
      ]}
    />
  );
}
