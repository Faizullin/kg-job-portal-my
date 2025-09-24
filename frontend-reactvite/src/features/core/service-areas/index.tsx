import { ConfigDrawer } from "@/components/config-drawer";
import { DataTable } from "@/components/data-table/data-table";
import { DataTableToolbar } from "@/components/data-table/data-table-toolbar";
import { useDataTable } from "@/components/data-table/use-data-table";
import { DeleteConfirmNiceDialog } from "@/components/dialogs/delete-confirm-dialog";
import { Header } from "@/components/layout/header";
import { Main } from "@/components/layout/main";
import NiceModal from "@/components/nice-modal/modal-context";
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
import type { ServiceArea } from "@/lib/api/axios-client/api";
import myApi from "@/lib/api/my-api";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type ColumnDef } from "@tanstack/react-table";
import {
  Calendar,
  Edit,
  Eye,
  MoreHorizontal,
  Plus,
  Search as SearchIcon,
  Trash2
} from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import { ServiceAreaCreateEditDialog, type ServiceAreaFormData } from "./components/service-area-create-edit-dialog";

export function ServiceAreasManagement() {
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

const loadServiceAreasQueryKey = 'service-areas'

const RenderTable = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const debouncedSearchQuery = useDebounce(searchQuery, 500);
  const [parsedData, setParsedData] = useState<Array<ServiceArea>>([]);
  const [parsedPagination, setParsedPagination] = useState({
    pageCount: 1,
  });

  const areaDialog = useDialogControl<ServiceAreaFormData>();
  const queryClient = useQueryClient();

  const loadServiceAreasQuery = useQuery({
    queryKey: [loadServiceAreasQueryKey, debouncedSearchQuery],
    queryFn: () => myApi.v1CoreServiceAreasList({
      search: debouncedSearchQuery || undefined,
      page: 1,
      pageSize: 10,
    }).then(r => r.data),
    staleTime: 0,
  });

  useEffect(() => {
    if (!loadServiceAreasQuery.data) return;
    const parsed = loadServiceAreasQuery.data.results || [];
    setParsedData(parsed);
    setParsedPagination({
      pageCount: Math.ceil(
        loadServiceAreasQuery.data.count / 10,
      ),
    });
  }, [loadServiceAreasQuery.data]);

  const totalCount = parsedData.length;

  // Dialog handlers
  const handleCreateArea = useCallback(() => {
    areaDialog.show(undefined); // Explicitly pass undefined to ensure create mode
  }, [areaDialog]);

  const handleEdit = useCallback((area: ServiceArea) => {
    areaDialog.show({
      id: area.id,
      name: area.name,
      city: area.city,
      state: area.state,
      country: area.country,
      is_active: area.is_active ?? true,
    });
  }, [areaDialog]);

  const handleDelete = useCallback((area: ServiceArea) => {
    NiceModal.show(DeleteConfirmNiceDialog, {
      title: "Delete Service Area",
      description: `Are you sure you want to delete "${area.name}"? This action cannot be undone.`,
      onConfirm: () => deleteMutation.mutate(area.id),
    });
  }, []);

  const deleteMutation = useMutation({
    mutationFn: (id: number) => myApi.v1CoreServiceAreasDestroy({ id }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [loadServiceAreasQueryKey] });
      toast.success("Service area deleted successfully!");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to delete service area");
    },
  });

  const getStatusColor = useCallback((isActive: boolean) => {
    return isActive ? "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400" : "bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400";
  }, []);

  const columns = useMemo<ColumnDef<ServiceArea, any>[]>(() => [
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
      meta: {
        variant: "number",
        label: "ID",
        className: ""
      }
    },
    {
      accessorKey: "name",
      header: "Name",
      cell: ({ row }) => (
        <div className="font-medium">{row.getValue("name")}</div>
      ),
      meta: {
        variant: "text",
        label: "Name",
        className: ""
      }
    },
    {
      accessorKey: "city",
      header: "City",
      cell: ({ row }) => (
        <div className="text-sm text-muted-foreground">{row.getValue("city")}</div>
      ),
      meta: {
        variant: "text",
        label: "City",
        className: ""
      }
    },
    {
      accessorKey: "state",
      header: "State",
      cell: ({ row }) => (
        <div className="text-sm text-muted-foreground">{row.getValue("state")}</div>
      ),
      meta: {
        variant: "text",
        label: "State",
        className: ""
      }
    },
    {
      accessorKey: "country",
      header: "Country",
      cell: ({ row }) => (
        <div className="text-sm text-muted-foreground">{row.getValue("country")}</div>
      ),
      meta: {
        variant: "text",
        label: "Country",
        className: ""
      }
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
      meta: {
        variant: "select",
        label: "Status",
        options: [
          { label: "Active", value: "true" },
          { label: "Inactive", value: "false" },
        ],
        className: ""
      }
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
      meta: {
        label: "Created",
        variant: "date",
      }
    },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => {
        const area = row.original;
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
                <Button variant="ghost" size="sm" className="w-full justify-start" onClick={() => handleEdit(area)}>
                  <Edit className="h-4 w-4 mr-2" />
                  Edit
                </Button>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Button variant="ghost" size="sm" className="w-full justify-start text-red-600" onClick={() => handleDelete(area)}>
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete
                </Button>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        );
      },
    },
  ], [getStatusColor, handleEdit, handleDelete]);

  const { table } = useDataTable({
    data: parsedData,
    columns,
    pageCount: parsedPagination.pageCount,
    enableGlobalFilter: true,
    initialState: {
      sorting: [{ id: "id", desc: true }],
    },
  });

  if (loadServiceAreasQuery.isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (loadServiceAreasQuery.error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600">Error loading service areas</p>
        <Button onClick={() => loadServiceAreasQuery.refetch()} className="mt-2">
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
            <h3 className="text-lg font-semibold">Service Areas</h3>
            <p className="text-sm text-muted-foreground">
              {totalCount} area{totalCount !== 1 ? 's' : ''} found
            </p>
          </div>
          <Button onClick={handleCreateArea} className="gap-2">
            <Plus className="h-4 w-4" />
            Add Area
          </Button>
        </div>

        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-2">
            <div className="relative flex-1 max-w-sm">
              <SearchIcon className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search areas..."
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
      <ServiceAreaCreateEditDialog
        control={areaDialog}
      />
    </div>
  );
};