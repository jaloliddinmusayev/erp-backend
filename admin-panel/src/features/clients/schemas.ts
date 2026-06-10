import { z } from "zod";

export const clientCreateSchema = z.object({
  code: z.string().min(1, "Kod talab qilinadi"),
  name: z.string().min(1, "Nom talab qilinadi"),
  contact_person: z.string().optional(),
  phone: z.string().optional(),
  email: z.string().email().optional().or(z.literal("")),
  address: z.string().optional(),
  notes: z.string().optional(),
});

export const clientUpdateSchema = clientCreateSchema.partial();

export const clientFields = [
  { name: "code" as const, label: "Kod", required: true },
  { name: "name" as const, label: "Nom", required: true },
  { name: "contact_person" as const, label: "Mas'ul shaxs" },
  { name: "phone" as const, label: "Telefon" },
  { name: "email" as const, label: "Email", type: "email" as const },
  { name: "address" as const, label: "Manzil", type: "textarea" as const },
  { name: "notes" as const, label: "Izoh", type: "textarea" as const },
];
