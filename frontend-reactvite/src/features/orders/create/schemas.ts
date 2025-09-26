import { z } from 'zod'

export const orderDetailsSchema = z.object({
  title: z.string().min(1, 'Название заказа обязательно'),
  description: z.string().min(1, 'Описание обязательно'),
  location: z.string().optional(),
  budget: z.string().optional(),
})

export const serviceSelectionSchema = z.object({
  serviceSubcategory: z.number().min(1, 'Выберите услугу'),
})

export const dateTimeSchema = z.object({
  serviceDate: z.date({ required_error: 'Выберите дату' }),
  serviceTime: z.string().optional(),
})

export const orderCreateSchema = z.object({
  ...orderDetailsSchema.shape,
  ...serviceSelectionSchema.shape,
  ...dateTimeSchema.shape,
})

export type OrderDetailsForm = z.infer<typeof orderDetailsSchema>
export type ServiceSelectionForm = z.infer<typeof serviceSelectionSchema>
export type DateTimeForm = z.infer<typeof dateTimeSchema>
export type OrderCreateForm = z.infer<typeof orderCreateSchema>
