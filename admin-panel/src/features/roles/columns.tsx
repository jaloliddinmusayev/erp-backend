"use client";

import type { ColumnDef } from "@tanstack/react-table";
import type { Role } from "@/types/api";
import { StatusBadge } from "@/components/shared/status-badge";

export const roleColumns: ColumnDef<Role, unknown>[] = [
  { accessorKey: "code", header: "Kod" },
  { accessorKey: "name", header: "Nom" },
  { accessorKey: "description", header: "Tavsif", cell: ({ row }) => row.original.description ?? "—" },
  {
    accessorKey: "is_active",
    header: "Holat",
    cell: ({ row }) => (
      <StatusBadge status={row.original.is_active ? "active" : "inactive"} />
    ),
  },
];
