import { createFileRoute } from '@tanstack/react-router'
import { OrderCreateStep1 } from '../../../../../features/orders/create/order-create-step1'

export const Route = createFileRoute('/_authenticated/app/orders/create/')({
  component: OrderCreateStep1,
})