import { z } from "zod";

const phoneRegex = /^(\+998|998)?[0-9]{9}$/;

function normalizePhone(value: string): string {
  const normalized = value.replace(/[\s\-()]/g, "");
  if (normalized.startsWith("+998")) return normalized;
  if (normalized.startsWith("998")) return `+${normalized}`;
  return `+998${normalized}`;
}

const optionalNumber = z
  .union([z.number(), z.string(), z.null(), z.undefined()])
  .transform((v) => {
    if (v === "" || v === null || v === undefined) return undefined;
    const n = typeof v === "number" ? v : Number(v);
    return Number.isFinite(n) ? n : undefined;
  });

const clientBaseSchema = z.object({
  code: z.string().min(1, "validation.codeRequired").max(64),
  name: z.string().min(1, "validation.nameRequired").max(255),
  client_type: z.enum(["legal_entity", "individual"]),
  inn: z.string().min(1, "validation.innRequired"),
  legal_name: z.string().max(255).optional().or(z.literal("")),
  contact_person: z.string().max(255).optional().or(z.literal("")),
  phone: z
    .string()
    .optional()
    .or(z.literal(""))
    .refine((v) => !v || phoneRegex.test(v.replace(/[\s\-()]/g, "")), "validation.phoneInvalid")
    .transform((v) => (v ? normalizePhone(v) : undefined)),
  email: z.string().email("validation.emailInvalid").optional().or(z.literal("")),
  region: z.string().max(128).optional().or(z.literal("")),
  city: z.string().max(128).optional().or(z.literal("")),
  district: z.string().max(128).optional().or(z.literal("")),
  address: z.string().optional().or(z.literal("")),
  latitude: optionalNumber,
  longitude: optionalNumber,
  bank_name: z.string().max(255).optional().or(z.literal("")),
  bank_account: z
    .string()
    .optional()
    .or(z.literal(""))
    .refine((v) => !v || /^\d{5,32}$/.test(v), "validation.bankAccountInvalid"),
  bank_mfo: z
    .string()
    .optional()
    .or(z.literal(""))
    .refine((v) => !v || /^\d{5}$/.test(v), "validation.mfoInvalid"),
  notes: z.string().optional().or(z.literal("")),
  is_active: z.boolean(),
});

function validateInnAndCoords(
  data: z.infer<typeof clientBaseSchema>,
  ctx: z.RefinementCtx,
) {
  const inn = data.inn.replace(/\s/g, "");
  if (data.client_type === "legal_entity") {
    if (!/^\d{9}$/.test(inn)) {
      ctx.addIssue({ code: "custom", message: "validation.innLegal", path: ["inn"] });
    }
  } else if (!/^\d{14}$/.test(inn)) {
    ctx.addIssue({ code: "custom", message: "validation.innIndividual", path: ["inn"] });
  }

  const hasLat = data.latitude !== undefined;
  const hasLng = data.longitude !== undefined;
  if (hasLat !== hasLng) {
    ctx.addIssue({ code: "custom", message: "validation.coordsPair", path: ["latitude"] });
  }
  if (hasLat && (data.latitude! < -90 || data.latitude! > 90)) {
    ctx.addIssue({ code: "custom", message: "validation.latitudeInvalid", path: ["latitude"] });
  }
  if (hasLng && (data.longitude! < -180 || data.longitude! > 180)) {
    ctx.addIssue({ code: "custom", message: "validation.longitudeInvalid", path: ["longitude"] });
  }
}

export const clientCreateSchema = clientBaseSchema.superRefine(validateInnAndCoords);

export const clientUpdateSchema = clientCreateSchema;

export type ClientFormValues = z.infer<typeof clientCreateSchema>;

export const clientDefaultValues: ClientFormValues = {
  code: "",
  name: "",
  client_type: "legal_entity",
  inn: "",
  legal_name: "",
  contact_person: "",
  phone: "",
  email: "",
  region: "",
  city: "",
  district: "",
  address: "",
  latitude: undefined,
  longitude: undefined,
  bank_name: "",
  bank_account: "",
  bank_mfo: "",
  notes: "",
  is_active: true,
};

export function clientToFormValues(client: {
  code: string;
  name: string;
  client_type: "legal_entity" | "individual";
  inn: string | null;
  legal_name: string | null;
  contact_person: string | null;
  phone: string | null;
  email: string | null;
  region: string | null;
  city: string | null;
  district: string | null;
  address: string | null;
  latitude: number | string | null;
  longitude: number | string | null;
  bank_name: string | null;
  bank_account: string | null;
  bank_mfo: string | null;
  notes: string | null;
  is_active: boolean;
}): ClientFormValues {
  const lat = client.latitude != null ? Number(client.latitude) : undefined;
  const lng = client.longitude != null ? Number(client.longitude) : undefined;
  return {
    code: client.code,
    name: client.name,
    client_type: client.client_type,
    inn: client.inn ?? "",
    legal_name: client.legal_name ?? "",
    contact_person: client.contact_person ?? "",
    phone: client.phone ?? "",
    email: client.email ?? "",
    region: client.region ?? "",
    city: client.city ?? "",
    district: client.district ?? "",
    address: client.address ?? "",
    latitude: Number.isFinite(lat) ? lat : undefined,
    longitude: Number.isFinite(lng) ? lng : undefined,
    bank_name: client.bank_name ?? "",
    bank_account: client.bank_account ?? "",
    bank_mfo: client.bank_mfo ?? "",
    notes: client.notes ?? "",
    is_active: client.is_active,
  };
}

export function clientFormToPayload(values: ClientFormValues): Record<string, unknown> {
  return {
    code: values.code,
    name: values.name,
    client_type: values.client_type,
    inn: values.inn.replace(/\s/g, ""),
    legal_name: values.legal_name || null,
    contact_person: values.contact_person || null,
    phone: values.phone || null,
    email: values.email || null,
    region: values.region || null,
    city: values.city || null,
    district: values.district || null,
    address: values.address || null,
    latitude: values.latitude ?? null,
    longitude: values.longitude ?? null,
    bank_name: values.bank_name || null,
    bank_account: values.bank_account || null,
    bank_mfo: values.bank_mfo || null,
    notes: values.notes || null,
    is_active: values.is_active,
  };
}
