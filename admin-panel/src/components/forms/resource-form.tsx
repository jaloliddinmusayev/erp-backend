"use client";

import {
  useForm,
  type DefaultValues,
  type FieldValues,
  type Path,
  type Resolver,
} from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import type { ZodType } from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export type FieldType = "text" | "email" | "number" | "date" | "textarea" | "select";

export interface FormFieldConfig<T extends FieldValues> {
  name: Path<T>;
  label: string;
  type?: FieldType;
  placeholder?: string;
  required?: boolean;
  options?: { label: string; value: string }[];
  disabled?: boolean;
}

interface ResourceFormProps<T extends FieldValues> {
  schema: ZodType<T>;
  fields: FormFieldConfig<T>[];
  defaultValues?: DefaultValues<T>;
  onSubmit: (data: T) => void | Promise<void>;
  loading?: boolean;
  submitLabel?: string;
  cancelHref?: string;
}

export function ResourceForm<T extends FieldValues>({
  schema,
  fields,
  defaultValues,
  onSubmit,
  loading,
  submitLabel = "Saqlash",
}: ResourceFormProps<T>) {
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<T>({
    resolver: zodResolver(schema) as Resolver<T>,
    defaultValues,
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2">
        {fields.map((field) => {
          const error = errors[field.name]?.message as string | undefined;
          const value = watch(field.name);

          return (
            <div
              key={String(field.name)}
              className={field.type === "textarea" ? "sm:col-span-2" : ""}
            >
              <Label htmlFor={String(field.name)}>
                {field.label}
                {field.required && <span className="text-destructive"> *</span>}
              </Label>

              {field.type === "textarea" ? (
                <Textarea
                  id={String(field.name)}
                  placeholder={field.placeholder}
                  disabled={field.disabled || loading}
                  className="mt-1.5"
                  {...register(field.name)}
                />
              ) : field.type === "select" && field.options ? (
                <Select
                  value={value != null ? String(value) : undefined}
                  onValueChange={(v) =>
                    setValue(field.name, (field.type === "select" && !Number.isNaN(Number(v)) && field.name.toString().includes("_id")
                      ? Number(v)
                      : v) as T[Path<T>])
                  }
                  disabled={field.disabled || loading}
                >
                  <SelectTrigger className="mt-1.5" id={String(field.name)}>
                    <SelectValue placeholder={field.placeholder ?? "Tanlang"} />
                  </SelectTrigger>
                  <SelectContent>
                    {field.options.map((opt) => (
                      <SelectItem key={opt.value} value={opt.value}>
                        {opt.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              ) : (
                <Input
                  id={String(field.name)}
                  type={field.type ?? "text"}
                  placeholder={field.placeholder}
                  disabled={field.disabled || loading}
                  className="mt-1.5"
                  {...register(field.name, {
                    valueAsNumber: field.type === "number",
                  })}
                />
              )}

              {error && (
                <p className="mt-1 text-sm text-destructive">{error}</p>
              )}
            </div>
          );
        })}
      </div>

      <div className="flex gap-3">
        <Button type="submit" disabled={loading}>
          {loading ? "Saqlanmoqda..." : submitLabel}
        </Button>
      </div>
    </form>
  );
}
