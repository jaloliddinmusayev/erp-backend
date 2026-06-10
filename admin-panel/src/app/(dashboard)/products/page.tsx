"use client";

import { ResourceListPage } from "@/components/crud/resource-list-page";
import { productsResource } from "@/config/resources/products";

export default function ProductsPage() {
  return <ResourceListPage config={productsResource} />;
}
