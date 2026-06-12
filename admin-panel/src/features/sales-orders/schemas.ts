import { z } from "zod";

export const salesOrderCreateSchema = z.object({
  client_id: z.number().min(1, "validation.clientRequired"),
  order_number: z.string().min(1, "validation.numberRequired"),
  order_date: z.string().min(1, "validation.dateRequired"),
  branch_id: z.number().optional(),
  notes: z.string().optional(),
  items: z
    .array(
      z.object({
        product_id: z.number().min(1),
        ordered_qty: z.number().positive(),
        unit_price: z.number().min(0),
        notes: z.string().optional(),
      }),
    )
    .min(1, "validation.itemsRequired"),
});

export type SalesOrderCreateForm = z.infer<typeof salesOrderCreateSchema>;
