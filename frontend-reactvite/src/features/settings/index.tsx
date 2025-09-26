import { ConfigDrawer } from "@/components/config-drawer";
import { Header } from "@/components/layout/header";
import { Main } from "@/components/layout/main";
import { ProfileDropdown } from "@/components/profile-dropdown";
import { Search } from "@/components/search";
import { ThemeSwitch } from "@/components/theme-switch";
import { Separator } from "@/components/ui/separator";
import { useAuthStore } from "@/stores/auth-store";
import { Outlet } from "@tanstack/react-router";
import { Bell, Briefcase, Monitor, Palette, Shield, ShoppingCart, User, UserCog, Users } from "lucide-react";
import { useMemo } from "react";
import { SidebarNav } from "./_components/sidebar-nav";

// Base sidebar navigation items
const getBaseSidebarItems = () => [
  {
    title: "Profile",
    href: "/settings/profile",
    icon: <UserCog size={18} />,
    visible: true,
  },
  {
    title: "User Profile",
    href: "/settings/user-profile",
    icon: <User size={18} />,
    visible: true,
  },
  {
    title: "Appearance",
    href: "/settings/appearance",
    icon: <Palette size={18} />,
    visible: true,
  },
  {
    title: "Notifications",
    href: "/settings/notifications",
    icon: <Bell size={18} />,
    visible: true,
  },
  {
    title: "Display",
    href: "/settings/display",
    icon: <Monitor size={18} />,
    visible: true,
  },
];

// Role-based sidebar navigation items
const getRoleBasedSidebarItems = (user: any) => {
  const items = [];

  // Always show both tabs; pages handle initialization if profile missing
  items.push({
    title: "Service Provider",
    href: "/settings/service-provider",
    icon: <Briefcase size={18} />,
    visible: true,
  });
  items.push({
    title: "Client Profile",
    href: "/settings/client-profile",
    icon: <ShoppingCart size={18} />,
    visible: true,
  });

  // Admin/Staff sections - only for staff or superusers
  if (user?.is_staff || user?.is_superuser) {
    items.push({
      title: "User Management",
      href: "/settings/user-management",
      icon: <Users size={18} />,
      visible: true,
    });
  }

  // Superuser sections - only for superusers
  if (user?.is_superuser) {
    items.push({
      title: "System Settings",
      href: "/settings/system",
      icon: <Shield size={18} />,
      visible: true,
    });
  }

  return items;
};

export function Settings() {
  const auth = useAuthStore();

  // Memoize sidebar items based on user roles and permissions
  const sidebarNavItems = useMemo(() => {
    const baseItems = getBaseSidebarItems();
    const roleBasedItems = getRoleBasedSidebarItems(auth.user);

    return [
      ...baseItems,
      ...roleBasedItems.filter(item => item.visible)
    ];
  }, [auth.user]);
  return (
    <>
      {/* ===== Top Heading ===== */}
      <Header>
        <Search />
        <div className="ms-auto flex items-center space-x-4">
          <ThemeSwitch />
          <ConfigDrawer />
          <ProfileDropdown />
        </div>
      </Header>

      <Main fixed>
        <div className="space-y-0.5">
          <h1 className="text-2xl font-bold tracking-tight md:text-3xl">
            Settings
          </h1>
          <p className="text-muted-foreground">
            Manage your account settings and set e-mail preferences.
          </p>
        </div>
        <Separator className="my-4 lg:my-6" />
        <div className="flex flex-1 flex-col space-y-2 overflow-hidden md:space-y-2 lg:flex-row lg:space-y-0 lg:space-x-12">
          <aside className="top-0 lg:sticky lg:w-1/5">
            <SidebarNav items={sidebarNavItems} />
          </aside>
          <div className="flex w-full overflow-y-hidden p-1">
            <Outlet />
          </div>
        </div>
      </Main>
    </>
  );
}
