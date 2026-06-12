"use client";

import Link from "next/link";
import type { ColumnDef } from "@tanstack/react-table";
import type { Client } from "@/types/api";
import { StatusBadge } from "@/components/shared/status-badge";
import { Button } from "@/components/ui/button";
import { Eye, Pencil } from "lucide-react";
import { T } from "@/lib/i18n";

export const clientColumns: ColumnDef<Client, unknown>[] = [
  { accessorKey: "code", header: () => <T k="fields.code" /> },
  { accessorKey: "name", header: () => <T k="fields.name" /> },
  { accessorKey: "phone", header: () => <T k="fields.phone" />, cell: ({ row }) => row.original.phone ?? "—" },
  { accessorKey: "email", header: () => <T k="fields.email" />, cell: ({ row }) => row.original.email ?? "—" },
  {
    accessorKey: "is_active",
    header: () => <T k="fields.status" />,
    cell: ({ row }) => (
      <StatusBadge status={row.original.is_active ? "active" : "inactive"} />
    ),
  },
  {
    id: "actions",
    header: "",
    cell: ({ row }) => (
      <div className="flex justify-end gap-1">
        <Button variant="ghost" size="icon" asChild>
          <Link href={`/clients/${row.original.id}`}><Eye className="h-4 w-4" /></Link>
        </Button>
        <Button variant="ghost" size="icon" asChild>
          <Link href={`/clients/${row.original.id}/edit`}><Pencil className="h-4 w-4" /></Link>
        </Button>
      </div>
    ),
  },
];
