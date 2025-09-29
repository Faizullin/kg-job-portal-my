import { createFileRoute } from '@tanstack/react-router'
import { OrderCreateStep4 } from '../../../../../features/orders/create/order-create-step4'

export const Route = createFileRoute('/_authenticated/app/jobs/create/review')({
  component: OrderCreateStep4,
})