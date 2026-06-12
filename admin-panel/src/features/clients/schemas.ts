import { z } from "zod";

export const clientCreateSchema = z.object({
  code: z.string().min(1, "validation.codeRequired"),
  name: z.string().min(1, "validation.nameRequired"),
  contact_person: z.string().optional(),
  phone: z.string().optional(),
  email: z.string().email("validation.emailInvalid").optional().or(z.literal("")),
  address: z.string().optional(),
  notes: z.string().optional(),
});

export const clientUpdateSchema = clientCreateSchema.partial();

export const clientFields = [
  { name: "code" as const, label: "fields.code", required: true },
  { name: "name" as const, label: "fields.name", required: true },
  { name: "contact_person" as const, label: "fields.contactPerson" },
  { name: "phone" as const, label: "fields.phone" },
  { name: "email" as const, label: "fields.email", type: "email" as const },
  { name: "address" as const, label: "fields.address", type: "textarea" as const },
  { name: "notes" as const, label: "fields.notes", type: "textarea" as const },
];
