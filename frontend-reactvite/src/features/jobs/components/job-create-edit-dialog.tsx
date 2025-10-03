import { AttachmentsView } from "@/components/attachments/attachments-view";
import ComboBox2 from "@/components/combobox";
import { FormDialog } from "@/components/dialogs/form-dialog";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { useDialogControl } from "@/hooks/use-dialog-control";
import { UrgencyEnum, Status30eEnum, type City, type Country, type ServiceCategory, type ServiceSubcategory } from "@/lib/api/axios-client/api";
import myApi from "@/lib/api/my-api";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { format } from "date-fns";
import { ru } from "date-fns/locale";
import { ArrowLeft, ArrowRight, Calendar as CalendarIcon, Clock } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

const jobFormSchema = z.object({
  id: z.number().optional(),
  title: z.string().min(1, "Title is required").max(200, "Title must be less than 200 characters"),
  description: z.string().min(1, "Description is required").max(1000, "Description must be less than 1000 characters"),
  country: z.custom<Country>().refine(val => val && val.id && val.name, { message: "Country is required" }),
  city: z.custom<City>().refine(val => val && val.id && val.name, { message: "City is required" }),
  location: z.string().min(1, "Location is required"),
  budget_min: z.string().min(1, "Budget is required").regex(/^\d+$/, "Enter a valid amount"),
  budget_max: z.string().optional(),
  service_category: z.custom<ServiceCategory>().refine(val => val && val.id && val.name, { message: "Service category is required" }),
  service_subcategory: z.custom<ServiceSubcategory>().optional(),
  service_date: z.string().min(1, "Service date is required"),
  service_time: z.string().min(1, "Service time is required"),
  urgency: z.enum(UrgencyEnum),
  status: z.enum(Status30eEnum).optional(),
});

export type JobFormData = z.infer<typeof jobFormSchema>;

export interface FormStep {
  id: number;
  title: string;
  description: string;
  component: React.ComponentType<any>;
  validationFields: string[];
}

// Step 1 Component: Job Details
const JobDetailsStep = ({ form, selectedCountry, searchCountries, searchCities }: any) => (
  <div className="space-y-4">
    <FormField
      control={form.control}
      name="title"
      render={({ field }) => (
        <FormItem>
          <FormLabel>Job Title *</FormLabel>
          <FormControl>
            <Input placeholder="Enter job title" {...field} />
          </FormControl>
          <FormMessage />
        </FormItem>
      )}
    />

    <FormField
      control={form.control}
      name="description"
      render={({ field }) => (
        <FormItem>
          <FormLabel>Description *</FormLabel>
          <FormControl>
            <Textarea
              placeholder="Describe the job requirements..."
              className="min-h-[120px]"
              {...field}
            />
          </FormControl>
          <FormMessage />
        </FormItem>
      )}
    />

    <FormField
      control={form.control}
      name="country"
      render={({ field }) => (
        <FormItem>
          <FormLabel>Country *</FormLabel>
          <FormControl>
            <ComboBox2<Country>
              title="Select country..."
              value={field.value}
              valueKey="id"
              multiple={false}
              renderLabel={(country) => country.name}
              searchFn={searchCountries}
              onChange={field.onChange}
            />
          </FormControl>
          <FormMessage />
        </FormItem>
      )}
    />

    <FormField
      control={form.control}
      name="city"
      render={({ field }) => (
        <FormItem>
          <FormLabel>City *</FormLabel>
          <FormControl>
            <ComboBox2<City>
              title="Select city..."
              value={field.value}
              valueKey="id"
              multiple={false}
              renderLabel={(city) => city.name}
              searchFn={searchCities}
              onChange={field.onChange}
              disabled={!selectedCountry}
            />
          </FormControl>
          <FormMessage />
        </FormItem>
      )}
    />

    <FormField
      control={form.control}
      name="location"
      render={({ field }) => (
        <FormItem>
          <FormLabel>Location *</FormLabel>
          <FormControl>
            <Input placeholder="Enter specific location" {...field} />
          </FormControl>
          <FormMessage />
        </FormItem>
      )}
    />

    <div className="grid grid-cols-2 gap-4">
      <FormField
        control={form.control}
        name="budget_min"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Budget Min *</FormLabel>
            <FormControl>
              <Input placeholder="0" {...field} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />

      <FormField
        control={form.control}
        name="budget_max"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Budget Max</FormLabel>
            <FormControl>
              <Input placeholder="0" {...field} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
    </div>
  </div>
);

