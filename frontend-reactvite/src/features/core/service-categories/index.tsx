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
import type { ServiceCategory } from "@/lib/api/axios-client/api";
import myApi from "@/lib/api/my-api";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type ColumnDef } from "@tanstack/react-table";
import {
  Calendar,
  Edit,
  Eye,
  EyeOff,
  MoreHorizontal,
  Plus,
  Search as SearchIcon,
  Star,
  Trash2
} from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import { ServiceCategoryCreateEditDialog, type ServiceCategoryFormData } from "./components/service-category-create-edit-dialog";


export function ServiceCategoriesManagement() {
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

const loadServiceCategoriesQueryKey = 'service-categories'

const RenderTable = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const debouncedSearchQuery = useDebounce(searchQuery, 500);
  const [parsedData, setParsedData] = useState<Array<ServiceCategory>>([]);
  const [parsedPagination, setParsedPagination] = useState({
    pageCount: 1,
  });

  const categoryDialog = useDialogControl<ServiceCategoryFormData>();
  const queryClient = useQueryClient();

  const loadServiceCategoriesQuery = useQuery({
    queryKey: [loadServiceCategoriesQueryKey, debouncedSearchQuery],
    queryFn: () => myApi.v1CoreServiceCategoriesList({
      search: debouncedSearchQuery || undefined,
      page: 1,
      pageSize: 10,
    }).then(r => r.data),
    staleTime: 0,
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => myApi.v1CoreServiceCategoriesDestroy({
      id,
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [loadServiceCategoriesQueryKey] });
      toast.success("Service category deleted successfully!");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to delete service category");
    },
  });

  useEffect(() => {
    if (!loadServiceCategoriesQuery.data) return;
    const parsed = loadServiceCategoriesQuery.data.results || [];
    setParsedData(parsed);
    setParsedPagination({
      pageCount: Math.ceil(
        (loadServiceCategoriesQuery.data.count || 0) / 10,
      ),
    });
  }, [loadServiceCategoriesQuery.data]);

  const totalCount = parsedData.length;

  // Dialog handlers
  const handleCreateCategory = useCallback(() => {
    categoryDialog.show(undefined); // Explicitly pass undefined to ensure create mode
  }, [categoryDialog]);

  const handleEdit = useCallback((category: ServiceCategory) => {
    categoryDialog.show({
      id: category.id,
      name: category.name,
      description: category.description || "",
      is_active: category.is_active ?? true,
      featured: category.featured ?? false,
    });
  }, [categoryDialog]);

  const handleDelete = useCallback((category: ServiceCategory) => {
    NiceModal.show(DeleteConfirmNiceDialog, {
      args: {
        title: "Delete Category",
        desc: "Are you sure you want to delete this category?",
        confirmText: "Delete",
      },
    }).then((response) => {
      if (response?.reason === "confirm") {
        deleteMutation.mutate(category.id);
      }
    });
  }, [deleteMutation]);

  const getStatusColor = useCallback((isActive: boolean) => {
    return isActive ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800';
  }, []);

  const getFeaturedColor = useCallback((featured: boolean) => {
    return featured ? 'bg-yellow-100 text-yellow-800' : 'bg-blue-100 text-blue-800';
  }, []);

  const columns = useMemo<ColumnDef<ServiceCategory, any>[]>(() => [
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
        <div className="max-w-[200px]">
          <div className="font-medium truncate">{row.getValue("name")}</div>
          <div className="text-sm text-muted-foreground truncate">
            {row.original.description || "No description"}
          </div>
        </div>
      ),
      meta: {
        variant: "text",
        placeholder: "Search categories...",
        label: "Search",
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
            {isActive ? (
              <>
                <Eye className="h-3 w-3 mr-1" />
                Active
              </>
            ) : (
              <>
                <EyeOff className="h-3 w-3 mr-1" />
                Inactive
              </>
            )}
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
      accessorKey: "created_at",
      header: "Created",
      cell: ({ row }) => (
        <div className="flex items-center gap-1 text-sm text-muted-foreground">
          <Calendar className="h-3 w-3" />
          <span>{new Date(row.getValue("created_at")).toLocaleDateString()}</span>
        </div>
      ),
      meta: {
        variant: "date",
        label: "Created Date",
        className: ""
      }
    },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="h-8 w-8 p-0">
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem
              className="flex items-center gap-2"
              onClick={() => handleEdit(row.original)}
            >
              <Edit className="h-4 w-4" />
              Edit
            </DropdownMenuItem>
            <DropdownMenuItem className="flex items-center gap-2 text-destructive"
              onClick={() => handleDelete(row.original)}
            >
              <Trash2 className="h-4 w-4" />
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      ),
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

  return (
    <div className="-mx-4 flex-1 overflow-auto px-4 py-1 lg:flex-row lg:space-y-0 lg:space-x-12">
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-lg font-semibold">Service Categories</h3>
            <p className="text-sm text-muted-foreground">
              {totalCount} categor{totalCount !== 1 ? 'ies' : 'y'} found
            </p>
          </div>
          <Button onClick={handleCreateCategory} className="gap-2">
            <Plus className="h-4 w-4" />
            Add Category
          </Button>
        </div>

        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-2">
            <div className="relative flex-1 max-w-sm">
              <SearchIcon className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search categories..."
                value={searchQuery}
                onChange={(event) => setSearchQuery(event.target.value)}
                className="pl-8 h-8"
              />
            </div>
          </div>
          <DataTable table={table}>
            <DataTableToolbar table={table} />
          </DataTable>
        </div>
      </div>

      {/* Dialog */}
      <ServiceCategoryCreateEditDialog
        control={categoryDialog}
      />
    </div>
  );
};