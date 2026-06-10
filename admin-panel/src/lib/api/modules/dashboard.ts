import { parseMoney } from "@/lib/utils";
import type { DashboardStats } from "@/types/api";
import { listClients } from "./clients";
import { listInvoices } from "./invoices";
import { listPayments } from "./payments";
import { listProducts } from "./products";
import { listSalesOrders } from "./sales-orders";

const LIMIT = 500;

export async function fetchDashboardStats(): Promise<DashboardStats> {
  const [products, clients, orders, invoices, payments] = await Promise.all([
    listProducts({ skip: 0, limit: LIMIT, is_active: true }),
    listClients({ skip: 0, limit: LIMIT, is_active: true }),
    listSalesOrders({ skip: 0, limit: LIMIT, is_active: true }),
    listInvoices({ skip: 0, limit: LIMIT, is_active: true }),
    listPayments({ skip: 0, limit: LIMIT, is_active: true }),
  ]);

  const openOrders = orders.filter(
    (o) =>
      !["completed", "cancelled"].includes(o.status) && o.is_active,
  ).length;

  const invoicesOutstanding = invoices
    .filter(
      (inv) =>
        inv.is_active &&
        !["draft", "cancelled", "paid"].includes(inv.status) &&
        parseMoney(inv.outstanding_amount) > 0,
    )
    .reduce((sum, inv) => sum + parseMoney(inv.outstanding_amount), 0);

  const paymentsReceived = payments
    .filter((p) => p.is_active)
    .reduce((sum, p) => sum + parseMoney(p.amount), 0);

  return {
    totalProducts: products.length,
    totalClients: clients.length,
    totalSalesOrders: orders.length,
    openOrders,
    invoicesOutstanding,
    paymentsReceived,
  };
}
