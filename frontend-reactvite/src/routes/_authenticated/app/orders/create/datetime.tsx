import { createFileRoute } from '@tanstack/react-router'
import { OrderCreateStep3 } from '../../../../../features/orders/create/order-create-step3'

export const Route = createFileRoute('/_authenticated/app/orders/create/datetime')({
  component: OrderCreateStep3,
})