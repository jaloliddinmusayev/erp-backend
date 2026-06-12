"use client";

import dynamic from "next/dynamic";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useT } from "@/lib/i18n";
import {
  clientCreateSchema,
  type ClientFormValues,
} from "./schemas";

const LocationMapPicker = dynamic(
  () => import("./location-map-picker").then((m) => m.LocationMapPicker),
  { ssr: false, loading: () => <div className="h-64 animate-pulse rounded-xl bg-muted" /> },
);

interface ClientFormProps {
  defaultValues: ClientFormValues;
  onSubmit: (values: ClientFormValues) => void | Promise<void>;
  loading?: boolean;
  submitLabel?: string;
}

export function ClientForm({
  defaultValues,
  onSubmit,
  loading,
  submitLabel,
}: ClientFormProps) {
  const t = useT();
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<ClientFormValues>({
    resolver: zodResolver(clientCreateSchema),
    defaultValues,
  });

  const clientType = watch("client_type");
  const latitude = watch("latitude");
  const longitude = watch("longitude");
  const isLegal = clientType === "legal_entity";

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle className="text-lg">{t("clients.sectionMain")}</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-2">
          <div>
            <Label htmlFor="code">{t("fields.code")} *</Label>
            <Input id="code" className="mt-1.5" {...register("code")} disabled={loading} />
            {errors.code && <p className="mt-1 text-sm text-destructive">{t(errors.code.message ?? "")}</p>}
          </div>
          <div>
            <Label htmlFor="name">{t("fields.name")} *</Label>
            <Input id="name" className="mt-1.5" {...register("name")} disabled={loading} />
            {errors.name && <p className="mt-1 text-sm text-destructive">{t(errors.name.message ?? "")}</p>}
          </div>
          <div>
            <Label>{t("fields.clientType")} *</Label>
            <Select
              value={clientType}
              onValueChange={(v) => setValue("client_type", v as ClientFormValues["client_type"])}
              disabled={loading}
            >
              <SelectTrigger className="mt-1.5">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="legal_entity">{t("clientType.legal_entity")}</SelectItem>
                <SelectItem value="individual">{t("clientType.individual")}</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label>{t("fields.status")}</Label>
            <Select
              value={watch("is_active") ? "active" : "inactive"}
              onValueChange={(v) => setValue("is_active", v === "active")}
              disabled={loading}
            >
              <SelectTrigger className="mt-1.5">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="active">{t("status.active")}</SelectItem>
                <SelectItem value="inactive">{t("status.inactive")}</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle className="text-lg">{t("clients.sectionIdentity")}</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-2">
          <div>
            <Label htmlFor="inn">
              {isLegal ? t("fields.innStir") : t("fields.innPinfl")} *
            </Label>
            <Input
              id="inn"
              className="mt-1.5"
              inputMode="numeric"
              maxLength={isLegal ? 9 : 14}
              {...register("inn")}
              disabled={loading}
            />
            {errors.inn && <p className="mt-1 text-sm text-destructive">{t(errors.inn.message ?? "")}</p>}
          </div>
          {isLegal && (
            <div>
              <Label htmlFor="legal_name">{t("fields.legalName")}</Label>
              <Input id="legal_name" className="mt-1.5" {...register("legal_name")} disabled={loading} />
            </div>
          )}
        </CardContent>
      </Card>

      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle className="text-lg">{t("clients.sectionContact")}</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-2">
          <div>
            <Label htmlFor="contact_person">{t("fields.contactPerson")}</Label>
            <Input id="contact_person" className="mt-1.5" {...register("contact_person")} disabled={loading} />
          </div>
          <div>
            <Label htmlFor="phone">{t("fields.phone")}</Label>
            <Input id="phone" className="mt-1.5" placeholder="+998901234567" {...register("phone")} disabled={loading} />
            {errors.phone && <p className="mt-1 text-sm text-destructive">{t(errors.phone.message ?? "")}</p>}
          </div>
          <div className="sm:col-span-2">
            <Label htmlFor="email">{t("fields.email")}</Label>
            <Input id="email" type="email" className="mt-1.5" {...register("email")} disabled={loading} />
            {errors.email && <p className="mt-1 text-sm text-destructive">{t(errors.email.message ?? "")}</p>}
          </div>
        </CardContent>
      </Card>

      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle className="text-lg">{t("clients.sectionAddress")}</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-2">
          <div>
            <Label htmlFor="region">{t("fields.region")}</Label>
            <Input id="region" className="mt-1.5" {...register("region")} disabled={loading} />
          </div>
          <div>
            <Label htmlFor="city">{t("fields.city")}</Label>
            <Input id="city" className="mt-1.5" {...register("city")} disabled={loading} />
          </div>
          <div>
            <Label htmlFor="district">{t("fields.district")}</Label>
            <Input id="district" className="mt-1.5" {...register("district")} disabled={loading} />
          </div>
          <div className="sm:col-span-2">
            <Label htmlFor="address">{t("fields.address")}</Label>
            <Textarea id="address" className="mt-1.5" {...register("address")} disabled={loading} />
          </div>
        </CardContent>
      </Card>

      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle className="text-lg">{t("fields.location")}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">{t("clients.mapHint")}</p>
          <LocationMapPicker
            latitude={latitude}
            longitude={longitude}
            onChange={(lat, lng) => {
              setValue("latitude", lat, { shouldValidate: true });
              setValue("longitude", lng, { shouldValidate: true });
            }}
          />
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <Label htmlFor="latitude">{t("fields.latitude")}</Label>
              <Input
                id="latitude"
                type="number"
                step="any"
                className="mt-1.5"
                value={latitude ?? ""}
                onChange={(e) => {
                  const v = e.target.value;
                  setValue("latitude", v === "" ? undefined : Number(v), { shouldValidate: true });
                }}
                disabled={loading}
              />
              {errors.latitude && (
                <p className="mt-1 text-sm text-destructive">{t(errors.latitude.message ?? "")}</p>
              )}
            </div>
            <div>
              <Label htmlFor="longitude">{t("fields.longitude")}</Label>
              <Input
                id="longitude"
                type="number"
                step="any"
                className="mt-1.5"
                value={longitude ?? ""}
                onChange={(e) => {
                  const v = e.target.value;
                  setValue("longitude", v === "" ? undefined : Number(v), { shouldValidate: true });
                }}
                disabled={loading}
              />
              {errors.longitude && (
                <p className="mt-1 text-sm text-destructive">{t(errors.longitude.message ?? "")}</p>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle className="text-lg">{t("clients.sectionBank")}</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-2">
          <div className="sm:col-span-2">
            <Label htmlFor="bank_name">{t("fields.bankName")}</Label>
            <Input id="bank_name" className="mt-1.5" {...register("bank_name")} disabled={loading} />
          </div>
          <div>
            <Label htmlFor="bank_account">{t("fields.bankAccount")}</Label>
            <Input id="bank_account" className="mt-1.5" inputMode="numeric" {...register("bank_account")} disabled={loading} />
            {errors.bank_account && (
              <p className="mt-1 text-sm text-destructive">{t(errors.bank_account.message ?? "")}</p>
            )}
          </div>
          <div>
            <Label htmlFor="bank_mfo">{t("fields.bankMfo")}</Label>
            <Input id="bank_mfo" className="mt-1.5" inputMode="numeric" maxLength={5} {...register("bank_mfo")} disabled={loading} />
            {errors.bank_mfo && (
              <p className="mt-1 text-sm text-destructive">{t(errors.bank_mfo.message ?? "")}</p>
            )}
          </div>
        </CardContent>
      </Card>

      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle className="text-lg">{t("clients.sectionNotes")}</CardTitle>
        </CardHeader>
        <CardContent>
          <Textarea id="notes" {...register("notes")} disabled={loading} />
        </CardContent>
      </Card>

      <div className="sticky bottom-0 flex gap-3 rounded-2xl border bg-card/95 p-4 shadow-sm backdrop-blur supports-[backdrop-filter]:bg-card/80">
        <Button type="submit" disabled={loading}>
          {loading ? t("common.saving") : submitLabel ?? t("common.save")}
        </Button>
      </div>
    </form>
  );
}
