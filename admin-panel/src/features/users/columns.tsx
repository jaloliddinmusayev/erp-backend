"use client";

import type { ColumnDef } from "@tanstack/react-table";
import type { User } from "@/types/api";
import { StatusBadge } from "@/components/shared/status-badge";

export const userColumns: ColumnDef<User, unknown>[] = [
  { accessorKey: "full_name", header: "Ism" },
  { accessorKey: "email", header: "Email" },
  { accessorKey: "role_id", header: "Rol ID" },
  {
    accessorKey: "is_active",
    header: "Holat",
    cell: ({ row }) => (
      <StatusBadge status={row.original.is_active ? "active" : "inactive"} />
    ),
  },
];
