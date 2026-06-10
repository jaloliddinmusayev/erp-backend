"use client";

import Link from "next/link";
import type { ColumnDef } from "@tanstack/react-table";
import type { Payment } from "@/types/api";
import { formatMoney, formatDate } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Eye } from "lucide-react";

export const paymentColumns: ColumnDef<Payment, unknown>[] = [
  { accessorKey: "id", header: "ID" },
  {
    accessorKey: "client.name",
    header: "Mijoz",
    cell: ({ row }) => row.original.client?.name ?? "—",
  },
  {
    accessorKey: "amount",
    header: "Summa",
    cell: ({ row }) => formatMoney(row.original.amount),
  },
  {
    accessorKey: "payment_date",
    header: "Sana",
    cell: ({ row }) => formatDate(row.original.payment_date),
  },
  { accessorKey: "payment_method", header: "Usul" },
  {
    id: "actions",
    header: "",
    cell: ({ row }) => (
      <Button variant="ghost" size="icon" asChild>
        <Link href={`/payments/${row.original.id}`}><Eye className="h-4 w-4" /></Link>
      </Button>
    ),
  },
];