// Step 2 Component: Service Selection
const ServiceSelectionStep = ({ form, selectedCategory, searchServiceCategories, searchServiceSubcategories }: any) => (
  <div className="space-y-4">
    <FormField
      control={form.control}
      name="service_category"
      render={({ field }) => (
        <FormItem>
          <FormLabel>Service Category *</FormLabel>
          <FormControl>
            <ComboBox2<ServiceCategory>
              title="Select service category..."
              value={field.value}
              valueKey="id"
              multiple={false}
              renderLabel={(category) => category.name}
              searchFn={searchServiceCategories}
              onChange={field.onChange}
            />
          </FormControl>
          <FormMessage />
        </FormItem>
      )}
    />

    <FormField
      control={form.control}
      name="service_subcategory"
      render={({ field }) => (
        <FormItem>
          <FormLabel>Service Subcategory</FormLabel>
          <FormControl>
            <ComboBox2<ServiceSubcategory>
              title="Select service subcategory..."
              value={field.value}
              valueKey="id"
              multiple={false}
              renderLabel={(subcategory) => subcategory.name}
              searchFn={searchServiceSubcategories}
              onChange={field.onChange}
              disabled={!selectedCategory}
            />
          </FormControl>
          <FormMessage />
        </FormItem>
      )}
    />
  </div>
);

