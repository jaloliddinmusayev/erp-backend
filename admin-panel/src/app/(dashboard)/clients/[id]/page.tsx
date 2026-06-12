"use client";

import { use } from "react";
import dynamic from "next/dynamic";
import { useRouter } from "next/navigation";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Ban } from "lucide-react";
import { ResourceDetailPage } from "@/components/crud/resource-detail-page";
import { clientsResource } from "@/config/resources/clients";
import { StatusBadge } from "@/components/shared/status-badge";
import { Button } from "@/components/ui/button";
import { PermissionGuard } from "@/components/crud/permission-guard";
import { deactivateClient } from "@/lib/api/modules/clients";
import { onMutationError } from "@/lib/api/errors";
import { useT } from "@/lib/i18n";
import type { Client } from "@/types/api";

const LocationMapView = dynamic(
  () => import("@/features/clients/location-map-view").then((m) => m.LocationMapView),
  { ssr: false, loading: () => <div className="h-56 animate-pulse rounded-xl bg-muted" /> },
);

function formatAddress(c: Client) {
  return [c.region, c.city, c.district, c.address].filter(Boolean).join(", ") || "—";
}

export default function ClientDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const clientId = Number(id);
  const router = useRouter();
  const queryClient = useQueryClient();
  const t = useT();

  const deactivateMut = useMutation({
    mutationFn: () => deactivateClient(clientId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["clients"] });
      queryClient.invalidateQueries({ queryKey: ["clients", clientId] });
      toast.success(t("clients.deactivated"));
      router.refresh();
    },
    onError: onMutationError,
  });

  return (
    <ResourceDetailPage
      config={clientsResource}
      id={clientId}
      actions={
        <PermissionGuard permission="clients:write">
          <Button
            variant="outline"
            onClick={() => {
              if (window.confirm(t("clients.deactivateConfirm"))) {
                deactivateMut.mutate();
              }
            }}
            disabled={deactivateMut.isPending}
          >
            <Ban className="mr-2 h-4 w-4" />
            {t("clients.deactivate")}
          </Button>
        </PermissionGuard>
      }
      getFields={(c: Client) => {
        const lat = c.latitude != null ? Number(c.latitude) : null;
        const lng = c.longitude != null ? Number(c.longitude) : null;
        const hasCoords = lat != null && lng != null && Number.isFinite(lat) && Number.isFinite(lng);

        return [
          { label: "fields.code", value: c.code },
          { label: "fields.name", value: c.name },
          { label: "fields.clientType", value: t(`clientType.${c.client_type}`) },
          { label: "fields.inn", value: c.inn ?? "—" },
          { label: "fields.legalName", value: c.legal_name ?? "—" },
          { label: "fields.contactPerson", value: c.contact_person ?? "—" },
          { label: "fields.phone", value: c.phone ?? "—" },
          { label: "fields.email", value: c.email ?? "—" },
          { label: "fields.region", value: c.region ?? "—" },
          { label: "fields.city", value: c.city ?? "—" },
          { label: "fields.district", value: c.district ?? "—" },
          { label: "fields.address", value: formatAddress(c) },
          { label: "fields.bankName", value: c.bank_name ?? "—" },
          { label: "fields.bankAccount", value: c.bank_account ?? "—" },
          { label: "fields.bankMfo", value: c.bank_mfo ?? "—" },
          { label: "fields.notes", value: c.notes ?? "—" },
          {
            label: "fields.status",
            value: <StatusBadge status={c.is_active ? "active" : "inactive"} />,
          },
          ...(hasCoords
            ? [
                {
                  label: "fields.location",
                  value: (
                    <div className="mt-2 space-y-1">
                      <p className="text-sm tabular-nums text-muted-foreground">
                        {lat!.toFixed(6)}, {lng!.toFixed(6)}
                      </p>
                      <LocationMapView latitude={lat!} longitude={lng!} />
                    </div>
                  ),
                },
              ]
            : []),
        ];
      }}
    />
  );
}
