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
import {
  MasterResumeStatusEnum,
  type MasterResume
} from "@/lib/api/axios-client/api";
import myApi from "@/lib/api/my-api";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type ColumnDef } from "@tanstack/react-table";
import {
  Calendar,
  Edit,
  MoreHorizontal,
  Plus,
  SearchIcon,
  Trash2,
} from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import { ResumeCreateEditDialog, type ResumeFormData } from "./components/resume-create-edit-dialog";

export function ResumesPage() {
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

const loadResumesQueryKey = 'resumes';

const RenderTable = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const debouncedSearchQuery = useDebounce(searchQuery, 500);
  const [parsedData, setParsedData] = useState<Array<MasterResume>>([]);
  const [parsedPagination, setParsedPagination] = useState({
    pageCount: 1,
  });

  const resumeDialog = useDialogControl<ResumeFormData>();
  const queryClient = useQueryClient();

  const loadResumesQuery = useQuery({
    queryKey: [loadResumesQueryKey, debouncedSearchQuery],
    queryFn: async () => {
      const response = await myApi.v1ResumesList({
        search: debouncedSearchQuery || undefined,
        page: 1,
        pageSize: 10,
      });
      return response.data;
    },
    staleTime: 0,
  });

  useEffect(() => {
    if (!loadResumesQuery.data) return;
    const parsed = loadResumesQuery.data.results || [];
    setParsedData(parsed);
    setParsedPagination({
      pageCount: Math.ceil(
        (loadResumesQuery.data.count || 0) / 10,
      ),
    });
  }, [loadResumesQuery.data]);

  const totalCount = parsedData.length;

  // Dialog handlers
  const handleCreateResume = useCallback(() => {
    resumeDialog.show(undefined); // Explicitly pass undefined to ensure create mode
  }, [resumeDialog]);

  const handleEditResume = useCallback((resume: MasterResume) => {
    resumeDialog.show({
      id: resume.id,
      title: resume.title,
      content: resume.content,
      status: resume.status || MasterResumeStatusEnum.draft,
    });
  }, [resumeDialog]);

  const deleteMutation = useMutation({
    mutationFn: (id: number) => myApi.v1ResumesDestroy({ id }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [loadResumesQueryKey] });
      toast.success("Resume deleted successfully!");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to delete resume");
    },
  });
  const deleteMutationMutateAsync = deleteMutation.mutateAsync;
  const handleDeleteResume = useCallback((resume: MasterResume) => {
    NiceModal.show(DeleteConfirmNiceDialog, {
      args: {
        title: "Delete Resume",
        desc: `Are you sure you want to delete "${resume.title}"? This action cannot be undone.`,
      }
    }).then((response) => {
      if (response.reason === "confirm") {
        deleteMutationMutateAsync(resume.id);
      }
    })
  }, [deleteMutationMutateAsync]);

  const getStatusColor = useCallback((status: MasterResumeStatusEnum) => {
    switch (status) {
      case MasterResumeStatusEnum.published:
        return 'bg-green-100 text-green-800';
      case MasterResumeStatusEnum.draft:
        return 'bg-yellow-100 text-yellow-800';
      case MasterResumeStatusEnum.archived:
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  }, []);

  const columns = useMemo<ColumnDef<MasterResume, any>[]>(() => [
    {
      accessorKey: "id",
      header: "ID",
      cell: ({ row }) => (
        <a className="font-mono text-sm" href="#" onClick={(e) => {
          e.preventDefault();
          handleEditResume(row.original);
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
      accessorKey: "title",
      header: "Title",
      cell: ({ row }) => (
        <div className="max-w-[300px]">
          <div className="font-medium truncate">{row.getValue("title")}</div>
          <div className="text-sm text-muted-foreground truncate">
            {row.original.content.substring(0, 100)}...
          </div>
        </div>
      ),
      meta: {
        variant: "text",
        placeholder: "Search resumes...",
        label: "Search",
        className: ""
      }
    },
    {
      accessorKey: "status",
      header: "Status",
      cell: ({ row }) => {
        const status = row.getValue("status") as MasterResumeStatusEnum;
        return (
          <Badge className={getStatusColor(status)}>
            {status?.charAt(0).toUpperCase() + status?.slice(1)}
          </Badge>
        );
      },
      meta: {
        variant: "text",
        label: "Status",
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
      accessorKey: "updated_at",
      header: "Updated",
      cell: ({ row }) => (
        <div className="flex items-center gap-1 text-sm text-muted-foreground">
          <Calendar className="h-3 w-3" />
          <span>{new Date(row.getValue("updated_at")).toLocaleDateString()}</span>
        </div>
      ),
      meta: {
        variant: "date",
        label: "Updated Date",
        className: ""
      }
    },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => {
        const resume = row.original;
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
                <Button variant="ghost" size="sm" className="w-full justify-start" onClick={() => handleEditResume(resume)}>
                  <Edit className="h-4 w-4 mr-2" />
                  Edit
                </Button>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Button variant="ghost" size="sm" className="w-full justify-start text-red-600" onClick={() => handleDeleteResume(resume)}>
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete
                </Button>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        );
      },
    },
  ], [getStatusColor, handleEditResume, handleDeleteResume]);

  const { table } = useDataTable({
    data: parsedData,
    columns,
    pageCount: parsedPagination.pageCount,
    enableGlobalFilter: true,
    initialState: {
      sorting: [{ id: "id", desc: true }],
    },
  });

  if (loadResumesQuery.isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (loadResumesQuery.error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600">Error loading resumes</p>
        <Button onClick={() => loadResumesQuery.refetch()} className="mt-2">
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
            <h3 className="text-lg font-semibold">Resumes</h3>
            <p className="text-sm text-muted-foreground">
              {totalCount} resume{totalCount !== 1 ? 's' : ''} found
            </p>
          </div>
          <Button onClick={handleCreateResume} className="gap-2">
            <Plus className="h-4 w-4" />
            Add Resume
          </Button>
        </div>

        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-2">
            <div className="relative flex-1 max-w-sm">
              <SearchIcon className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search resumes..."
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
      <ResumeCreateEditDialog
        control={resumeDialog}
      />
    </div>
  );
};
