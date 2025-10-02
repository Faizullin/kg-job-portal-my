import ComboBox2 from "@/components/combobox";
import { BaseDialog } from "@/components/dialogs/base-dialog";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { UrgencyEnum, type City, type Country, type Job, type ServiceCategory, type ServiceSubcategory } from "@/lib/api/axios-client/api";
import myApi from "@/lib/api/my-api";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { format } from "date-fns";
import { ru } from "date-fns/locale";
import { ArrowLeft, ArrowRight, Calendar as CalendarIcon, Clock } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";


interface JobMultiStepDialogProps {
  isOpen: boolean;
  onClose: () => void;
  initialData?: Partial<JobFormData> & { id?: number };
  mode: 'create' | 'edit';
}


const step1Schema = z.object({
  title: z.string().min(1, "Название заказа обязательно"),
  description: z.string().min(1, "Описание обязательно"),
  country: z.custom<Country>().refine(val => val && val.id && val.name, { message: "Страна обязательна" }),
  city: z.custom<City>().refine(val => val && val.id && val.name, { message: "Город обязателен" }),
  location: z.string().min(1, "Адрес обязателен"),
  budget: z.string().min(1, "Бюджет обязателен").regex(/^\d+$/, "Введите корректную сумму"),
});

const step2Schema = z.object({
  service_category: z.custom<ServiceCategory>().refine(val => val && val.id && val.name, { message: "Категория услуги обязательна" }),
  service_subcategory: z.custom<ServiceSubcategory>().optional(),
});

const step3Schema = z.object({
  service_date: z.string().min(1, "Дата услуги обязательна"),
  service_time: z.string().min(1, "Время услуги обязательно"),
  urgency: z.enum(UrgencyEnum),
});

const multiStepSchema = step1Schema.merge(step2Schema).merge(step3Schema);

type JobFormData = z.infer<typeof multiStepSchema>;

const STEPS = [
  { id: 1, title: "Детали заказа", description: "Основная информация о заказе" },
  { id: 2, title: "Выберите услугу", description: "Выбор категории и типа услуги" },
  { id: 3, title: "Дата и время", description: "Планирование выполнения" },
];

