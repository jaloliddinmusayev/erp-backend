"use client";

import Link from "next/link";
import type { ColumnDef } from "@tanstack/react-table";
import type { Client } from "@/types/api";
import { StatusBadge } from "@/components/shared/status-badge";
import { Button } from "@/components/ui/button";
import { Eye, Pencil } from "lucide-react";

export const clientColumns: ColumnDef<Client, unknown>[] = [
  { accessorKey: "code", header: "Kod" },
  { accessorKey: "name", header: "Nom" },
  { accessorKey: "phone", header: "Telefon", cell: ({ row }) => row.original.phone ?? "—" },
  { accessorKey: "email", header: "Email", cell: ({ row }) => row.original.email ?? "—" },
  {
    accessorKey: "is_active",
    header: "Holat",
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
