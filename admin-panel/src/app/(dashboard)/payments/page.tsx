"use client";

import { ResourceListPage } from "@/components/crud/resource-list-page";
import { paymentsResource } from "@/config/resources/payments";

export default function PaymentsPage() {
  return <ResourceListPage config={paymentsResource} />;
}
