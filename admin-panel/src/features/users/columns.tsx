"use client";

import type { ColumnDef } from "@tanstack/react-table";
import type { User } from "@/types/api";
import { StatusBadge } from "@/components/shared/status-badge";
import { T } from "@/lib/i18n";

export const userColumns: ColumnDef<User, unknown>[] = [
  { accessorKey: "full_name", header: () => <T k="fields.fullName" /> },
  { accessorKey: "email", header: () => <T k="fields.email" /> },
  { accessorKey: "role_id", header: () => <T k="fields.roleId" /> },
  {
    accessorKey: "is_active",
    header: () => <T k="fields.status" />,
    cell: ({ row }) => (
      <StatusBadge status={row.original.is_active ? "active" : "inactive"} />
    ),
  },
];
