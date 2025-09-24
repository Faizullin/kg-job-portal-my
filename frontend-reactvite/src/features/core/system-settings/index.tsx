import { ConfigDrawer } from "@/components/config-drawer";
import { DataTable } from "@/components/data-table/data-table";
import { DataTableToolbar } from "@/components/data-table/data-table-toolbar";
import { useDataTable } from "@/components/data-table/use-data-table";
import { Header } from "@/components/layout/header";
import { Main } from "@/components/layout/main";
import { ProfileDropdown } from "@/components/profile-dropdown";
import { Search } from "@/components/search";
import { ThemeSwitch } from "@/components/theme-switch";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { useDebounce } from "@/hooks/use-debounce";
import { useDialogControl } from "@/hooks/use-dialog-control";
import type { SystemSettings } from "@/lib/api/axios-client/api";
import myApi from "@/lib/api/my-api";
import { useQuery } from "@tanstack/react-query";
import { type ColumnDef } from "@tanstack/react-table";
import {
  Calendar,
  Edit,
  Eye,
  MoreHorizontal,
  Search as SearchIcon,
} from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { SystemSettingsEditDialog, type SystemSettingsFormData } from "./components/system-settings-edit-dialog";

export function SystemSettingsManagement() {
  return (
    <>
      <Header fixed>
        <Search />
        <div className="ms-auto flex items-center space-x-4">
          <ThemeSwitch />
          <ConfigDrawer />
          <ProfileDropdown />
        </div>
      </Header>
      <Main>
        <RenderTable />
      </Main>
    </>
  );
}

const loadSystemSettingsQueryKey = 'system-settings'

const RenderTable = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const debouncedSearchQuery = useDebounce(searchQuery, 500);
  const [parsedData, setParsedData] = useState<Array<SystemSettings>>([]);
  const [parsedPagination, setParsedPagination] = useState({
    pageCount: 1,
  });

  const settingsDialog = useDialogControl<SystemSettingsFormData>();

  const loadSystemSettingsQuery = useQuery({
    queryKey: [loadSystemSettingsQueryKey, debouncedSearchQuery],
    queryFn: () => myApi.v1CoreSystemSettingsList({
      search: debouncedSearchQuery || undefined,
      page: 1,
      pageSize: 10,
    }).then(r => r.data),
    staleTime: 0,
  });

  useEffect(() => {
    if (!loadSystemSettingsQuery.data) return;
    const parsed = loadSystemSettingsQuery.data.results || [];
    setParsedData(parsed);
    setParsedPagination({
      pageCount: Math.ceil(
        loadSystemSettingsQuery.data.count / 10,
      ),
    });
  }, [loadSystemSettingsQuery.data]);

  const totalCount = parsedData.length;

  // Dialog handlers
  const handleEdit = useCallback((setting: SystemSettings) => {
    settingsDialog.show({
      id: setting.id,
      key: setting.key,
      value: setting.value,
      description: setting.description || "",
      setting_type: setting.setting_type,
      is_active: setting.is_active ?? true,
    });
  }, [settingsDialog]);

  const getStatusColor = useCallback((isActive: boolean) => {
    return isActive ? "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400" : "bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400";
  }, []);

  const getTypeColor = useCallback((type: string) => {
    const colors: Record<string, string> = {
      string: "bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400",
      integer: "bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-400",
      float: "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400",
      boolean: "bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-400",
      json: "bg-indigo-100 text-indigo-800 dark:bg-indigo-900/20 dark:text-indigo-400",
    };
    return colors[type] || "bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400";
  }, []);

  const columns = useMemo<ColumnDef<SystemSettings, any>[]>(() => [
    {
      accessorKey: "id",
      header: "ID",
      cell: ({ row }) => (
        <a className="font-mono text-sm" href="#" onClick={(e) => {
          e.preventDefault();
          handleEdit(row.original);
        }}>
          #{row.getValue("id")}
        </a>
      ),
    },
    {
      accessorKey: "key",
      header: "Key",
      cell: ({ row }) => (
        <div className="font-medium">{row.getValue("key")}</div>
      ),
    },
    {
      accessorKey: "value",
      header: "Value",
      cell: ({ row }) => {
        const value = row.getValue("value") as string;
        return (
          <div className="max-w-xs truncate text-sm text-muted-foreground">
            {value}
          </div>
        );
      },
    },
    {
      accessorKey: "description",
      header: "Description",
      cell: ({ row }) => {
        const description = row.getValue("description") as string;
        return (
          <div className="max-w-xs truncate text-sm text-muted-foreground">
            {description || "No description"}
          </div>
        );
      },
    },
    {
      accessorKey: "setting_type",
      header: "Type",
      cell: ({ row }) => {
        const type = row.getValue("setting_type") as string;
        return (
          <Badge className={getTypeColor(type)}>
            {type}
          </Badge>
        );
      },
    },
    {
      accessorKey: "is_active",
      header: "Status",
      cell: ({ row }) => {
        const isActive = row.getValue("is_active") as boolean;
        return (
          <Badge className={getStatusColor(isActive)}>
            {isActive ? "Active" : "Inactive"}
          </Badge>
        );
      },
    },
    {
      accessorKey: "created_at",
      header: "Created",
      cell: ({ row }) => (
        <div className="flex items-center gap-1 text-sm text-muted-foreground">
          <Calendar className="h-3 w-3" />
          <span>{new Date(row.getValue("created_at")).toLocaleDateString()}</span>
        </div>
      ),
    },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => {
        const setting = row.original;
        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon">
                <MoreHorizontal className="h-4 w-4" />
                <span className="sr-only">Open menu</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem asChild>
                <Button variant="ghost" size="sm" className="w-full justify-start">
                  <Eye className="h-4 w-4 mr-2" />
                  View Details
                </Button>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Button variant="ghost" size="sm" className="w-full justify-start" onClick={() => handleEdit(setting)}>
                  <Edit className="h-4 w-4 mr-2" />
                  Edit
                </Button>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        );
      },
    },
  ], [getStatusColor, getTypeColor, handleEdit]);

  const { table } = useDataTable({
    data: parsedData,
    columns,
    pageCount: parsedPagination.pageCount,
    enableGlobalFilter: true,
    initialState: {
      sorting: [{ id: "id", desc: true }],
    },
  });

  if (loadSystemSettingsQuery.isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (loadSystemSettingsQuery.error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600">Error loading system settings</p>
        <Button onClick={() => loadSystemSettingsQuery.refetch()} className="mt-2">
          Try Again
        </Button>
      </div>
    );
  }

  return (
    <div className="-mx-4 flex-1 overflow-auto px-4 py-1 lg:flex-row lg:space-y-0 lg:space-x-12">
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-lg font-semibold">System Settings</h3>
            <p className="text-sm text-muted-foreground">
              {totalCount} setting{totalCount !== 1 ? 's' : ''} found
            </p>
          </div>
        </div>

        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-2">
            <div className="relative flex-1 max-w-sm">
              <SearchIcon className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search settings..."
                value={searchQuery}
                onChange={(event) => setSearchQuery(event.target.value)}
                className="pl-8 h-8"
              />
            </div>
          </div>
        </div>
        <DataTable table={table}>
          <DataTableToolbar table={table} />
        </DataTable>
      </div>

      {/* Dialog */}
      <SystemSettingsEditDialog
        control={settingsDialog}
      />
    </div>
  );
};