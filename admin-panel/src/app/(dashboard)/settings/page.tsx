"use client";

import { useTheme } from "next-themes";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useAuthStore } from "@/stores/auth-store";

export default function SettingsPage() {
  const { theme, setTheme } = useTheme();
  const user = useAuthStore((s) => s.user);

  return (
    <div className="space-y-6">
      <PageHeader title="Settings" description="Profil va ko'rinish sozlamalari" />

      <Card>
        <CardHeader><CardTitle>Profil</CardTitle></CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-2">
          <div><Label className="text-muted-foreground">Ism</Label><p className="mt-1 font-medium">{user?.full_name}</p></div>
          <div><Label className="text-muted-foreground">Email</Label><p className="mt-1 font-medium">{user?.email}</p></div>
          <div><Label className="text-muted-foreground">Rol</Label><p className="mt-1 font-medium">{user?.role.name}</p></div>
          <div><Label className="text-muted-foreground">Tenant ID</Label><p className="mt-1 font-medium">{user?.company_id}</p></div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Ko&apos;rinish</CardTitle></CardHeader>
        <CardContent>
          <Label>Mavzu</Label>
          <Select value={theme} onValueChange={setTheme}>
            <SelectTrigger className="mt-1.5 w-48"><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="light">Light</SelectItem>
              <SelectItem value="dark">Dark</SelectItem>
              <SelectItem value="system">System</SelectItem>
            </SelectContent>
          </Select>
        </CardContent>
      </Card>
    </div>
  );
}