// Step 3 Component: Schedule
const ScheduleStep = ({ 
  form, 
  selectedDate, 
  setSelectedDate, 
  selectedTime, 
  setSelectedTime, 
  isCalendarOpen, 
  setIsCalendarOpen, 
  isTimePickerOpen, 
  setIsTimePickerOpen 
}: any) => (
  <div className="space-y-4">
    <div className="space-y-2">
      <Label>Service Date *</Label>
      <Popover open={isCalendarOpen} onOpenChange={setIsCalendarOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            className="w-full justify-start text-left font-normal"
          >
            <CalendarIcon className="mr-2 h-4 w-4" />
            {selectedDate ? (
              format(selectedDate, "PPP", { locale: ru })
            ) : (
              "Select date"
            )}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0" align="start">
          <Calendar
            mode="single"
            selected={selectedDate || undefined}
            onSelect={(date) => {
              setSelectedDate(date || null);
              form.setValue("service_date", date ? format(date, "yyyy-MM-dd") : "");
              setIsCalendarOpen(false);
            }}
            initialFocus
          />
        </PopoverContent>
      </Popover>
    </div>

    <div className="space-y-2">
      <Label>Service Time *</Label>
      <Popover open={isTimePickerOpen} onOpenChange={setIsTimePickerOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            className="w-full justify-start text-left font-normal"
          >
            <Clock className="mr-2 h-4 w-4" />
            {selectedTime || "Select time"}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0" align="start">
          <div className="p-3">
            <div className="grid grid-cols-4 gap-2">
              {Array.from({ length: 24 }, (_, i) => {
                const hour = i.toString().padStart(2, '0');
                return (
                  <Button
                    key={hour}
                    variant={selectedTime === hour ? "default" : "outline"}
                    size="sm"
                    onClick={() => {
                      setSelectedTime(hour);
                      form.setValue("service_time", hour);
                      setIsTimePickerOpen(false);
                    }}
                  >
                    {hour}:00
                  </Button>
                );
              })}
            </div>
          </div>
        </PopoverContent>
      </Popover>
    </div>

    <FormField
      control={form.control}
      name="urgency"
      render={({ field }) => (
        <FormItem>
          <FormLabel>Urgency *</FormLabel>
          <Select onValueChange={field.onChange} defaultValue={field.value}>
            <FormControl>
              <SelectTrigger>
                <SelectValue placeholder="Select urgency" />
              </SelectTrigger>
            </FormControl>
            <SelectContent>
              <SelectItem value={UrgencyEnum.low}>Low</SelectItem>
              <SelectItem value={UrgencyEnum.medium}>Medium</SelectItem>
              <SelectItem value={UrgencyEnum.high}>High</SelectItem>
              <SelectItem value={UrgencyEnum.urgent}>Urgent</SelectItem>
            </SelectContent>
          </Select>
          <FormMessage />
        </FormItem>
      )}
    />

    <FormField
      control={form.control}
      name="status"
      render={({ field }) => (
        <FormItem>
          <FormLabel>Status</FormLabel>
          <Select onValueChange={field.onChange} defaultValue={field.value}>
            <FormControl>
              <SelectTrigger>
                <SelectValue placeholder="Select status" />
              </SelectTrigger>
            </FormControl>
            <SelectContent>
              <SelectItem value={Status30eEnum.draft}>Draft</SelectItem>
              <SelectItem value={Status30eEnum.published}>Published</SelectItem>
              <SelectItem value={Status30eEnum.assigned}>Assigned</SelectItem>
              <SelectItem value={Status30eEnum.in_progress}>In Progress</SelectItem>
              <SelectItem value={Status30eEnum.completed}>Completed</SelectItem>
              <SelectItem value={Status30eEnum.cancelled}>Cancelled</SelectItem>
            </SelectContent>
          </Select>
          <FormMessage />
        </FormItem>
      )}
    />
  </div>
);

// Step 4 Component: Attachments
const AttachmentsStep = ({ 
  control, 
  loadJobAttachmentsQuery, 
  queryClient, 
  loadJobAttachmentsQueryKey 
}: any) => (
  <AttachmentsView
    attachments={loadJobAttachmentsQuery.data || []}
    onUpload={async (files) => {
      await myApi.v1JobsAttachmentsCreate({
        jobId: control.data!.id!.toString(),
        files: files
      });

      return { success: true, files };
    }}
    onDelete={async (attachment) => {
      await myApi.v1JobsAttachmentsDestroy({
        id: attachment.id.toString(),
        jobId: control.data!.id!.toString()
      });
    }}
    onUploadSuccess={() => {
      queryClient.invalidateQueries({ queryKey: loadJobAttachmentsQueryKey });
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
    }}
    onDeleteSuccess={() => {
      queryClient.invalidateQueries({ queryKey: loadJobAttachmentsQueryKey });
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
    }}
    isLoading={loadJobAttachmentsQuery.isLoading}
    title="Attachments"
    description="Upload files to attach to this job"
  />
);

// Step definitions with components
const JOB_STEPS: FormStep[] = [
  {
    id: 1,
    title: "Job Details",
    description: "Basic job information",
    component: JobDetailsStep,
    validationFields: ['title', 'description', 'country', 'city', 'location', 'budget_min'],
  },
  {
    id: 2,
    title: "Service Selection",
    description: "Choose service category and type",
    component: ServiceSelectionStep,
    validationFields: ['service_category'],
  },
  {
    id: 3,
    title: "Schedule",
    description: "Date and time planning",
    component: ScheduleStep,
    validationFields: ['service_date', 'service_time', 'urgency'],
  },
  {
    id: 4,
    title: "Attachments",
    description: "Upload related files (Edit only)",
    component: AttachmentsStep,
    validationFields: [],
  },
];

const loadJobDetailQueryKey = 'job-detail';

interface JobCreateEditDialogProps {
  control: ReturnType<typeof useDialogControl<JobFormData>>;
  onSave?: (data: JobFormData) => void;
  onCancel?: () => void;
}

export function JobCreateEditDialog({
  control,
  onSave,
  onCancel,
}: JobCreateEditDialogProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [selectedTime, setSelectedTime] = useState("");
  const [isCalendarOpen, setIsCalendarOpen] = useState(false);
  const [isTimePickerOpen, setIsTimePickerOpen] = useState(false);
  const [formReady, setFormReady] = useState(false);

  const queryClient = useQueryClient();
  const isEditMode = !!control.data?.id;

  const form = useForm<JobFormData>({
    resolver: zodResolver(jobFormSchema),
    defaultValues: {
      title: "",
      description: "",
      country: undefined,
      city: undefined,
      location: "",
      budget_min: "",
      budget_max: "",
      service_category: undefined,
      service_subcategory: undefined,
      service_date: "",
      service_time: "",
      urgency: UrgencyEnum.medium,
      status: Status30eEnum.draft,
    },
  });

  const loadJobDetailQuery = useQuery({
    queryKey: [loadJobDetailQueryKey, control.data?.id],
    queryFn: () => myApi.v1JobsRetrieve({ id: control.data!.id! }).then(r => r.data),
    enabled: isEditMode && !!control.data?.id,
  });

  const loadJobAttachmentsQueryKey = useMemo(() => ['job-attachments', control.data?.id], [control.data?.id]);
  const loadJobAttachmentsQuery = useQuery({
    queryKey: loadJobAttachmentsQueryKey,
    queryFn: () => myApi.v1JobsAttachmentsList({
      jobId: control.data!.id!.toString()
    }).then(r => r.data.results || []),
    enabled: isEditMode && !!control.data?.id,
  });

  const selectedCategory = form.watch("service_category");
  const selectedCountry = form.watch("country");

  useEffect(() => {
    if (selectedCountry && formReady && !isEditMode) {
      form.setValue("city", undefined as any);
    }
  }, [selectedCountry, form, formReady, isEditMode]);

  // Reset subcategory when category changes (only in create mode or when user manually changes category)
  useEffect(() => {
    if (selectedCategory && formReady && !isEditMode) {
      form.setValue("service_subcategory", undefined);
    }
  }, [selectedCategory, form, formReady, isEditMode]);

  // Search functions for ComboBox2
  const searchCountries = useCallback(async (search: string, offset: number, size: number) => {
    const response = await myApi.v1LocationsCountriesList({ search, page: Math.floor(offset / size) + 1, pageSize: size });
    return response.data.results || [];
  }, []);

  const searchCities = useCallback(async (search: string, offset: number, size: number) => {
    if (!selectedCountry?.id) return [];
    const response = await myApi.v1LocationsCitiesList({ country: selectedCountry.id, search, page: Math.floor(offset / size) + 1, pageSize: size });
    return (response.data.results || []) as City[];
  }, [selectedCountry]);

  const searchServiceCategories = useCallback(async (search: string, offset: number, size: number) => {
    const response = await myApi.v1CoreServiceCategoriesList({ search, isActive: true, page: Math.floor(offset / size) + 1, pageSize: size });
    return response.data.results || [];
  }, []);

  const searchServiceSubcategories = useCallback(async (search: string, offset: number, size: number) => {
    if (!selectedCategory?.id) return [];
    const response = await myApi.v1CoreServiceSubcategoriesList({ category: selectedCategory.id, search, isActive: true, page: Math.floor(offset / size) + 1, pageSize: size });
    return response.data.results || [];
  }, [selectedCategory]);

  const jobMutation = useMutation({
    mutationFn: (data: JobFormData) => {
      const jobData = {
        title: data.title,
        description: data.description,
        service_subcategory: data.service_subcategory?.id || null,
        location: data.location,
        city_id: data.city?.id || 0, // Extract ID from city object and use city_id
        service_date: data.service_date,
        service_time: data.service_time,
        urgency: data.urgency as UrgencyEnum,
        budget_min: data.budget_min,
        budget_max: data.budget_max || data.budget_min,
        special_requirements: "",
        status: data.status,
      };

      if (isEditMode && data.id) {
        return myApi.v1JobsUpdate({
          id: data.id,
          jobRequest: jobData
        });
      } else {
        return myApi.v1JobsCreate({
          jobRequest: jobData
        });
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
      if (isEditMode) {
        queryClient.invalidateQueries({ queryKey: [loadJobDetailQueryKey, control.data?.id] });
        toast.success("Job updated successfully!");
      } else {
        toast.success("Job created successfully!");
      }
      control.hide();
      onSave?.(form.getValues());
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || `Failed to ${isEditMode ? 'update' : 'create'} job`);
    },
  });

  useEffect(() => {
    if (control.isVisible) {
      if (isEditMode && loadJobDetailQuery.data) {
        const jobData = loadJobDetailQuery.data;
        const loadRelatedData = async () => {
          const [categoryData] = await Promise.all([
            jobData.service_subcategory?.category ? myApi.v1CoreServiceCategoriesRetrieve({ id: jobData.service_subcategory.category }).then((r) => r.data).catch(() => null) : Promise.resolve(null)
          ]);
        form.reset({
            id: jobData.id,
            title: jobData.title,
            description: jobData.description,
            location: jobData.location,
            budget_min: jobData.budget_min || "",
            budget_max: jobData.budget_max || "",
            service_date: jobData.service_date || "",
            service_time: jobData.service_time || "",
            urgency: jobData.urgency || UrgencyEnum.medium,
            status: jobData.status || Status30eEnum.draft,
            country: jobData.city.country,
            city: jobData.city,
            service_category: categoryData || undefined,
            service_subcategory: jobData.service_subcategory,
          });
          setFormReady(true);
        };

        loadRelatedData();
      } else if (!isEditMode) {
        form.reset({
          title: "",
          description: "",
          country: undefined,
          city: undefined,
          location: "",
          budget_min: "",
          budget_max: "",
          service_category: undefined,
          service_subcategory: undefined,
          service_date: "",
          service_time: "",
          urgency: UrgencyEnum.medium,
          status: Status30eEnum.draft,
        });
        setFormReady(true);
      }
    }
  }, [control.isVisible, isEditMode, loadJobDetailQuery.data, form]);

  const handleCancel = useCallback(() => {
    setCurrentStep(1);
    setSelectedDate(null);
    setSelectedTime("");
    setFormReady(false);
    form.reset({
      title: "",
      description: "",
      country: undefined,
      city: undefined,
      location: "",
      budget_min: "",
      budget_max: "",
      service_category: undefined,
      service_subcategory: undefined,
      service_date: "",
      service_time: "",
      urgency: UrgencyEnum.medium,
      status: Status30eEnum.draft,
    });
    control.hide();
    onCancel?.();
  }, [form, control, onCancel]);

  const handleNext = useCallback(() => {
    const maxStep = isEditMode ? 4 : 3; // 4 steps total, but create mode skips step 4
    if (currentStep < maxStep) {
      setCurrentStep(currentStep + 1);
    } else {
      // Submit form
      const values = form.getValues();
      jobMutation.mutate(values);
    }
  }, [currentStep, isEditMode, form, jobMutation]);

  const handlePrevious = useCallback(() => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    } else {
      handleCancel();
    }
  }, [currentStep, handleCancel]);

  // Create steps with components
  const steps = useMemo(() => {
    return JOB_STEPS;
  }, []);

  const currentStepData = useMemo(() => steps.find(step => step.id === currentStep), [steps, currentStep]);

  const canProceed = useCallback(() => {
    if (!formReady) return false;
    
    const currentStepData = steps.find(step => step.id === currentStep);
    if (!currentStepData) return false;
    
    // If no validation fields, step is always valid
    if (currentStepData.validationFields.length === 0) return true;
    
    // Check if all required fields have values
    const formValues = form.getValues();
    return currentStepData.validationFields.every(fieldName => {
      const value = formValues[fieldName as keyof typeof formValues];
      return value && (typeof value === 'string' ? value.trim() !== '' : true);
    });
  }, [currentStep, form, formReady, steps]);

  const renderCurrentStep = () => {
    const CurrentStepComponent = currentStepData?.component;
    if (!CurrentStepComponent) return null;

    // Pass props based on current step
    const stepProps = {
      form,
      selectedCountry,
      selectedCategory,
      searchCountries,
      searchCities,
      searchServiceCategories,
      searchServiceSubcategories,
      selectedDate,
      setSelectedDate,
      selectedTime,
      setSelectedTime,
      isCalendarOpen,
      setIsCalendarOpen,
      isTimePickerOpen,
      setIsTimePickerOpen,
      control,
      loadJobAttachmentsQuery,
      queryClient,
      loadJobAttachmentsQueryKey,
    };

    return <CurrentStepComponent {...stepProps} />;
  };

  const isLoading = jobMutation.isPending || loadJobDetailQuery.isLoading;

  return (
    <FormDialog
      open={control.isVisible}
      onOpenChange={(open) => {
        if (!open) {
          setCurrentStep(1);
          setFormReady(false);
          setSelectedDate(null);
          setSelectedTime("");
          setIsCalendarOpen(false);
          setIsTimePickerOpen(false);
          form.reset({
            title: "",
            description: "",
            country: undefined,
            city: undefined,
            location: "",
            service_category: undefined,
            service_subcategory: undefined,
            service_date: "",
            service_time: "",
            urgency: UrgencyEnum.medium,
            status: Status30eEnum.draft,
            budget_min: "",
            budget_max: "",
          });
          control.hide();
        }
      }}
      title={isEditMode ? "Edit Job" : "Create Job"}
      description={isEditMode ? "Update the job details" : "Add a new job"}
      onSubmit={form.handleSubmit(() => { })}
      onCancel={handleCancel}
      isLoading={isLoading}
      submitText={isEditMode ? "Update" : "Create"}
      maxWidth="4xl"
    >
      <Form {...form}>
        <div className="space-y-6">
          {/* Progress Steps */}
          <div className="flex items-center justify-between">
            {steps.filter(step => isEditMode || step.id !== 4).map((step, index) => (
              <div key={step.id} className="flex items-center">
                <div className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium ${currentStep >= step.id
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted text-muted-foreground'
                  }`}>
                  {step.id}
                </div>
                <div className="ml-2">
                  <div className="text-sm font-medium">{step.title}</div>
                  <div className="text-xs text-muted-foreground">{step.description}</div>
                </div>
                {index < steps.filter(step => isEditMode || step.id !== 4).length - 1 && (
                  <div className="w-8 h-px bg-border mx-4" />
                )}
              </div>
            ))}
          </div>

          {/* Step Content */}
          <div className="min-h-[400px]">
            {renderCurrentStep()}
          </div>

          {/* Navigation Buttons */}
          <div className="flex justify-between pt-6 border-t">
            <Button
              type="button"
              variant="outline"
              onClick={handlePrevious}
              disabled={currentStep === 1}
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Previous
            </Button>

            <Button
              type="button"
              onClick={handleNext}
              disabled={!canProceed() || isLoading}
            >
              {isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                  {isEditMode ? 'Updating...' : 'Creating...'}
                </>
              ) : currentStep < (isEditMode ? 4 : 3) ? (
                <>
                  Next <ArrowRight className="ml-2 h-4 w-4" />
                </>
              ) : (
                isEditMode ? 'Update Job' : 'Create Job'
              )}
            </Button>
          </div>
        </div>
      </Form>
    </FormDialog>
  );
}