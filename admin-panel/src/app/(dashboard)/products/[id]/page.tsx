"use client";

import { use } from "react";
import { ResourceDetailPage } from "@/components/crud/resource-detail-page";
import { productsResource } from "@/config/resources/products";
import { StatusBadge } from "@/components/shared/status-badge";
import type { Product } from "@/types/api";

export default function ProductDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const numId = Number(id);

  return (
    <ResourceDetailPage
      config={productsResource}
      id={numId}
      getFields={(p: Product) => [
        { label: "fields.code", value: p.code },
        { label: "fields.name", value: p.name },
        { label: "fields.category", value: p.category?.name },
        { label: "fields.unit", value: p.base_unit?.name },
        { label: "fields.barcode", value: p.barcode ?? "—" },
        { label: "fields.description", value: p.description ?? "—" },
        {
          label: "fields.status",
          value: <StatusBadge status={p.is_active ? "active" : "inactive"} />,
        },
      ]}
    />
  );
}
