import type { ResourceConfig } from "./types";
import { productColumns } from "@/features/products/columns";
import {
  productCreateSchema,
  productUpdateSchema,
} from "@/features/products/schemas";
import * as productsApi from "@/lib/api/modules/products";
import type { Product } from "@/types/api";

export const productsResource: ResourceConfig<Product> = {
  key: "products",
  labelKey: "modules.products",
  labelSingularKey: "modules.product",
  basePath: "/products",
  permissions: { read: "products:read", write: "products:write" },
  list: productsApi.listProducts,
  get: productsApi.getProduct,
  create: productsApi.createProduct,
  update: productsApi.updateProduct,
  columns: productColumns,
  createSchema: productCreateSchema,
  updateSchema: productUpdateSchema,
  supportsCreate: true,
  supportsEdit: true,
  supportsView: true,
};
