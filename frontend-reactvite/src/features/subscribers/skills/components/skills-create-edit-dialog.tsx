import ComboBox2 from "@/components/combobox";
import { FormDialog } from "@/components/dialogs/form-dialog";
import { Checkbox } from "@/components/ui/checkbox";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useDialogControl } from "@/hooks/use-dialog-control";
import type { SkillDetail } from "@/lib/api/axios-client";
import { ProficiencyLevelEnum } from "@/lib/api/axios-client/api";
import myApi from "@/lib/api/my-api";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback, useEffect } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

const skillsFormSchema = z.object({
    id: z.number().optional(),
    skill: z.object({
        id: z.number(),
        name: z.string(),
        description: z.string().optional(),
        category: z.number(),
        is_active: z.boolean().optional(),
    }).optional().refine((skill) => skill !== undefined, {
        message: "Skill is required",
    }),
    is_primary_skill: z.boolean().optional(),
    proficiency_level: z.nativeEnum(ProficiencyLevelEnum).optional(),
    years_of_experience: z.number().min(0, "Years of experience cannot be negative").max(50, "Years of experience cannot exceed 50").optional(),
});

export type SkillsFormData = z.infer<typeof skillsFormSchema>;

const loadSkillDetailQueryKey = 'skill-detail';

interface SkillsCreateEditDialogProps {
    control: ReturnType<typeof useDialogControl<SkillsFormData>>;
    onSave?: (data: SkillsFormData) => void;
    onCancel?: () => void;
}

