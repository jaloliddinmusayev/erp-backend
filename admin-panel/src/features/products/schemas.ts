import { z } from "zod";

export const productCreateSchema = z.object({
  name: z.string().min(1, "Nom talab qilinadi"),
  code: z.string().min(1, "Kod talab qilinadi"),
  category_id: z.number().min(1, "Kategoriya tanlang"),
  base_unit_id: z.number().min(1, "Birlik tanlang"),
  barcode: z.string().optional(),
  description: z.string().optional(),
});

export const productUpdateSchema = productCreateSchema.partial().extend({
  name: z.string().min(1).optional(),
  code: z.string().min(1).optional(),
});

export type ProductCreateForm = z.infer<typeof productCreateSchema>;
export type ProductUpdateForm = z.infer<typeof productUpdateSchema>;
