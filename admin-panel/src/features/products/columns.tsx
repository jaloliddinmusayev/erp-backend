"use client";

import Link from "next/link";
import type { ColumnDef } from "@tanstack/react-table";
import type { Product } from "@/types/api";
import { StatusBadge } from "@/components/shared/status-badge";
import { Button } from "@/components/ui/button";
import { Eye, Pencil } from "lucide-react";
import { T } from "@/lib/i18n";

export const productColumns: ColumnDef<Product, unknown>[] = [
  { accessorKey: "code", header: () => <T k="fields.code" /> },
  { accessorKey: "name", header: () => <T k="fields.name" /> },
  {
    accessorKey: "category.name",
    header: () => <T k="fields.category" />,
    cell: ({ row }) => row.original.category?.name ?? "—",
  },
  {
    accessorKey: "base_unit.name",
    header: () => <T k="fields.unit" />,
    cell: ({ row }) => row.original.base_unit?.name ?? "—",
  },
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
          <Link href={`/products/${row.original.id}`}>
            <Eye className="h-4 w-4" />
          </Link>
        </Button>
        <Button variant="ghost" size="icon" asChild>
          <Link href={`/products/${row.original.id}/edit`}>
            <Pencil className="h-4 w-4" />
          </Link>
        </Button>
      </div>
    ),
  },
];
