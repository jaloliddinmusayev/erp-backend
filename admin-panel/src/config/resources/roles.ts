import type { ResourceConfig } from "./types";
import { roleColumns } from "@/features/roles/columns";
import * as rolesApi from "@/lib/api/modules/roles";
import type { Role } from "@/types/api";

export const rolesResource: ResourceConfig<Role> = {
  key: "roles",
  label: "Roles",
  labelSingular: "Role",
  basePath: "/roles",
  permissions: { read: "roles:read", write: "roles:write" },
  list: rolesApi.listRoles,
  create: rolesApi.createRole,
  columns: roleColumns,
  supportsCreate: true,
  supportsEdit: false,
  supportsView: false,
};
