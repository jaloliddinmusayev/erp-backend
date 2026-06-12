"use client";

import type { ColumnDef } from "@tanstack/react-table";
import type { Warehouse } from "@/types/api";
import { StatusBadge } from "@/components/shared/status-badge";
import { T } from "@/lib/i18n";

export const warehouseColumns: ColumnDef<Warehouse, unknown>[] = [
  { accessorKey: "code", header: () => <T k="fields.code" /> },
  { accessorKey: "name", header: () => <T k="fields.name" /> },
  { accessorKey: "address", header: () => <T k="fields.address" />, cell: ({ row }) => row.original.address ?? "—" },
  {
    accessorKey: "is_active",
    header: () => <T k="fields.status" />,
    cell: ({ row }) => (
      <StatusBadge status={row.original.is_active ? "active" : "inactive"} />
    ),
  },
];
