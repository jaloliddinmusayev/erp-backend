"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ComponentType } from "react";
import { Sparkles } from "lucide-react";
import { filterNavigation, groupNavigationItems } from "@/config/navigation";
import { NAV_GROUP_LABELS, NAV_GROUP_ORDER } from "@/config/design";
import { hasPermission } from "@/config/permissions";
import { useAuthStore } from "@/stores/auth-store";
import { useUiStore } from "@/stores/ui-store";
import { cn } from "@/lib/utils";
import { useT } from "@/lib/i18n";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface SidebarProps {
  onNavigate?: () => void;
}

function NavLink({
  href,
  icon: Icon,
  label,
  isActive,
  collapsed,
  onNavigate,
}: {
  href: string;
  icon: ComponentType<{ className?: string }>;
  label: string;
  isActive: boolean;
  collapsed: boolean;
  onNavigate?: () => void;
}) {
  const link = (
    <Link
      href={href}
      onClick={onNavigate}
      className={cn(
        "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all",
        isActive
          ? "border-l-2 border-primary bg-primary/10 text-primary"
          : "border-l-2 border-transparent text-muted-foreground hover:bg-sidebar-accent hover:text-sidebar-foreground",
        collapsed && "justify-center border-l-0 px-2",
      )}
    >
      <Icon className="h-5 w-5 shrink-0" />
      {!collapsed && <span>{label}</span>}
    </Link>
  );

  if (collapsed) {
    return (
      <Tooltip delayDuration={0}>
        <TooltipTrigger asChild>{link}</TooltipTrigger>
        <TooltipContent side="right">{label}</TooltipContent>
      </Tooltip>
    );
  }

  return link;
}

export function Sidebar({ onNavigate }: SidebarProps) {
  const pathname = usePathname();
  const t = useT();
  const roleCode = useAuthStore((s) => s.user?.role.code ?? "viewer");
  const collapsed = useUiStore((s) => s.sidebarCollapsed);
  const items = filterNavigation(roleCode, hasPermission);
  const grouped = groupNavigationItems(items);

  return (
    <TooltipProvider>
      <aside
        className={cn(
          "flex h-full flex-col border-r border-sidebar-border bg-sidebar transition-all duration-300",
          collapsed ? "w-[72px]" : "w-64",
        )}
      >
        <div className="flex h-16 items-center gap-3 border-b border-sidebar-border px-4">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 text-white shadow-md shadow-indigo-500/25">
            <Sparkles className="h-5 w-5" />
          </div>
          {!collapsed && (
            <div className="min-w-0">
              <p className="truncate text-sm font-bold tracking-tight">Triad ERP</p>
              <p className="truncate text-xs text-muted-foreground">{t("common.adminPanel")}</p>
            </div>
          )}
        </div>

        <nav className="flex-1 space-y-4 overflow-y-auto p-3">
          {NAV_GROUP_ORDER.map((groupKey) => {
            const groupItems = grouped.get(groupKey);
            if (!groupItems?.length) return null;

            return (
              <div key={groupKey}>
                {!collapsed && (
                  <p className="mb-2 px-3 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                    {t(NAV_GROUP_LABELS[groupKey])}
                  </p>
                )}
                <div className="space-y-0.5">
                  {groupItems.map((item) => {
                    const isActive =
                      item.href === "/"
                        ? pathname === "/"
                        : pathname.startsWith(item.href);
                    return (
                      <NavLink
                        key={item.href}
                        href={item.href}
                        icon={item.icon}
                        label={t(item.titleKey)}
                        isActive={isActive}
                        collapsed={collapsed}
                        onNavigate={onNavigate}
                      />
                    );
                  })}
                </div>
              </div>
            );
          })}
        </nav>
      </aside>
    </TooltipProvider>
  );
}
