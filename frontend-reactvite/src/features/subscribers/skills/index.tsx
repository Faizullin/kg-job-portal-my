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
  ProficiencyLevelEnum,
  type MasterSkill,
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
import { SkillsCreateEditDialog, type SkillsFormData } from "./components/skills-create-edit-dialog";

export function SkillsPage() {
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

const loadSkillsQueryKey = 'skills';

const RenderTable = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const debouncedSearchQuery = useDebounce(searchQuery, 500);
  const [parsedData, setParsedData] = useState<Array<MasterSkill>>([]);
  const [parsedPagination, setParsedPagination] = useState({
    pageCount: 1,
  });

  const skillsDialog = useDialogControl<SkillsFormData>();
  const queryClient = useQueryClient();

  const loadSkillsQuery = useQuery({
    queryKey: [loadSkillsQueryKey, debouncedSearchQuery],
    queryFn: async () => {
      const response = await myApi.v1UsersMySkillsList({
        search: debouncedSearchQuery || undefined,
        page: 1,
        pageSize: 10,
      });
      return response.data;
    },
    staleTime: 0,
  });

  useEffect(() => {
    if (!loadSkillsQuery.data) return;
    const parsed = loadSkillsQuery.data.results || [];
    setParsedData(parsed);
    setParsedPagination({
      pageCount: Math.ceil(
        (loadSkillsQuery.data.count || 0) / 10,
      ),
    });
  }, [loadSkillsQuery.data]);

  const totalCount = parsedData.length;

  const handleCreateSkill = useCallback(() => {
    skillsDialog.show(undefined);
  }, [skillsDialog]);

  const handleEditSkill = useCallback((skill: MasterSkill) => {
    skillsDialog.show({
      id: skill.id,
      skill: skill.skill,
      is_primary_skill: skill.is_primary_skill || false,
      proficiency_level: skill.proficiency_level || ProficiencyLevelEnum.beginner,
      years_of_experience: skill.years_of_experience || 0,
    });
  }, [skillsDialog]);

  const deleteMutation = useMutation({
    mutationFn: (id: number) => myApi.v1UsersMySkillsDestroy({ id: id.toString() }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [loadSkillsQueryKey] });
      toast.success("Skill deleted successfully!");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to delete skill");
    },
  });
  const deleteMutationMutateAsync = deleteMutation.mutateAsync;
  const handleDeleteSkill = useCallback((skill: MasterSkill) => {
    NiceModal.show(DeleteConfirmNiceDialog, {
      args: {
        title: "Delete Skill",
        desc: `Are you sure you want to delete "${skill.skill.name}"? This action cannot be undone.`,
      }
    }).then((response) => {
      if (response.reason === "confirm") {
        deleteMutationMutateAsync(skill.id);
      }
    })
  }, [deleteMutationMutateAsync]);

  const getProficiencyColor = useCallback((level: ProficiencyLevelEnum) => {
    switch (level) {
      case ProficiencyLevelEnum.expert:
        return 'bg-purple-100 text-purple-800';
      case ProficiencyLevelEnum.advanced:
        return 'bg-blue-100 text-blue-800';
      case ProficiencyLevelEnum.intermediate:
        return 'bg-green-100 text-green-800';
      case ProficiencyLevelEnum.beginner:
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  }, []);

  const columns = useMemo<ColumnDef<MasterSkill, any>[]>(() => [
    {
      accessorKey: "id",
      header: "ID",
      cell: ({ row }) => (
        <a className="font-mono text-sm" href="#" onClick={(e) => {
          e.preventDefault();
          handleEditSkill(row.original);
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
      accessorKey: "skill.name",
      header: "Skill",
      cell: ({ row }) => (
        <div className="max-w-[300px]">
          <div className="font-medium truncate">{row.original.skill.name}</div>
          {row.original.skill.description && (
            <div className="text-sm text-muted-foreground truncate">
              {row.original.skill.description.substring(0, 100)}...
            </div>
          )}
        </div>
      ),
      meta: {
        variant: "text",
        placeholder: "Search skills...",
        label: "Search",
        className: ""
      }
    },
    {
      accessorKey: "proficiency_level",
      header: "Proficiency",
      cell: ({ row }) => {
        const level = row.getValue("proficiency_level") as ProficiencyLevelEnum;
        return (
          <Badge className={getProficiencyColor(level)}>
            {level?.charAt(0).toUpperCase() + level?.slice(1)}
          </Badge>
        );
      },
      meta: {
        variant: "select",
        label: "Proficiency",
        options: [
          { label: "Beginner", value: ProficiencyLevelEnum.beginner },
          { label: "Intermediate", value: ProficiencyLevelEnum.intermediate },
          { label: "Advanced", value: ProficiencyLevelEnum.advanced },
          { label: "Expert", value: ProficiencyLevelEnum.expert },
        ],
        className: ""
      }
    },
    {
      accessorKey: "years_of_experience",
      header: "Experience",
      cell: ({ row }) => {
        const years = row.getValue("years_of_experience") as number;
        return (
          <div className="text-sm">
            {years || 0} year{years !== 1 ? 's' : ''}
          </div>
        );
      },
      meta: {
        variant: "number",
        label: "Years of Experience",
        className: ""
      }
    },
    {
      accessorKey: "is_primary_skill",
      header: "Primary",
      cell: ({ row }) => {
        const isPrimary = row.getValue("is_primary_skill") as boolean;
        return (
          <Badge variant={isPrimary ? "default" : "secondary"}>
            {isPrimary ? "Primary" : "Secondary"}
          </Badge>
        );
      },
      meta: {
        variant: "select",
        label: "Primary Skill",
        options: [
          { label: "Primary", value: "true" },
          { label: "Secondary", value: "false" },
        ],
        className: ""
      }
    },
    {
      accessorKey: "created_at",
      header: "Added",
      cell: ({ row }) => (
        <div className="flex items-center gap-1 text-sm text-muted-foreground">
          <Calendar className="h-3 w-3" />
          <span>{new Date(row.getValue("created_at")).toLocaleDateString()}</span>
        </div>
      ),
      meta: {
        variant: "date",
        label: "Added Date",
        className: ""
      }
    },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => {
        const skill = row.original;
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
                <Button variant="ghost" size="sm" className="w-full justify-start" onClick={() => handleEditSkill(skill)}>
                  <Edit className="h-4 w-4 mr-2" />
                  Edit
                </Button>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Button variant="ghost" size="sm" className="w-full justify-start text-red-600" onClick={() => handleDeleteSkill(skill)}>
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete
                </Button>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        );
      },
    },
  ], [getProficiencyColor, handleEditSkill, handleDeleteSkill]);

  const { table } = useDataTable({
    data: parsedData,
    columns,
    pageCount: parsedPagination.pageCount,
    enableGlobalFilter: true,
    initialState: {
      sorting: [{ id: "id", desc: true }],
    },
  });

  if (loadSkillsQuery.isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (loadSkillsQuery.error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600">Error loading skills</p>
        <Button onClick={() => loadSkillsQuery.refetch()} className="mt-2">
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
            <h3 className="text-lg font-semibold">Skills</h3>
            <p className="text-sm text-muted-foreground">
              {totalCount} skill{totalCount !== 1 ? 's' : ''} found
            </p>
          </div>
          <Button onClick={handleCreateSkill} className="gap-2">
            <Plus className="h-4 w-4" />
            Add Skill
          </Button>
        </div>

        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-2">
            <div className="relative flex-1 max-w-sm">
              <SearchIcon className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search skills..."
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
      <SkillsCreateEditDialog
        control={skillsDialog}
      />
    </div>
  );
};