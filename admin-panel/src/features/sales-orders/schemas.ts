import { z } from "zod";

export const salesOrderCreateSchema = z.object({
  client_id: z.number().min(1, "Mijoz tanlang"),
  order_number: z.string().min(1, "Raqam talab qilinadi"),
  order_date: z.string().min(1, "Sana talab qilinadi"),
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
    .min(1, "Kamida bitta qator"),
});

export type SalesOrderCreateForm = z.infer<typeof salesOrderCreateSchema>;
