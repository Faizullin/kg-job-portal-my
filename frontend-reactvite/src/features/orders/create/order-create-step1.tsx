import { useNavigate } from '@tanstack/react-router'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import { ArrowLeft } from 'lucide-react'
import { useOrderCreateStore } from '@/stores/order-create-store'
import { orderDetailsSchema, type OrderDetailsForm } from './schemas'

export function OrderCreateStep1() {
  const navigate = useNavigate()
  const { title, description, location, budget, setStep1Data } = useOrderCreateStore()

  const form = useForm<OrderDetailsForm>({
    resolver: zodResolver(orderDetailsSchema),
    defaultValues: {
      title: title || '',
      description: description || '',
      location: location || '',
      budget: budget || '',
    },
  })

  const onSubmit = (data: OrderDetailsForm) => {
    setStep1Data(data)
    navigate({ to: '/app/orders/create/service' })
  }

  const handleBack = () => {
    navigate({ to: '/app/client' })
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
            <h2 className="text-xl font-semibold mb-2">Детали заказа*</h2>
          </div>

          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="title"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Название заказа*</FormLabel>
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
                    <FormLabel>Описание*</FormLabel>
                    <FormControl>
                      <Textarea placeholder="Опишите подробности работы..." className="min-h-[100px]" {...field} />
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
                      <Input type="number" placeholder="Ваш бюджет" {...field} />
                    </FormControl>
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
          disabled={form.formState.isSubmitting}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 text-lg font-semibold"
        >
          {form.formState.isSubmitting ? 'Загрузка...' : 'Продолжить →'}
        </Button>
      </div>
    </div>
  )
}
