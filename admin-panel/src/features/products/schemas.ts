import { z } from "zod";

export const productCreateSchema = z.object({
  name: z.string().min(1, "validation.nameRequired"),
  code: z.string().min(1, "validation.codeRequired"),
  category_id: z.number().min(1, "validation.categoryRequired"),
  base_unit_id: z.number().min(1, "validation.unitRequired"),
  barcode: z.string().optional(),
  description: z.string().optional(),
});

export const productUpdateSchema = productCreateSchema.partial().extend({
  name: z.string().min(1).optional(),
  code: z.string().min(1).optional(),
});

export type ProductCreateForm = z.infer<typeof productCreateSchema>;
export type ProductUpdateForm = z.infer<typeof productUpdateSchema>;
