"use client";

import { use } from "react";
import { ResourceDetailPage } from "@/components/crud/resource-detail-page";
import { paymentsResource } from "@/config/resources/payments";
import { formatMoney, formatDate } from "@/lib/utils";
import type { Payment } from "@/types/api";

export default function PaymentDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  return (
    <ResourceDetailPage
      config={paymentsResource}
      id={Number(id)}
      getFields={(p: Payment) => [
        { label: "Mijoz", value: p.client?.name },
        { label: "Summa", value: formatMoney(p.amount) },
        { label: "Sana", value: formatDate(p.payment_date) },
        { label: "Usul", value: p.payment_method },
        { label: "Referens", value: p.reference_number ?? "—" },
        { label: "Izoh", value: p.notes ?? "—" },
      ]}
    />
  );
}
