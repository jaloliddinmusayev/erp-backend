"use client";

import { use } from "react";
import { useT } from "@/lib/i18n";

export default function EditSalesOrderPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  use(params);
  const t = useT();
  return <p className="text-muted-foreground">{t("common.editNotReady")}</p>;
}
