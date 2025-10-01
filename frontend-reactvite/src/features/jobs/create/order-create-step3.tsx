import { Button } from '@/components/ui/button'
import { Calendar as CalendarComponent } from '@/components/ui/calendar'
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import myApi from '@/lib/api/my-api'
import { useOrderCreateStore } from '@/stores/order-create-store'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation } from '@tanstack/react-query'
import { useNavigate } from '@tanstack/react-router'
import { format } from 'date-fns'
import { ru } from 'date-fns/locale'
import { ArrowLeft, Calendar, Clock } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { dateTimeSchema, type DateTimeForm } from './schemas'

export function OrderCreateStep3() {
    const navigate = useNavigate()
    const {
        serviceDate,
        serviceTime,
        setStep3Data,
        setOrderId,
        getOrderCreateData
    } = useOrderCreateStore()

    const form = useForm<DateTimeForm>({
        resolver: zodResolver(dateTimeSchema),
        defaultValues: {
            serviceDate: serviceDate ? new Date(serviceDate) : undefined,
            serviceTime: serviceTime || '',
        },
    })

    const createOrderMutation = useMutation({
        mutationFn: async (orderData: any) => {
            const response = await myApi.v1OrdersCreateCreate(orderData)
            return response.data
        },
        onSuccess: (data: any) => {
            const orderId = (data as any).id
            if (orderId) {
                setOrderId(orderId)
                navigate({ to: '/app/jobs/create/review' })
            } else {
                console.error('No order ID returned from create order API')
            }
        },
        onError: (error) => {
            console.error('Failed to create order:', error)
        },
    })

    const onSubmit = (data: DateTimeForm) => {
        const orderData = getOrderCreateData()
        orderData.service_date = data.serviceDate.toISOString().split('T')[0]
        orderData.service_time = data.serviceTime || null

        setStep3Data(orderData.service_date, orderData.service_time)
        createOrderMutation.mutate(orderData)
    }

    const handleBack = () => {
        navigate({ to: '/app/jobs/create/service' })
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
                        <h2 className="text-xl font-semibold mb-2">Выберите дату и время*</h2>
                    </div>

                    <Form {...form}>
                        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                            <FormField
                                control={form.control}
                                name="serviceDate"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Дата*</FormLabel>
                                        <Popover>
                                            <PopoverTrigger asChild>
                                                <FormControl>
                                                    <Button
                                                        variant="outline"
                                                        className="w-full justify-start text-left font-normal"
                                                    >
                                                        <Calendar className="mr-2 h-4 w-4" />
                                                        {field.value ? format(field.value, 'PPP', { locale: ru }) : 'Выберите дату'}
                                                    </Button>
                                                </FormControl>
                                            </PopoverTrigger>
                                            <PopoverContent className="w-auto p-0" align="start">
                                                <CalendarComponent
                                                    mode="single"
                                                    selected={field.value}
                                                    onSelect={field.onChange}
                                                    locale={ru}
                                                />
                                            </PopoverContent>
                                        </Popover>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />

                            <FormField
                                control={form.control}
                                name="serviceTime"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Время</FormLabel>
                                        <div className="relative">
                                            <Clock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                                            <FormControl>
                                                <Input
                                                    type="time"
                                                    className="pl-10"
                                                    {...field}
                                                />
                                            </FormControl>
                                        </div>
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
                    disabled={form.formState.isSubmitting || createOrderMutation.isPending}
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 text-lg font-semibold"
                >
                    {form.formState.isSubmitting || createOrderMutation.isPending ? 'Загрузка...' : 'Продолжить →'}
                </Button>
            </div>
        </div>
    )
}