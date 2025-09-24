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
import type { SupportFAQ } from "@/lib/api/axios-client/api";
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
import { SupportFAQCreateEditDialog, type SupportFAQFormData } from "./components/support-faq-create-edit-dialog";

export function SupportFAQManagement() {
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

const loadSupportFAQQueryKey = 'support-faq'

const RenderTable = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const debouncedSearchQuery = useDebounce(searchQuery, 500);
  const [parsedData, setParsedData] = useState<Array<SupportFAQ>>([]);
  const [parsedPagination, setParsedPagination] = useState({
    pageCount: 1,
  });

  const faqDialog = useDialogControl<SupportFAQFormData>();
  const queryClient = useQueryClient();

  const loadSupportFAQQuery = useQuery({
    queryKey: [loadSupportFAQQueryKey, debouncedSearchQuery],
    queryFn: () => myApi.v1CoreSupportFaqList({
      search: debouncedSearchQuery || undefined,
      page: 1,
      pageSize: 10,
    }).then(r => r.data),
    staleTime: 0,
  });

  useEffect(() => {
    if (!loadSupportFAQQuery.data) return;
    const parsed = loadSupportFAQQuery.data.results || [];
    setParsedData(parsed);
    setParsedPagination({
      pageCount: Math.ceil(
        loadSupportFAQQuery.data.count / 10,
      ),
    });
  }, [loadSupportFAQQuery.data]);

  const totalCount = parsedData.length;

  // Dialog handlers
  const handleCreateFAQ = useCallback(() => {
    faqDialog.show(undefined);
  }, [faqDialog]);

  const handleEdit = useCallback((faq: SupportFAQ) => {
    faqDialog.show({
      id: faq.id,
      question: faq.question,
      answer: faq.answer,
      category: faq.category,
      is_active: faq.is_active ?? true,
      is_popular: faq.is_popular ?? false,
      sort_order: faq.sort_order || 1,
    });
  }, [faqDialog]);

  const handleDelete = useCallback((faq: SupportFAQ) => {
    NiceModal.show(DeleteConfirmNiceDialog, {
      title: "Delete Support FAQ",
      description: `Are you sure you want to delete "${faq.question}"? This action cannot be undone.`,
      onConfirm: () => deleteMutation.mutate(faq.id),
    });
  }, []);

  const deleteMutation = useMutation({
    mutationFn: (id: number) => myApi.v1CoreSupportFaqDestroy({ id }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [loadSupportFAQQueryKey] });
      toast.success("Support FAQ deleted successfully!");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to delete support FAQ");
    },
  });

  const getStatusColor = useCallback((isActive: boolean) => {
    return isActive ? "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400" : "bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400";
  }, []);

  const getPopularColor = useCallback((isPopular: boolean) => {
    return isPopular ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400" : "bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400";
  }, []);

  const getCategoryColor = useCallback((category: string) => {
    const colors: Record<string, string> = {
      account: "bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400",
      general: "bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-400",
      reviews: "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400",
      safety: "bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400",
      search: "bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-400",
      specialist: "bg-indigo-100 text-indigo-800 dark:bg-indigo-900/20 dark:text-indigo-400",
    };
    return colors[category] || "bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400";
  }, []);

  const columns = useMemo<ColumnDef<SupportFAQ, any>[]>(() => [
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
      accessorKey: "question",
      header: "Question",
      cell: ({ row }) => (
        <div className="font-medium max-w-xs truncate">{row.getValue("question")}</div>
      ),
    },
    {
      accessorKey: "category",
      header: "Category",
      cell: ({ row }) => {
        const category = row.getValue("category") as string;
        return (
          <Badge className={getCategoryColor(category)}>
            {category.charAt(0).toUpperCase() + category.slice(1)}
          </Badge>
        );
      },
    },
    {
      accessorKey: "is_popular",
      header: "Popular",
      cell: ({ row }) => {
        const isPopular = row.getValue("is_popular") as boolean;
        return (
          <Badge className={getPopularColor(isPopular)}>
            {isPopular ? (
              <>
                <Star className="h-3 w-3 mr-1" />
                Popular
              </>
            ) : (
              "Regular"
            )}
          </Badge>
        );
      },
    },
    {
      accessorKey: "view_count",
      header: "Views",
      cell: ({ row }) => (
        <div className="text-sm text-muted-foreground">{row.getValue("view_count")}</div>
      ),
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
        const faq = row.original;
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
                <Button variant="ghost" size="sm" className="w-full justify-start" onClick={() => handleEdit(faq)}>
                  <Edit className="h-4 w-4 mr-2" />
                  Edit
                </Button>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Button variant="ghost" size="sm" className="w-full justify-start text-red-600" onClick={() => handleDelete(faq)}>
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete
                </Button>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        );
      },
    },
  ], [getStatusColor, getPopularColor, getCategoryColor, handleEdit, handleDelete]);

  const { table } = useDataTable({
    data: parsedData,
    columns,
    pageCount: parsedPagination.pageCount,
    enableGlobalFilter: true,
    initialState: {
      sorting: [{ id: "id", desc: true }],
    },
  });

  if (loadSupportFAQQuery.isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (loadSupportFAQQuery.error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600">Error loading support FAQs</p>
        <Button onClick={() => loadSupportFAQQuery.refetch()} className="mt-2">
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
            <h3 className="text-lg font-semibold">Support FAQs</h3>
            <p className="text-sm text-muted-foreground">
              {totalCount} FAQ{totalCount !== 1 ? 's' : ''} found
            </p>
          </div>
          <Button onClick={handleCreateFAQ} className="gap-2">
            <Plus className="h-4 w-4" />
            Add FAQ
          </Button>
        </div>

        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-2">
            <div className="relative flex-1 max-w-sm">
              <SearchIcon className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search FAQs..."
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
      <SupportFAQCreateEditDialog
        control={faqDialog}
      />
    </div>
  );
};
