import type { ResourceConfig } from "./types";
import { userColumns } from "@/features/users/columns";
import * as usersApi from "@/lib/api/modules/users";
import type { User } from "@/types/api";

export const usersResource: ResourceConfig<User> = {
  key: "users",
  labelKey: "modules.users",
  labelSingularKey: "modules.user",
  basePath: "/users",
  permissions: { read: "users:read", write: "users:write" },
  list: usersApi.listUsers,
  create: usersApi.createUser,
  columns: userColumns,
  supportsCreate: true,
  supportsEdit: false,
  supportsView: false,
};
