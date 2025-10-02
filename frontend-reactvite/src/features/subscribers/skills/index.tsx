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
import myApi from "@/lib/api/my-api";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { type ColumnDef } from "@tanstack/react-table";
import {
  Award,
  Calendar,
  Edit,
  Loader2,
  MoreHorizontal,
  Plus,
  Star,
  Trash2,
} from "lucide-react";
import { useCallback, useMemo, useState } from "react";
import { toast } from "sonner";

// Define skill interface based on API structure
interface MasterSkill {
  id: number;
  skill: {
    id: number;
    name: string;
    category?: string;
  };
  proficiency_level: number; // 1-5 scale
  years_of_experience: number;
  is_certified: boolean;
  certification_name?: string;
  created_at: string;
  updated_at: string;
}

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
        <SkillsTable />
      </Main>
    </>
  );
}

const SKILLS_PAGE_QUERY_KEY = 'skills-page';

const SkillsTable = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [editingSkill, setEditingSkill] = useState<MasterSkill | null>(null);
  
  const queryClient = useQueryClient();

  const loadSkillsListQuery = useQuery({
    queryKey: [SKILLS_PAGE_QUERY_KEY, searchQuery],
    queryFn: async () => {
      // Using the actual API method found in the OpenAPI client
      const response = await myApi.v1UsersMySkillsList({
        search: searchQuery || undefined,
        page: 1,
        pageSize: 50,
      });
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
  });

  const skills = useMemo(() => {
    // Mock data for now - replace with actual API response when available
    return [
      {
        id: 1,
        skill: {
          id: 1,
          name: "React.js",
          category: "Frontend Development"
        },
        proficiency_level: 4,
        years_of_experience: 3,
        is_certified: true,
        certification_name: "React Developer Certification",
        created_at: "2024-01-15T10:00:00Z",
        updated_at: "2024-01-20T14:30:00Z",
      },
      {
        id: 2,
        skill: {
          id: 2,
          name: "Node.js",
          category: "Backend Development"
        },
        proficiency_level: 5,
        years_of_experience: 4,
        is_certified: false,
        created_at: "2024-01-10T09:00:00Z",
        updated_at: "2024-01-18T16:45:00Z",
      },
      {
        id: 3,
        skill: {
          id: 3,
          name: "Python",
          category: "Programming Languages"
        },
        proficiency_level: 3,
        years_of_experience: 2,
        is_certified: true,
        certification_name: "Python Institute PCAP",
        created_at: "2024-01-05T08:00:00Z",
        updated_at: "2024-01-15T12:00:00Z",
      }
    ] as MasterSkill[];
  }, []);

  const createSkillMutation = useMutation({
    mutationFn: async (skillData: Partial<MasterSkill>) => {
      // Using the actual API method
      const response = await myApi.v1UsersMySkillsCreate({
        masterSkill: skillData as any,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [SKILLS_PAGE_QUERY_KEY] });
      toast.success("Skill added successfully!");
      setShowCreateDialog(false);
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : "Failed to add skill");
    },
  });

  const updateSkillMutation = useMutation({
    mutationFn: async ({ id, ...skillData }: Partial<MasterSkill> & { id: number }) => {
      // Using the actual API method
      const response = await myApi.v1UsersMySkillsUpdate({
        id: id.toString(),
        masterSkill: skillData as any,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [SKILLS_PAGE_QUERY_KEY] });
      toast.success("Skill updated successfully!");
      setEditingSkill(null);
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : "Failed to update skill");
    },
  });

  const deleteSkillMutation = useMutation({
    mutationFn: async (id: number) => {
      // Using the actual API method
      await myApi.v1UsersMySkillsDestroy({ id: id.toString() });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [SKILLS_PAGE_QUERY_KEY] });
      toast.success("Skill deleted successfully!");
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : "Failed to delete skill");
    },
  });

  const handleCreateSkill = useCallback(() => {
    setEditingSkill(null);
    setShowCreateDialog(true);
  }, []);

  const handleEditSkill = useCallback((skill: MasterSkill) => {
    setEditingSkill(skill);
    setShowCreateDialog(true);
  }, []);

  const handleDeleteSkill = useCallback((skill: MasterSkill) => {
    if (window.confirm(`Are you sure you want to delete "${skill.skill.name}"?`)) {
      deleteSkillMutation.mutate(skill.id);
    }
  }, [deleteSkillMutation]);

  const getProficiencyColor = useCallback((level: number) => {
    if (level >= 4) return 'bg-green-100 text-green-800';
    if (level >= 3) return 'bg-blue-100 text-blue-800';
    if (level >= 2) return 'bg-yellow-100 text-yellow-800';
    return 'bg-gray-100 text-gray-800';
  }, []);

  const renderProficiencyStars = useCallback((level: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`h-3 w-3 ${
          i < level ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'
        }`}
      />
    ));
  }, []);

  const totalCount = useMemo(() => skills.length, [skills]);

  const columns = useMemo<ColumnDef<MasterSkill>[]>(() => [
    {
      accessorKey: "skill.name",
      header: "Skill",
      cell: ({ row }) => (
        <div className="max-w-[200px]">
          <div className="font-medium truncate">{row.original.skill.name}</div>
          {row.original.skill.category && (
            <div className="text-sm text-muted-foreground truncate">
              {row.original.skill.category}
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
        const level = row.getValue("proficiency_level") as number;
        return (
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1">
              {renderProficiencyStars(level)}
            </div>
            <Badge className={getProficiencyColor(level)}>
              {level}/5
            </Badge>
          </div>
        );
      },
      meta: {
        variant: "select",
        label: "Proficiency",
        options: [
          { label: "Beginner (1)", value: "1" },
          { label: "Basic (2)", value: "2" },
          { label: "Intermediate (3)", value: "3" },
          { label: "Advanced (4)", value: "4" },
          { label: "Expert (5)", value: "5" },
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
          <div className="flex items-center gap-1">
            <Calendar className="h-3 w-3 text-muted-foreground" />
            <span className="text-sm">{years} years</span>
          </div>
        );
      },
      meta: {
        variant: "number",
        label: "Experience",
        unit: "years",
        className: ""
      }
    },
    {
      accessorKey: "is_certified",
      header: "Certified",
      cell: ({ row }) => {
        const isCertified = row.getValue("is_certified") as boolean;
        const certificationName = row.original.certification_name;
        return (
          <div className="flex items-center gap-2">
            {isCertified ? (
              <>
                <Award className="h-4 w-4 text-green-600" />
                <span className="text-sm text-green-600">Yes</span>
                {certificationName && (
                  <div className="text-xs text-muted-foreground truncate max-w-[100px]" title={certificationName}>
                    {certificationName}
                  </div>
                )}
              </>
            ) : (
              <span className="text-sm text-gray-500">No</span>
            )}
          </div>
        );
      },
      meta: {
        variant: "select",
        label: "Certified",
        options: [
          { label: "Yes", value: "true" },
          { label: "No", value: "false" },
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
      cell: ({ row }) => (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="h-8 w-8 p-0">
              <span className="sr-only">Open menu</span>
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => handleEditSkill(row.original)}>
              <Edit className="mr-2 h-4 w-4" />
              Edit
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => handleDeleteSkill(row.original)}>
              <Trash2 className="mr-2 h-4 w-4" />
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      ),
    },
  ], [getProficiencyColor, renderProficiencyStars, handleEditSkill, handleDeleteSkill]);

  const { table } = useDataTable({
    data: skills,
    columns,
    pageCount: Math.ceil(totalCount / 10),
  });

  if (loadSkillsListQuery.isLoading) {
    return (
      <div className="flex items-center justify-center h-32">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (loadSkillsListQuery.error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-500">Error loading skills: {loadSkillsListQuery.error.message}</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Skills Management</h2>
          <p className="text-muted-foreground">
            Manage your professional skills and certifications.
          </p>
        </div>
        <Button onClick={handleCreateSkill}>
          <Plus className="mr-2 h-4 w-4" />
          Add Skill
        </Button>
      </div>

      <DataTable table={table}>
        <DataTableToolbar table={table} />
      </DataTable>

      {/* TODO: Add SkillCreateEditDialog component */}
      {showCreateDialog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">
              {editingSkill ? 'Edit Skill' : 'Add Skill'}
            </h3>
            <p className="text-muted-foreground">
              Skill creation/edit dialog will be implemented here.
            </p>
            <div className="flex justify-end space-x-2 mt-4">
              <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                Cancel
              </Button>
              <Button>
                {editingSkill ? 'Update' : 'Add'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
