"use client";

import { useQuery } from "@tanstack/react-query";
import { ResourceFormPage } from "@/components/crud/resource-form-page";
import { productsResource } from "@/config/resources/products";
import { listCategories, listUnits } from "@/lib/api/modules/catalog";
import type { FormFieldConfig } from "@/components/forms/resource-form";
import type { ProductCreateForm } from "@/features/products/schemas";

export default function NewProductPage() {
  const { data: categories = [] } = useQuery({
    queryKey: ["categories"],
    queryFn: () => listCategories({ skip: 0, limit: 200 }),
  });
  const { data: units = [] } = useQuery({
    queryKey: ["units"],
    queryFn: () => listUnits({ skip: 0, limit: 200 }),
  });

  const fields = (): FormFieldConfig<ProductCreateForm>[] => [
    { name: "code", label: "fields.code", required: true },
    { name: "name", label: "fields.name", required: true },
    {
      name: "category_id",
      label: "fields.category",
      type: "select",
      required: true,
      options: categories.map((c) => ({ label: c.name, value: String(c.id) })),
    },
    {
      name: "base_unit_id",
      label: "fields.unit",
      type: "select",
      required: true,
      options: units.map((u) => ({ label: u.name, value: String(u.id) })),
    },
    { name: "barcode", label: "fields.barcode" },
    { name: "description", label: "fields.description", type: "textarea" },
  ];

  return (
    <ResourceFormPage
      config={productsResource}
      mode="create"
      extraFields={() => fields() as never}
    />
  );
}