export function SkillsCreateEditDialog({
    control,
    onSave,
    onCancel,
}: SkillsCreateEditDialogProps) {
    const queryClient = useQueryClient();
    const isEditMode = !!control.data?.id;

    const form = useForm<SkillsFormData>({
        resolver: zodResolver(skillsFormSchema),
        defaultValues: {
            skill: undefined,
            is_primary_skill: false,
            proficiency_level: ProficiencyLevelEnum.beginner,
            years_of_experience: 0,
        },
    });

    const loadSkillDetailQuery = useQuery({
        queryKey: [loadSkillDetailQueryKey, control.data?.id],
        queryFn: () => myApi.v1UsersMySkillsRetrieve({ id: control.data!.id!.toString() }).then(r => r.data),
        enabled: isEditMode && !!control.data?.id,
    });

    const searchSkills = useCallback(async (search: string, offset: number, size: number): Promise<SkillDetail[]> => {
        try {
            const response = await myApi.v1UsersSkillsList({
                search: search || undefined,
                page: Math.floor(offset / size) + 1,
                pageSize: size,
                isActive: true,
            });
            return response.data.results || [];
        } catch (error) {
            console.error("Error searching skills:", error);
            return [];
        }
    }, []);


    const createMutation = useMutation({
        mutationFn: (data: SkillsFormData) => {
            const { id, ...createData } = data;
            return myApi.v1UsersMySkillsCreate({
                masterSkillRequest: {
                    skill_id: createData.skill?.id || 0,
                    is_primary_skill: createData.is_primary_skill || false,
                    proficiency_level: createData.proficiency_level || ProficiencyLevelEnum.beginner,
                    years_of_experience: createData.years_of_experience || 0,
                }
            });
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['skills'] });
            toast.success("Skill added successfully!");
            control.hide();
            onSave?.(form.getValues());
        },
        onError: (error: any) => {
            toast.error(error.response?.data?.detail || "Failed to add skill");
        },
    });

    const updateMutation = useMutation({
        mutationFn: (data: SkillsFormData) => {
            const { id, ...updateData } = data;
            return myApi.v1UsersMySkillsPartialUpdate({
                id: control.data!.id!.toString(),
                patchedMasterSkillRequest: {
                    skill_id: updateData.skill?.id,
                    is_primary_skill: updateData.is_primary_skill,
                    proficiency_level: updateData.proficiency_level,
                    years_of_experience: updateData.years_of_experience,
                }
            });
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['skills'] });
            queryClient.invalidateQueries({ queryKey: [loadSkillDetailQueryKey, control.data?.id] });
            toast.success("Skill updated successfully!");
            control.hide();
            onSave?.(form.getValues());
        },
        onError: (error: any) => {
            toast.error(error.response?.data?.detail || "Failed to update skill");
        },
    });

    useEffect(() => {
        if (control.isVisible) {
            if (isEditMode && loadSkillDetailQuery.data) {
                form.reset({
                    id: loadSkillDetailQuery.data.id,
                    skill: loadSkillDetailQuery.data.skill,
                    is_primary_skill: loadSkillDetailQuery.data.is_primary_skill || false,
                    proficiency_level: loadSkillDetailQuery.data.proficiency_level || ProficiencyLevelEnum.beginner,
                    years_of_experience: loadSkillDetailQuery.data.years_of_experience || 0,
                });
            } else if (!isEditMode) {
                form.reset({
                    skill: undefined,
                    is_primary_skill: false,
                    proficiency_level: ProficiencyLevelEnum.beginner,
                    years_of_experience: 0,
                });
            }
        }
    }, [control.isVisible, isEditMode, loadSkillDetailQuery.data, form]);

    const onSubmit = (data: SkillsFormData) => {
        if (isEditMode) {
            updateMutation.mutate(data);
        } else {
            createMutation.mutate(data);
        }
    };

    const handleCancel = () => {
        form.reset({
            skill: undefined,
            is_primary_skill: false,
            proficiency_level: ProficiencyLevelEnum.beginner,
            years_of_experience: 0,
        });
        control.hide();
        onCancel?.();
    };

    const isLoading = createMutation.isPending || updateMutation.isPending || loadSkillDetailQuery.isLoading;

    return (
        <FormDialog
            open={control.isVisible}
            onOpenChange={(open) => {
                if (!open) {
                    form.reset({
                        skill: undefined,
                        is_primary_skill: false,
                        proficiency_level: ProficiencyLevelEnum.beginner,
                        years_of_experience: 0,
                    });
                    control.hide();
                }
            }}
            title={isEditMode ? "Edit Skill" : "Add Skill"}
            description={isEditMode ? "Update your skill details" : "Add a new skill to your profile"}
            onSubmit={form.handleSubmit(onSubmit)}
            onCancel={handleCancel}
            isLoading={isLoading}
            submitText={isEditMode ? "Update" : "Add"}
            maxWidth="2xl"
        >
            <Form {...form}>
                <div className="space-y-4">
                    <FormField
                        control={form.control}
                        name="skill"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Skill *</FormLabel>
                                <FormControl>
                                    <ComboBox2<SkillDetail>
                                        title="Search and select a skill..."
                                        value={field.value}
                                        valueKey="id"
                                        multiple={false}
                                        disabled={isLoading}
                                        renderLabel={(skill) => skill.name}
                                        searchFn={searchSkills}
                                        onChange={field.onChange}
                                    />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="proficiency_level"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Proficiency Level</FormLabel>
                                <Select onValueChange={field.onChange} defaultValue={field.value} disabled={isLoading}>
                                    <FormControl>
                                        <SelectTrigger>
                                            <SelectValue placeholder="Select proficiency level" />
                                        </SelectTrigger>
                                    </FormControl>
                                    <SelectContent>
                                        <SelectItem value={ProficiencyLevelEnum.beginner}>Beginner</SelectItem>
                                        <SelectItem value={ProficiencyLevelEnum.intermediate}>Intermediate</SelectItem>
                                        <SelectItem value={ProficiencyLevelEnum.advanced}>Advanced</SelectItem>
                                        <SelectItem value={ProficiencyLevelEnum.expert}>Expert</SelectItem>
                                    </SelectContent>
                                </Select>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="years_of_experience"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Years of Experience</FormLabel>
                                <FormControl>
                                    <Input
                                        type="number"
                                        min="0"
                                        max="50"
                                        placeholder="Enter years of experience"
                                        {...field}
                                        onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
                                        disabled={isLoading}
                                    />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="is_primary_skill"
                        render={({ field }) => (
                            <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                                <FormControl>
                                    <Checkbox
                                        checked={field.value}
                                        onCheckedChange={field.onChange}
                                        disabled={isLoading}
                                    />
                                </FormControl>
                                <div className="space-y-1 leading-none">
                                    <FormLabel>Primary Skill</FormLabel>
                                    <p className="text-sm text-muted-foreground">
                                        Mark this as one of your primary skills
                                    </p>
                                </div>
                            </FormItem>
                        )}
                    />
                </div>
            </Form>
        </FormDialog>
    );
}
