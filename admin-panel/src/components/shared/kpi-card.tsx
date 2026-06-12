import { type LucideIcon } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { KPI_ACCENT_STYLES, type KpiAccent } from "@/config/design";
import { cn } from "@/lib/utils";

interface KpiCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  description?: string;
  loading?: boolean;
  accent?: KpiAccent;
  className?: string;
  money?: boolean;
}

export function KpiCard({
  title,
  value,
  icon: Icon,
  description,
  loading,
  accent = "indigo",
  className,
  money,
}: KpiCardProps) {
  const styles = KPI_ACCENT_STYLES[accent];

  return (
    <Card
      className={cn(
        "overflow-hidden shadow-sm ring-1 ring-border/50 transition-shadow hover:shadow-md",
        styles.ring,
        className,
      )}
    >
      <CardContent className="p-5">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0 flex-1 space-y-2">
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            {loading ? (
              <Skeleton className="h-8 w-24" />
            ) : (
              <p
                className={cn(
                  "text-2xl font-bold tracking-tight",
                  money && "tabular-nums",
                )}
              >
                {value}
              </p>
            )}
            {description && (
              <p className="text-xs text-muted-foreground">{description}</p>
            )}
          </div>
          <div
            className={cn(
              "flex h-10 w-10 shrink-0 items-center justify-center rounded-xl",
              styles.icon,
            )}
          >
            <Icon className="h-5 w-5" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
