"use client";

import Link from "next/link";
import type { ColumnDef } from "@tanstack/react-table";
import type { Invoice } from "@/types/api";
import { StatusBadge } from "@/components/shared/status-badge";
import { formatMoney, formatDate } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Eye, Pencil } from "lucide-react";
import { T } from "@/lib/i18n";

export const invoiceColumns: ColumnDef<Invoice, unknown>[] = [
  { accessorKey: "invoice_number", header: () => <T k="fields.number" /> },
  {
    accessorKey: "client.name",
    header: () => <T k="fields.client" />,
    cell: ({ row }) => row.original.client?.name ?? "—",
  },
  {
    accessorKey: "invoice_date",
    header: () => <T k="fields.date" />,
    cell: ({ row }) => formatDate(row.original.invoice_date),
  },
  {
    accessorKey: "status",
    header: () => <T k="fields.status" />,
    cell: ({ row }) => <StatusBadge status={row.original.status} />,
  },
  {
    accessorKey: "outstanding_amount",
    header: () => <T k="fields.outstanding" />,
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
