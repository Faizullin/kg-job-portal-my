import { useState } from 'react'
import { useNavigate } from '@tanstack/react-router'
import { useMutation } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { ArrowLeft, CheckCircle, Calendar, Clock, MapPin, DollarSign } from 'lucide-react'
import { useOrderCreateStore } from '@/stores/order-create-store'
import myApi from '@/lib/api/my-api'
import { format } from 'date-fns'
import { ru } from 'date-fns/locale'

export function OrderCreateStep4() {
  const navigate = useNavigate()
  const { 
    title, 
    description, 
    location, 
    budget, 
    serviceDate, 
    serviceTime, 
    orderId,
    reset 
  } = useOrderCreateStore()
  
  const [isLoading, setIsLoading] = useState(false)

  const publishOrderMutation = useMutation({
    mutationFn: async () => {
      if (!orderId) throw new Error('No order ID')
      const response = await myApi.v1OrdersUpdate(orderId, {
        title,
        description,
        location,
        city: 'Bishkek',
        state: 'Bishkek',
        country: 'Kyrgyzstan',
        postal_code: '720000',
        service_date: serviceDate,
        service_time: serviceTime,
        budget_min: budget || null,
        status: 'published'
      })
      return response.data
    },
    onSuccess: () => {
      reset()
      navigate({ to: '/app/client' })
    },
    onError: (error) => {
      console.error('Failed to publish order:', error)
    },
  })

  const handlePublish = async () => {
    setIsLoading(true)
    try {
      publishOrderMutation.mutate()
    } finally {
      setIsLoading(false)
    }
  }

  const handleBack = () => {
    navigate({ to: '/app/orders/create/datetime' })
  }

  const handleEdit = () => {
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
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Проверьте заказ</h2>
            <Button variant="outline" size="sm" onClick={handleEdit}>
              Редактировать
            </Button>
          </div>

          <div className="space-y-4">
            <div className="border rounded-lg p-4 space-y-3">
              <h3 className="font-semibold text-lg">{title}</h3>
              <p className="text-gray-600">{description}</p>
            </div>

            <div className="grid grid-cols-1 gap-3">
              {location && (
                <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                  <MapPin className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="text-sm text-gray-500">Адрес</p>
                    <p className="font-medium">{location}</p>
                  </div>
                </div>
              )}

              {serviceDate && (
                <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                  <Calendar className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="text-sm text-gray-500">Дата</p>
                    <p className="font-medium">
                      {format(new Date(serviceDate), 'PPP', { locale: ru })}
                    </p>
                  </div>
                </div>
              )}

              {serviceTime && (
                <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                  <Clock className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="text-sm text-gray-500">Время</p>
                    <p className="font-medium">{serviceTime}</p>
                  </div>
                </div>
              )}

              {budget && (
                <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                  <DollarSign className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="text-sm text-gray-500">Бюджет</p>
                    <p className="font-medium">{budget} сом</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="px-4 pb-6 space-y-3">
        <Button
          onClick={handlePublish}
          disabled={isLoading || publishOrderMutation.isPending}
          className="w-full bg-green-600 hover:bg-green-700 text-white py-3 text-lg font-semibold"
        >
          {isLoading || publishOrderMutation.isPending ? (
            'Публикация...'
          ) : (
            <>
              <CheckCircle className="mr-2 h-5 w-5" />
              Опубликовать заказ
            </>
          )}
        </Button>
        
        <Button
          variant="outline"
          onClick={handleBack}
          className="w-full"
        >
          Назад
        </Button>
      </div>
    </div>
  )
}