export function JobMultiStepDialog({ isOpen, onClose, initialData, mode }: JobMultiStepDialogProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [selectedTime, setSelectedTime] = useState("");
  const [isCalendarOpen, setIsCalendarOpen] = useState(false);
  const [isTimePickerOpen, setIsTimePickerOpen] = useState(false);

  const queryClient = useQueryClient();

  const form = useForm<JobFormData>({
    resolver: zodResolver(multiStepSchema),
    defaultValues: {
      title: initialData?.title || "",
      description: initialData?.description || "",
      country: initialData?.country || undefined,
      city: initialData?.city || undefined,
      location: initialData?.location || "",
      budget: initialData?.budget || "",
      service_category: initialData?.service_category || undefined,
      service_subcategory: initialData?.service_subcategory || undefined,
      service_date: initialData?.service_date || "",
      service_time: initialData?.service_time || "",
      urgency: initialData?.urgency || UrgencyEnum.medium,
    }
  });

  const selectedCategory = form.watch("service_category");
  const selectedCountry = form.watch("country");

  const selectedCountryName = selectedCountry?.name;
  const selectedCategoryName = selectedCategory?.name;


  // Reset city when country changes
  useEffect(() => {
    if (selectedCountryName) {
      form.setValue("city", undefined as any);
    }
  }, [selectedCountryName, form]);

  // Reset subcategory when category changes
  useEffect(() => {
    if (selectedCategoryName) {
      form.setValue("service_subcategory", undefined);
    }
  }, [selectedCategoryName, form]);

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
    mutationFn: async (data: JobFormData) => {
      const categoryId = data.service_category?.id;
      if (!categoryId) {
        throw new Error("Пожалуйста, выберите действительную категорию услуги");
      }

      const subcategoryId = data.service_subcategory?.id || null;

      const cityId = data.city?.id;
      if (!cityId) {
        throw new Error("Пожалуйста, выберите действительный город");
      }

      const jobData: Partial<Job> = {
        title: data.title,
        description: data.description,
        service_subcategory: subcategoryId,
        location: data.location,
        city: cityId,
        service_date: data.service_date,
        service_time: data.service_time,
        urgency: data.urgency as UrgencyEnum,
        budget_min: data.budget,
        budget_max: data.budget,
        special_requirements: "",
      };

      if (mode === 'edit' && initialData?.id) {
        const response = await myApi.v1JobsUpdate({ id: initialData.id, job: jobData as Job });
        return response.data;
      } else {
        const response = await myApi.v1JobsCreate({ job: jobData as Job });
        return response.data;
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
      toast.success(mode === 'edit' ? "Заказ успешно обновлен!" : "Заказ успешно создан!");
      handleClose();
    },
    onError: (error) => {
      console.error("Job save error:", error);
      toast.error(error instanceof Error ? error.message : "Не удалось сохранить заказ");
    },
  });

  const handleClose = useCallback(() => {
    setCurrentStep(1);
    setSelectedDate(null);
    setSelectedTime("");
    form.reset();
    onClose();
  }, [form, onClose]);

  const handleNext = useCallback(() => {
    if (currentStep < STEPS.length) {
      setCurrentStep(currentStep + 1);
    } else {
      // Submit form
      const values = form.getValues();
      jobMutation.mutate(values);
    }
  }, [currentStep, form, jobMutation]);

  const handlePrevious = useCallback(() => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    } else {
      handleClose();
    }
  }, [currentStep, handleClose]);

  const canProceed = useCallback(() => {
    switch (currentStep) {
      case 1:
        return form.watch("title") && form.watch("description") && form.watch("country") && form.watch("city") && form.watch("location") && form.watch("budget");
      case 2:
        return form.watch("service_category");
      case 3:
        return form.watch("service_date") && form.watch("service_time") && form.watch("urgency");
      default:
        return false;
    }
  }, [currentStep, form]);

  const currentStepData = useMemo(() => STEPS.find(step => step.id === currentStep), [currentStep]);

  const renderStep1 = () => (
    <div className="space-y-4">
      <FormField
        control={form.control}
        name="title"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Название заказа *</FormLabel>
            <FormControl>
              <Input placeholder="Например: Собрать шкаф IKEA" {...field} />
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
            <FormLabel>Описание *</FormLabel>
            <FormControl>
              <Textarea
                placeholder="Опишите подробности работы..."
                rows={4}
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
            <FormLabel>Страна *</FormLabel>
            <FormControl>
              <ComboBox2<Country>
                title="Выберите страну..."
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

      {selectedCountryName && (
        <FormField
          control={form.control}
          name="city"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Город *</FormLabel>
              <FormControl>
                <ComboBox2<City>
                  title="Выберите город..."
                  value={field.value}
                  valueKey="id"
                  multiple={false}
                  renderLabel={(city) => city.name}
                  searchFn={searchCities}
                  onChange={field.onChange}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      )}

      <FormField
        control={form.control}
        name="location"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Адрес</FormLabel>
            <FormControl>
              <Input placeholder="Укажите адрес выполнения работы" {...field} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />

      <FormField
        control={form.control}
        name="budget"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Бюджет (сом)</FormLabel>
            <FormControl>
              <Input placeholder="Ваш бюджет" type="number" {...field} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
    </div>
  );

  const renderStep2 = () => (
    <div className="space-y-4">
      <FormField
        control={form.control}
        name="service_category"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Выберите услугу *</FormLabel>
            <FormControl>
              <ComboBox2<ServiceCategory>
                title="Выберите услугу..."
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

      {selectedCategoryName && (
        <FormField
          control={form.control}
          name="service_subcategory"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Подкатегория услуги</FormLabel>
              <FormControl>
                <ComboBox2<ServiceSubcategory>
                  title="Выберите подкатегорию..."
                  value={field.value}
                  valueKey="id"
                  multiple={false}
                  renderLabel={(subcategory) => subcategory.name}
                  searchFn={searchServiceSubcategories}
                  onChange={field.onChange}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      )}
    </div>
  );

  const renderStep3 = () => (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label>Дата *</Label>
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
                "Выберите дату"
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
              disabled={(date) => date < new Date()}
              initialFocus
            />
          </PopoverContent>
        </Popover>
      </div>

      <div className="space-y-2">
        <Label>Время *</Label>
        <Popover open={isTimePickerOpen} onOpenChange={setIsTimePickerOpen}>
          <PopoverTrigger asChild>
            <Button
              variant="outline"
              className="w-full justify-start text-left font-normal"
            >
              <Clock className="mr-2 h-4 w-4" />
              {selectedTime || "Выберите время"}
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-auto p-0" align="start">
            <div className="p-3">
              <div className="grid grid-cols-1 gap-2">
                {[
                  "09:00", "10:00", "11:00", "12:00", "13:00", "14:00",
                  "15:00", "16:00", "17:00", "18:00", "19:00", "20:00"
                ].map((time) => (
                  <Button
                    key={time}
                    variant={selectedTime === time ? "default" : "ghost"}
                    className="w-full justify-start"
                    onClick={() => {
                      setSelectedTime(time);
                      form.setValue("service_time", time);
                      setIsTimePickerOpen(false);
                    }}
                  >
                    {time}
                  </Button>
                ))}
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
            <FormLabel>Срочность</FormLabel>
            <Select onValueChange={field.onChange} defaultValue={field.value}>
              <FormControl>
                <SelectTrigger>
                  <SelectValue placeholder="Выберите срочность" />
                </SelectTrigger>
              </FormControl>
              <SelectContent>
                <SelectItem value={UrgencyEnum.low}>Низкая</SelectItem>
                <SelectItem value={UrgencyEnum.medium}>Средняя</SelectItem>
                <SelectItem value={UrgencyEnum.high}>Высокая</SelectItem>
                <SelectItem value={UrgencyEnum.urgent}>Срочно</SelectItem>
              </SelectContent>
            </Select>
            <FormMessage />
          </FormItem>
        )}
      />
    </div>
  );

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 1:
        return renderStep1();
      case 2:
        return renderStep2();
      case 3:
        return renderStep3();
      default:
        return null;
    }
  };

  const dialogContent = (
    <div className="flex-1 overflow-auto">
      <Card className="w-full border-0 shadow-none">
        <CardHeader>
          <CardTitle className="text-lg">{currentStepData?.title} *</CardTitle>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form className="space-y-4">
              {renderCurrentStep()}
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );

  const dialogFooter = (
    <div className="mt-4">
      <Button
        onClick={handleNext}
        disabled={!canProceed() || jobMutation.isPending}
        className={`w-full ${canProceed() && !jobMutation.isPending
            ? "bg-blue-600 hover:bg-blue-700"
            : "bg-blue-300 cursor-not-allowed"
          } text-white py-4 text-lg font-semibold`}
      >
        {jobMutation.isPending ? (
          <>
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
            {mode === 'edit' ? 'Обновление...' : 'Создание...'}
          </>
        ) : currentStep < STEPS.length ? (
          <>
            Продолжить <ArrowRight className="ml-2 h-5 w-5" />
          </>
        ) : (
          mode === 'edit' ? 'Обновить заказ' : 'Создать заказ'
        )}
      </Button>
    </div>
  );

  return (
    <BaseDialog
      open={isOpen}
      onOpenChange={handleClose}
      title={mode === 'edit' ? 'Редактировать заказ' : 'Создать заказ'}
      maxWidth="md"
      footer={dialogFooter}
    >
      {/* Custom Header */}
      <div className="bg-blue-600 text-white -m-6 mb-6 p-6 rounded-t-lg">
        <div className="flex items-center">
          <Button
            variant="ghost"
            size="sm"
            onClick={handlePrevious}
            className="text-white hover:bg-blue-700 p-2 mr-3"
          >
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <span className="text-xl font-bold">
            {mode === 'edit' ? 'Редактировать заказ' : 'Создать заказ'}
          </span>
        </div>
      </div>

      {dialogContent}
    </BaseDialog>
  );
}
