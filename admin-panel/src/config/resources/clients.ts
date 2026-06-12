import type { ResourceConfig } from "./types";
import { clientColumns } from "@/features/clients/columns";
import { clientCreateSchema, clientFields, clientUpdateSchema } from "@/features/clients/schemas";
import * as clientsApi from "@/lib/api/modules/clients";
import type { Client } from "@/types/api";

export const clientsResource: ResourceConfig<Client> = {
  key: "clients",
  labelKey: "modules.clients",
  labelSingularKey: "modules.client",
  basePath: "/clients",
  permissions: { read: "clients:read", write: "clients:write" },
  list: clientsApi.listClients,
  get: clientsApi.getClient,
  create: clientsApi.createClient,
  update: clientsApi.updateClient,
  columns: clientColumns,
  createSchema: clientCreateSchema,
  updateSchema: clientUpdateSchema,
  createFields: clientFields,
  updateFields: clientFields,
  searchKey: "search",
  supportsCreate: true,
  supportsEdit: true,
  supportsView: true,
};
