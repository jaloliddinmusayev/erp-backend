"use client";

import { use } from "react";
import { ClientFormPage } from "@/features/clients/client-form-page";

export default function EditClientPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  return <ClientFormPage mode="edit" id={Number(id)} />;
}
