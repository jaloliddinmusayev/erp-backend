import { Badge } from "@/components/ui/badge";

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
};

export function StatusBadge({ status }: { status: string }) {
  const key = status.toLowerCase().replace(/\s+/g, "_");
  const variant = STATUS_VARIANTS[key] ?? "outline";
  return (
    <Badge variant={variant} className="capitalize">
      {status.replace(/_/g, " ")}
    </Badge>
  );
}
