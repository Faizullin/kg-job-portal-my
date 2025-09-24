import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
} from "@/components/ui/sidebar";
import { useLayout } from "@/context/layout-provider";
import { AuthClient } from "@/lib/auth/auth-client";
import { useMemo } from "react";
// import { AppTitle } from './app-title'
import { sidebarData } from "./data/sidebar-data";
import { NavGroup } from "./nav-group";
import { NavUser } from "./nav-user";
import { type SidebarData } from "./types";

export function AppSidebar() {
  const { collapsible, variant } = useLayout();

  // Memoize user data to prevent unnecessary re-computations
  const user = useMemo(() => {
    const backendUser = AuthClient.getCurrentUser();
    const firebaseUser = AuthClient.getCurrentFirebaseUser();

    return backendUser
      ? {
        name: backendUser.username || backendUser.email.split("@")[0] || "User",
        email: backendUser.email,
        avatar: firebaseUser?.photoURL || "/avatars/default.jpg",
      }
      : sidebarData.user;
  }, []); // Empty dependency array since AuthClient methods are stable

  // Role-aware filtering of nav groups
  const navGroups = useMemo(() => {
    const currentUser = AuthClient.getCurrentUser();
    const role = currentUser?.user_role || "client";
    const isProvider = /provider/i.test(role);
    const isAdmin = currentUser?.is_staff || currentUser?.is_superuser || false;

    const isAllowedUrl = (url: string) => {
      if (!url) return true;
      
      // Core URLs - only show for admin users
      if (url.startsWith("/core")) {
        return isAdmin;
      }
      
      if (isProvider) {
        // Providers: allow search and bids; hide orders and tasks by default
        if (url === "/orders" || url === "/tasks") return false;
        return true;
      }
      // Clients: allow orders; hide provider-only pages
      if (url === "/search" || url === "/bids") return false;
      return true;
    };

    const filterItems = (items: NonNullable<SidebarData["navGroups"]>[number]["items"]): typeof items => {
      return items
        .map((item) => {
          if (item.items && item.items.length) {
            const filteredChildren = filterItems(item.items);
            return filteredChildren.length ? { ...item, items: filteredChildren } : null;
          }
          if (item.url && !isAllowedUrl(item.url)) return null;
          return item;
        })
        .filter(Boolean) as any;
    };

    return sidebarData.navGroups
      .map((group) => {
        const items = filterItems(group.items);
        return items.length ? { ...group, items } : null;
      })
      .filter(Boolean) as typeof sidebarData.navGroups;
  }, []);

  // // Memoize teams data to prevent unnecessary re-renders
  // const teams = useMemo(() => sidebarData.teams, []);

  return (
    <Sidebar collapsible={collapsible} variant={variant}>
      <SidebarHeader>
        {/* <TeamSwitcher teams={teams} /> */}

        {/* Replace <TeamSwitch /> with the following <AppTitle />
         /* if you want to use the normal app title instead of TeamSwitch dropdown */}
        {/* <AppTitle /> */}
      </SidebarHeader>
      <SidebarContent>
        {navGroups.map((props) => (
          <NavGroup key={props.title} {...props} />
        ))}
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={user} />
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  );
}
