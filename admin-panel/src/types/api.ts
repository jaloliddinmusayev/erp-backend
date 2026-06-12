export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface MeRole {
  id: number;
  code: string;
  name: string;
}

export interface MeResponse {
  user_id: number;
  full_name: string;
  email: string;
  company_id: number;
  role: MeRole;
}

export interface RefClient {
  id: number;
  code: string;
  name: string;
}

export interface RefBranch {
  id: number;
  code: string;
  name: string;
}

export interface RefProduct {
  id: number;
  code: string;
  name: string;
}

export interface RefCategory {
  id: number;
  name: string;
  code: string;
}

export interface RefUnit {
  id: number;
  name: string;
  code: string;
}

export interface RefSalesOrder {
  id: number;
  order_number: string;
  status: string;
}

export interface RefUser {
  id: number;
  full_name: string;
  email: string;
}

export interface Category {
  id: number;
  company_id: number;
  name: string;
  code: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Unit {
  id: number;
  company_id: number;
  name: string;
  code: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Product {
  id: number;
  company_id: number;
  category_id: number;
  base_unit_id: number;
  name: string;
  code: string;
  barcode: string | null;
  description: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  category: RefCategory;
  base_unit: RefUnit;
}

export type ClientType = "legal_entity" | "individual";

export interface Client {
  id: number;
  company_id: number;
  code: string;
  name: string;
  client_type: ClientType;
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
  created_at: string;
  updated_at: string;
}

export interface Warehouse {
  id: number;
  company_id: number;
  branch_id: number;
  name: string;
  code: string;
  address: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Branch {
  id: number;
  company_id: number;
  name: string;
  code: string;
  address: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface SalesOrderItem {
  id: number;
  company_id: number;
  sales_order_id: number;
  product_id: number;
  ordered_qty: string;
  fulfilled_qty: string;
  remaining_qty: string;
  unit_price: string;
  line_total: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
  product: RefProduct;
}

export interface SalesOrder {
  id: number;
  company_id: number;
  client_id: number;
  branch_id: number | null;
  order_number: string;
  order_date: string;
  status: string;
  fulfillment_status: string;
  fulfilled_at: string | null;
  is_sent_to_wms: boolean;
  wms_order_id: string | null;
  integration_status: string;
  sent_to_wms_at: string | null;
  last_sync_error: string | null;
  notes: string | null;
  total_amount: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  client: RefClient;
  branch: RefBranch | null;
  items?: SalesOrderItem[];
}

export interface Payment {
  id: number;
  company_id: number;
  client_id: number;
  sales_order_id: number | null;
  amount: string;
  payment_date: string;
  payment_method: string;
  reference_number: string | null;
  notes: string | null;
  is_active: boolean;
  created_by_user_id: number | null;
  created_at: string;
  updated_at: string;
  client: RefClient;
  sales_order: RefSalesOrder | null;
  created_by_user: RefUser | null;
}

export interface InvoiceItem {
  id: number;
  company_id: number;
  invoice_id: number;
  product_id: number | null;
  product_code: string;
  product_name: string;
  quantity: string;
  unit_price: string;
  line_total: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface Invoice {
  id: number;
  company_id: number;
  client_id: number;
  sales_order_id: number | null;
  invoice_number: string;
  invoice_date: string;
  due_date: string | null;
  status: string;
  notes: string | null;
  total_amount: string;
  paid_amount: string;
  outstanding_amount: string;
  is_active: boolean;
  created_by_user_id: number | null;
  created_at: string;
  updated_at: string;
  client: RefClient;
  sales_order: RefSalesOrder | null;
  items?: InvoiceItem[];
  created_by_user?: RefUser | null;
}

export interface User {
  id: number;
  company_id: number;
  role_id: number;
  full_name: string;
  email: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Role {
  id: number;
  company_id: number | null;
  name: string;
  code: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AgingBucketSummary {
  total_outstanding: string | number;
  current: string | number;
  days_1_30: string | number;
  days_31_60: string | number;
  days_61_90: string | number;
  days_90_plus: string | number;
}

/** Matches backend `GlobalAgingResponse`. */
export interface AgingResponse {
  as_of_date: string;
  summary: AgingBucketSummary;
}

export interface AgingInvoiceDetail {
  invoice_id: number;
  invoice_number: string;
  invoice_date: string;
  due_date: string | null;
  total_amount: string;
  paid_amount: string;
  outstanding_amount: string;
  overdue_days: number;
  aging_bucket: string;
  is_overdue: boolean;
}

export interface DashboardStats {
  totalProducts: number;
  totalClients: number;
  totalSalesOrders: number;
  openOrders: number;
  invoicesOutstanding: number;
  paymentsReceived: number;
}
