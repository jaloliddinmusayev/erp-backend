"use client";

import { ResourceFormPage } from "@/components/crud/resource-form-page";
import { clientsResource } from "@/config/resources/clients";

export default function NewClientPage() {
  return <ResourceFormPage config={clientsResource} mode="create" />;
}
