import { useNavigate } from '@tanstack/react-router'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useQuery } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { ArrowLeft } from 'lucide-react'
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useOrderCreateStore } from '@/stores/order-create-store'
import myApi from '@/lib/api/my-api'
import { serviceSelectionSchema, type ServiceSelectionForm } from './schemas'

export function OrderCreateStep2() {
  const navigate = useNavigate()
  const { serviceSubcategory, setStep2Data } = useOrderCreateStore()

  const form = useForm<ServiceSelectionForm>({
    resolver: zodResolver(serviceSelectionSchema),
    defaultValues: {
      serviceSubcategory: serviceSubcategory || undefined,
    },
  })

  const { data: services, isLoading: servicesLoading } = useQuery({
    queryKey: ['service-subcategories'],
    queryFn: async () => {
      const response = await myApi.v1CoreServiceSubcategoriesList({
        isActive: true,
        pageSize: 100,
      })
      return response.data
    },
  })

  const onSubmit = (data: ServiceSelectionForm) => {
    setStep2Data(data.serviceSubcategory)
    navigate({ to: '/app/orders/create/datetime' })
  }

  const handleBack = () => {
    navigate({ to: '/app/orders/create' })
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-blue-600 px-4 py-3 flex items-center justify-between">
        <Button
          variant="ghost"
          size="sm"
          onClick={handleBack}
          className="text-white hover:bg-blue-700 p-2"
        >
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <h1 className="text-lg font-semibold text-white">Создать заказ</h1>
        <div className="w-9" />
      </div>

      <div className="px-4 py-6">
        <div className="bg-white rounded-lg p-6 space-y-6">
          <div>
            <h2 className="text-xl font-semibold mb-2">Выберите услугу*</h2>
          </div>

          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="serviceSubcategory"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Услуга*</FormLabel>
                    <Select onValueChange={(value) => field.onChange(parseInt(value))} value={field.value?.toString()}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Выберите услугу" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {services?.results?.map((service) => (
                          <SelectItem key={service.id} value={service.id.toString()}>
                            {service.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </form>
          </Form>
        </div>
      </div>

      {/* Footer */}
      <div className="px-4 pb-6">
        <Button
          onClick={form.handleSubmit(onSubmit)}
          disabled={form.formState.isSubmitting || servicesLoading}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 text-lg font-semibold"
        >
          {form.formState.isSubmitting ? 'Загрузка...' : 'Продолжить →'}
        </Button>
      </div>
    </div>
  )
}
