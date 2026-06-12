"use client";

import Link from "next/link";
import type { ColumnDef } from "@tanstack/react-table";
import type { SalesOrder } from "@/types/api";
import { StatusBadge } from "@/components/shared/status-badge";
import { formatMoney, formatDate } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Eye, Pencil } from "lucide-react";
import { T } from "@/lib/i18n";

export const salesOrderColumns: ColumnDef<SalesOrder, unknown>[] = [
  { accessorKey: "order_number", header: () => <T k="fields.number" /> },
  {
    accessorKey: "client.name",
    header: () => <T k="fields.client" />,
    cell: ({ row }) => row.original.client?.name ?? "—",
  },
  {
    accessorKey: "order_date",
    header: () => <T k="fields.date" />,
    cell: ({ row }) => formatDate(row.original.order_date),
  },
  {
    accessorKey: "status",
    header: () => <T k="fields.status" />,
    cell: ({ row }) => <StatusBadge status={row.original.status} />,
  },
  {
    accessorKey: "total_amount",
    header: () => <T k="fields.amount" />,
    cell: ({ row }) => formatMoney(row.original.total_amount),
  },
  {
    id: "actions",
    header: "",
    cell: ({ row }) => (
      <div className="flex justify-end gap-1">
        <Button variant="ghost" size="icon" asChild>
          <Link href={`/sales-orders/${row.original.id}`}><Eye className="h-4 w-4" /></Link>
        </Button>
        {row.original.status === "draft" && (
          <Button variant="ghost" size="icon" asChild>
            <Link href={`/sales-orders/${row.original.id}/edit`}><Pencil className="h-4 w-4" /></Link>
          </Button>
        )}
      </div>
    ),
  },
];
