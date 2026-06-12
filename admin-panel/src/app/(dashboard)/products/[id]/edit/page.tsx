"use client";

import { use } from "react";
import { useQuery } from "@tanstack/react-query";
import { ResourceFormPage } from "@/components/crud/resource-form-page";
import { productsResource } from "@/config/resources/products";
import { listCategories, listUnits } from "@/lib/api/modules/catalog";
import type { FormFieldConfig } from "@/components/forms/resource-form";
import type { ProductUpdateForm } from "@/features/products/schemas";

export default function EditProductPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { data: categories = [] } = useQuery({
    queryKey: ["categories"],
    queryFn: () => listCategories({ skip: 0, limit: 200 }),
  });
  const { data: units = [] } = useQuery({
    queryKey: ["units"],
    queryFn: () => listUnits({ skip: 0, limit: 200 }),
  });

  const fields = (): FormFieldConfig<ProductUpdateForm>[] => [
    { name: "code", label: "fields.code" },
    { name: "name", label: "fields.name" },
    {
      name: "category_id",
      label: "fields.category",
      type: "select",
      options: categories.map((c) => ({ label: c.name, value: String(c.id) })),
    },
    {
      name: "base_unit_id",
      label: "fields.unit",
      type: "select",
      options: units.map((u) => ({ label: u.name, value: String(u.id) })),
    },
    { name: "barcode", label: "fields.barcode" },
    { name: "description", label: "fields.description", type: "textarea" },
  ];

  return (
    <ResourceFormPage
      config={productsResource}
      mode="edit"
      id={Number(id)}
      extraFields={() => fields() as never}
    />
  );
}
