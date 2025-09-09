import { useMemo } from "react";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
} from "@/components/ui/sidebar";
import { useLayout } from "@/context/layout-provider";
import { AuthClient } from "@/lib/auth/auth-client";
// import { AppTitle } from './app-title'
import { sidebarData } from "./data/sidebar-data";
import { NavGroup } from "./nav-group";
import { NavUser } from "./nav-user";
import { TeamSwitcher } from "./team-switcher";

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

  // Memoize nav groups to prevent unnecessary re-renders
  const navGroups = useMemo(() => sidebarData.navGroups, []);
  
  // Memoize teams data to prevent unnecessary re-renders
  const teams = useMemo(() => sidebarData.teams, []);

  return (
    <Sidebar collapsible={collapsible} variant={variant}>
      <SidebarHeader>
        <TeamSwitcher teams={teams} />

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
