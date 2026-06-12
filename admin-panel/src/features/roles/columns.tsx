"use client";

import type { ColumnDef } from "@tanstack/react-table";
import type { Role } from "@/types/api";
import { StatusBadge } from "@/components/shared/status-badge";
import { T } from "@/lib/i18n";

export const roleColumns: ColumnDef<Role, unknown>[] = [
  { accessorKey: "code", header: () => <T k="fields.code" /> },
  { accessorKey: "name", header: () => <T k="fields.name" /> },
  { accessorKey: "description", header: () => <T k="fields.description" />, cell: ({ row }) => row.original.description ?? "—" },
  {
    accessorKey: "is_active",
    header: () => <T k="fields.status" />,
    cell: ({ row }) => (
      <StatusBadge status={row.original.is_active ? "active" : "inactive"} />
    ),
  },
];
