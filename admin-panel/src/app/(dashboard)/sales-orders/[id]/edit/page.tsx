"use client";

import { use } from "react";

export default function EditSalesOrderPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  use(params);
  return (
    <p className="text-muted-foreground">
      Draft buyurtmalarni tahrirlash — backend PUT /sales-orders/{`{id}`} orqali.
      Form keyingi iteratsiyada to&apos;ldiriladi.
    </p>
  );
}
