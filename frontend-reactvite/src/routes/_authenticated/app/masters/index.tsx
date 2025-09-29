import { ConfigDrawer } from "@/components/config-drawer";
import { Header } from "@/components/layout/header";
import { Main } from "@/components/layout/main";
import { ProfileDropdown } from "@/components/profile-dropdown";
import { ThemeSwitch } from "@/components/theme-switch";
import { Button } from "@/components/ui/button";
import { MastersList } from "@/features/app/masters/masters-list";
import { createFileRoute } from "@tanstack/react-router";
import { Menu } from "lucide-react";

export const Route = createFileRoute("/_authenticated/app/masters/")({
  component: MastersPage,
});

function MastersPage() {
  return (
    <>
      <Header>
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="sm">
            <Menu className="h-5 w-5" />
          </Button>
          <h1 className="text-lg font-semibold">Выберите мастера</h1>
        </div>
        <div className="ms-auto flex items-center space-x-4">
          <ThemeSwitch />
          <ConfigDrawer />
          <ProfileDropdown />
        </div>
      </Header>

      <Main>
        <MastersList />
      </Main>
    </>
  );
}