import { createFileRoute } from '@tanstack/react-router'
import { OrderCreateStep2 } from '../../../../../features/orders/create/order-create-step2'

export const Route = createFileRoute('/_authenticated/app/orders/create/service')({
  component: OrderCreateStep2,
})