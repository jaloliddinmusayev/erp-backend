"use client";

import type { ColumnDef } from "@tanstack/react-table";
import type { Warehouse } from "@/types/api";
import { StatusBadge } from "@/components/shared/status-badge";

export const warehouseColumns: ColumnDef<Warehouse, unknown>[] = [
  { accessorKey: "code", header: "Kod" },
  { accessorKey: "name", header: "Nom" },
  { accessorKey: "address", header: "Manzil", cell: ({ row }) => row.original.address ?? "—" },
  {
    accessorKey: "is_active",
    header: "Holat",
    cell: ({ row }) => (
      <StatusBadge status={row.original.is_active ? "active" : "inactive"} />
    ),
  },
];
