"use client";

import Link from "next/link";
import type { ColumnDef } from "@tanstack/react-table";
import type { Invoice } from "@/types/api";
import { StatusBadge } from "@/components/shared/status-badge";
import { formatMoney, formatDate } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Eye, Pencil } from "lucide-react";

export const invoiceColumns: ColumnDef<Invoice, unknown>[] = [
  { accessorKey: "invoice_number", header: "Raqam" },
  {
    accessorKey: "client.name",
    header: "Mijoz",
    cell: ({ row }) => row.original.client?.name ?? "—",
  },
  {
    accessorKey: "invoice_date",
    header: "Sana",
    cell: ({ row }) => formatDate(row.original.invoice_date),
  },
  {
    accessorKey: "status",
    header: "Holat",
    cell: ({ row }) => <StatusBadge status={row.original.status} />,
  },
  {
    accessorKey: "outstanding_amount",
    header: "Qarz",
    cell: ({ row }) => formatMoney(row.original.outstanding_amount),
  },
  {
    id: "actions",
    header: "",
    cell: ({ row }) => (
      <div className="flex justify-end gap-1">
        <Button variant="ghost" size="icon" asChild>
          <Link href={`/invoices/${row.original.id}`}><Eye className="h-4 w-4" /></Link>
        </Button>
        {row.original.status === "draft" && (
          <Button variant="ghost" size="icon" asChild>
            <Link href={`/invoices/${row.original.id}/edit`}><Pencil className="h-4 w-4" /></Link>
          </Button>
        )}
      </div>
    ),
  },
];
