"use client";

import { Badge } from "@/components/ui/badge";
import { useT } from "@/lib/i18n";

const STATUS_VARIANTS: Record<string, "default" | "secondary" | "success" | "warning" | "destructive"> = {
  draft: "secondary",
  confirmed: "default",
  sent_to_wms: "default",
  in_progress: "warning",
  completed: "success",
  cancelled: "destructive",
  issued: "default",
  partially_paid: "warning",
  paid: "success",
  pending: "secondary",
  partial: "warning",
  fulfilled: "success",
  active: "success",
  inactive: "secondary",
  not_sent: "secondary",
  sent: "default",
  acknowledged: "success",
  failed: "destructive",
};

export function StatusBadge({ status }: { status: string }) {
  const t = useT();
  const key = status.toLowerCase().replace(/\s+/g, "_");
  const variant = STATUS_VARIANTS[key] ?? "outline";
  const translated = t(`status.${key}`);
  // translate() returns the key itself for unknown statuses — fall back to raw text.
  const label = translated === `status.${key}` ? status.replace(/_/g, " ") : translated;
  return (
    <Badge variant={variant} className="capitalize">
      {label}
    </Badge>
  );
}
