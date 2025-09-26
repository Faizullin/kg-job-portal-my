import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { OrderCreate, PatchedOrderUpdate } from '@/lib/api/axios-client/api'

interface OrderCreateState {
  // Step 1: Order Details
  title: string
  description: string
  location: string
  budget: string
  
  // Step 2: Service Selection
  serviceSubcategory: number | null
  
  // Step 3: Date and Time
  serviceDate: string | null
  serviceTime: string | null
  
  // Order ID for updates
  orderId: number | null
  
  // Actions
  setStep1Data: (data: { title: string; description: string; location?: string; budget?: string }) => void
  setStep2Data: (serviceSubcategory: number) => void
  setStep3Data: (serviceDate: string | null, serviceTime: string | null) => void
  setOrderId: (orderId: number) => void
  reset: () => void
  
  // Computed values
  getOrderCreateData: () => Partial<OrderCreate>
  getOrderUpdateData: () => Partial<PatchedOrderUpdate>
}

const initialState = {
  title: '',
  description: '',
  location: '',
  budget: '',
  serviceSubcategory: null,
  serviceDate: null,
  serviceTime: null,
  orderId: null,
}

export const useOrderCreateStore = create<OrderCreateState>()(
  persist(
    (set, get) => ({
      ...initialState,
      
      setStep1Data: (data) => set(data),
      
      setStep2Data: (serviceSubcategory) => set({ serviceSubcategory }),
      
      setStep3Data: (serviceDate, serviceTime) => set({ serviceDate, serviceTime }),
      
      setOrderId: (orderId) => set({ orderId }),
      
      reset: () => set(initialState),
      
      getOrderCreateData: () => {
        const state = get()
        return {
          title: state.title,
          description: state.description,
          location: state.location,
          service_subcategory: state.serviceSubcategory!,
          city: 'Bishkek', // Default city
          state: 'Bishkek',
          country: 'Kyrgyzstan',
          postal_code: '720000',
          service_date: state.serviceDate,
          service_time: state.serviceTime,
          budget_min: state.budget ? state.budget : undefined,
        }
      },
      
      getOrderUpdateData: () => {
        const state = get()
        return {
          title: state.title,
          description: state.description,
          location: state.location,
          service_date: state.serviceDate,
          service_time: state.serviceTime,
          budget_min: state.budget ? state.budget : undefined,
        }
      },
    }),
    {
      name: 'order-create-store',
      partialize: (state) => ({
        title: state.title,
        description: state.description,
        location: state.location,
        budget: state.budget,
        serviceSubcategory: state.serviceSubcategory,
        serviceDate: state.serviceDate,
        serviceTime: state.serviceTime,
        orderId: state.orderId,
      }),
    }
  )
)
