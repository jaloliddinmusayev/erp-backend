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
        { label: "Kod", value: p.code },
        { label: "Nom", value: p.name },
        { label: "Kategoriya", value: p.category?.name },
        { label: "Birlik", value: p.base_unit?.name },
        { label: "Barcode", value: p.barcode ?? "—" },
        { label: "Tavsif", value: p.description ?? "—" },
        {
          label: "Holat",
          value: <StatusBadge status={p.is_active ? "active" : "inactive"} />,
        },
      ]}
    />
  );
}
