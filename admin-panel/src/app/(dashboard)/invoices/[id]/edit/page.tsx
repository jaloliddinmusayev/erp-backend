"use client";

import { use } from "react";

export default function EditInvoicePage({ params }: { params: Promise<{ id: string }> }) {
  use(params);
  return <p className="text-muted-foreground">Draft fakturalarni tahrirlash — keyingi iteratsiya.</p>;
}
