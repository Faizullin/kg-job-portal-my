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
import type { ServiceSubcategory } from "@/lib/api/axios-client/api";
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
  Star,
  Trash2
} from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import { ServiceSubcategoryCreateEditDialog } from "./components/service-subcategory-create-edit-dialog";

export function ServiceSubcategoriesManagement() {
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

const loadServiceSubcategoriesQueryKey = 'service-subcategories'

const RenderTable = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const debouncedSearchQuery = useDebounce(searchQuery, 500);
  const [parsedData, setParsedData] = useState<Array<ServiceSubcategory>>([]);
  const [parsedPagination, setParsedPagination] = useState({
    pageCount: 1,
  });

  const subcategoryDialog = useDialogControl<{ id?: number }>();
  const queryClient = useQueryClient();

  const loadServiceSubcategoriesQuery = useQuery({
    queryKey: [loadServiceSubcategoriesQueryKey, debouncedSearchQuery],
    queryFn: () => myApi.v1CoreServiceSubcategoriesList({
      search: debouncedSearchQuery || undefined,
      page: 1,
      pageSize: 10,
    }).then(r => r.data),
    staleTime: 0,
  });

  useEffect(() => {
    if (!loadServiceSubcategoriesQuery.data) return;
    const parsed = loadServiceSubcategoriesQuery.data.results || [];
    setParsedData(parsed);
    setParsedPagination({
      pageCount: Math.ceil(
        (loadServiceSubcategoriesQuery.data?.count || 0) / 10,
      ),
    });
  }, [loadServiceSubcategoriesQuery.data]);

  const totalCount = parsedData.length;

  // Dialog handlers
  const handleCreateSubcategory = useCallback(() => {
    subcategoryDialog.show(undefined); // Explicitly pass undefined to ensure create mode
  }, [subcategoryDialog]);

  const handleEdit = useCallback((subcategory: ServiceSubcategory) => {
    subcategoryDialog.show({
      id: subcategory.id,
    });
  }, [subcategoryDialog]);

  const handleDelete = useCallback((subcategory: ServiceSubcategory) => {
    NiceModal.show(DeleteConfirmNiceDialog, {
      args: {
        title: "Delete Service Subcategory",
        desc: `Are you sure you want to delete "${subcategory.name}"? This action cannot be undone.`,
        confirmText: "Delete",
      }
    }).then((response) => {
      if (response.reason === "confirm") {
        deleteMutation.mutate(subcategory.id);
      }
    });
  }, []);

  const deleteMutation = useMutation({
    mutationFn: (id: number) => myApi.v1CoreServiceSubcategoriesDestroy({ id }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [loadServiceSubcategoriesQueryKey] });
      toast.success("Service subcategory deleted successfully!");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to delete service subcategory");
    },
  });

  const getStatusColor = useCallback((isActive: boolean) => {
    return isActive ? "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400" : "bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400";
  }, []);

  const getFeaturedColor = useCallback((featured: boolean) => {
    return featured ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400" : "bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400";
  }, []);

  const columns = useMemo<ColumnDef<ServiceSubcategory, any>[]>(() => [
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
      accessorKey: "category",
      header: "Category",
      cell: ({ row }) => {
        const category = row.getValue("category") as number;
        return (
          <Badge variant="outline">Category #{category}</Badge>
        );
      },
      meta: {
        variant: "text",
        label: "Category",
        className: ""
      }
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
      meta: {
        variant: "text",
        label: "Description",
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
      accessorKey: "featured",
      header: "Featured",
      cell: ({ row }) => {
        const featured = row.getValue("featured") as boolean;
        return (
          <Badge className={getFeaturedColor(featured)}>
            {featured ? (
              <>
                <Star className="h-3 w-3 mr-1" />
                Featured
              </>
            ) : (
              "Regular"
            )}
          </Badge>
        );
      },
      meta: {
        variant: "select",
        label: "Featured",
        options: [
          { label: "Featured", value: "true" },
          { label: "Regular", value: "false" },
        ],
        className: ""
      }
    },
    {
      accessorKey: "sort_order",
      header: "Sort Order",
      cell: ({ row }) => (
        <div className="text-sm text-muted-foreground">{row.getValue("sort_order")}</div>
      ),
      meta: {
        label: "Sort Order",
        variant: "number",
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
        const subcategory = row.original;
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
                <Button variant="ghost" size="sm" className="w-full justify-start" onClick={() => handleEdit(subcategory)}>
                  <Edit className="h-4 w-4 mr-2" />
                  Edit
                </Button>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Button variant="ghost" size="sm" className="w-full justify-start text-red-600" onClick={() => handleDelete(subcategory)}>
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete
                </Button>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        );
      },
    },
  ], [getStatusColor, getFeaturedColor, handleEdit, handleDelete]);

  const { table } = useDataTable({
    data: parsedData,
    columns,
    pageCount: parsedPagination.pageCount,
    enableGlobalFilter: true,
    initialState: {
      sorting: [{ id: "id", desc: true }],
    },
  });

  if (loadServiceSubcategoriesQuery.isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (loadServiceSubcategoriesQuery.error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600">Error loading service subcategories</p>
        <Button onClick={() => loadServiceSubcategoriesQuery.refetch()} className="mt-2">
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
            <h3 className="text-lg font-semibold">Service Subcategories</h3>
            <p className="text-sm text-muted-foreground">
              {totalCount} subcategor{totalCount !== 1 ? 'ies' : 'y'} found
            </p>
          </div>
          <Button onClick={handleCreateSubcategory} className="gap-2">
            <Plus className="h-4 w-4" />
            Add Subcategory
          </Button>
        </div>

        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-2">
            <div className="relative flex-1 max-w-sm">
              <SearchIcon className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search subcategories..."
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
      <ServiceSubcategoryCreateEditDialog
        control={subcategoryDialog}
      />
    </div>
  );
};