import { apiClient } from "../client";
import type { AgingInvoiceDetail, AgingResponse } from "@/types/api";

export async function getAging(asOfDate?: string) {
  const { data } = await apiClient.get<AgingResponse>("/receivables/aging", {
    params: asOfDate ? { as_of_date: asOfDate } : undefined,
  });
  return data;
}

export async function getAgingInvoices(asOfDate?: string, clientId?: number) {
  const { data } = await apiClient.get<AgingInvoiceDetail[]>("/receivables/aging/invoices", {
    params: {
      ...(asOfDate ? { as_of_date: asOfDate } : {}),
      ...(clientId ? { client_id: clientId } : {}),
    },
  });
  return data;
}

export async function getClientStatement(
  clientId: number,
  dateFrom?: string,
  dateTo?: string,
) {
  const { data } = await apiClient.get(
    `/receivables/statements/client/${clientId}`,
    { params: { date_from: dateFrom, date_to: dateTo } },
  );
  return data;
}
