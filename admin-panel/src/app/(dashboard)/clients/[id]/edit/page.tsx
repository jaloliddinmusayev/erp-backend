"use client";

import { use } from "react";
import { ResourceFormPage } from "@/components/crud/resource-form-page";
import { clientsResource } from "@/config/resources/clients";

export default function EditClientPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  return <ResourceFormPage config={clientsResource} mode="edit" id={Number(id)} />;
}
