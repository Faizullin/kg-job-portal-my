# API Endpoints Documentation

Complete API endpoints for the kg-job-portal-my Django backend project.

## 🔗 **API Versioning**

All endpoints use **v1** versioning: `/api/v1/{app}/{resource}/`

## 🔐 **Authentication**

### Accounts App

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/v1/auth/firebase/` | POST | Firebase authentication | None |
| `/api/v1/auth/logout/` | POST | User logout | Required |
| `/api/v1/profile/` | GET/PUT/POST/DELETE | User profile management | Required |
| `/api/v1/users/` | GET | List all users | Required |

---

## 🏗️ **Core Services**

### Core App

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/v1/core/languages/` | GET | List supported languages | None |
| `/api/v1/core/service-categories/` | GET | List service categories | None |
| `/api/v1/core/service-subcategories/` | GET | List service subcategories | None |
| `/api/v1/core/service-areas/` | GET | List geographic service areas | None |
| `/api/v1/core/system-settings/` | GET | Get system configuration | None |
| `/api/v1/core/app-versions/` | GET | Get app version info | None |

---

## 👥 **User Management**

### Users App

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/v1/users/profile/` | GET | Current user profile | Required |
| `/api/v1/users/profile/update/` | POST | Update user profile | Required |
| `/api/v1/users/client/update/` | POST | Update client profile | Required |
| `/api/v1/users/provider/update/` | POST | Update provider profile | Required |
| `/api/v1/users/providers/` | GET | List service providers | Required |
| `/api/v1/users/provider/` | GET | Current provider profile | Required |
| `/api/v1/users/clients/` | GET | List client profiles | Required |
| `/api/v1/users/client/` | GET | Current client profile | Required |

---

## 📋 **Order Management**

### Orders App

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/v1/orders/` | GET | List orders | Required |
| `/api/v1/orders/create/` | POST | Create new order | Required |
| `/api/v1/orders/<int:pk>/` | GET/PUT/DELETE | Manage specific order | Required |
| `/api/v1/orders/addons/` | GET | List order add-ons | Required |
| `/api/v1/orders/photos/` | GET | List order photos | Required |
| `/api/v1/orders/bids/` | GET | List bids | Required |
| `/api/v1/orders/<int:order_id>/bids/` | POST | Create bid for order | Required |
| `/api/v1/orders/disputes/` | GET | List order disputes | Required |
| `/api/v1/orders/<int:order_id>/disputes/` | POST | Create order dispute | Required |
| `/api/v1/orders/disputes/<int:pk>/` | GET/PUT/DELETE | Manage dispute | Required |

---

## 💰 **Payment Processing**

### Payments App

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/v1/payments/` | GET | List payments | Required |
| `/api/v1/payments/create/` | POST | Create new payment | Required |
| `/api/v1/payments/<int:pk>/` | GET/PUT/DELETE | Manage specific payment | Required |
| `/api/v1/payments/methods/` | GET | List payment methods | Required |
| `/api/v1/payments/methods/create/` | POST | Create payment method | Required |
| `/api/v1/payments/methods/<int:pk>/` | GET/PUT/DELETE | Manage payment method | Required |
| `/api/v1/payments/invoices/` | GET | List invoices | Required |
| `/api/v1/payments/invoices/create/` | POST | Create new invoice | Required |
| `/api/v1/payments/invoices/<int:pk>/` | GET/PUT/DELETE | Manage invoice | Required |

### Stripe Webhooks

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/v1/payments/webhooks/stripe/` | POST | Stripe webhook handler | Webhook Secret |
| `/api/v1/payments/webhooks/stripe/drf/` | POST | DRF webhook handler | Webhook Secret |
| `/api/v1/payments/webhooks/events/` | GET | List webhook events | Required |
| `/api/v1/payments/webhooks/events/<int:event_id>/retry/` | POST | Retry failed webhook | Required |

---

## 💬 **Real-time Communication**

### Chat App

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/v1/chat/rooms/` | GET | List chat rooms | Required |
| `/api/v1/chat/rooms/create/` | POST | Create new chat room | Required |
| `/api/v1/chat/rooms/<int:pk>/` | GET/PUT/DELETE | Manage chat room | Required |
| `/api/v1/chat/messages/` | GET | List chat messages | Required |
| `/api/v1/chat/messages/create/` | POST | Create new message | Required |
| `/api/v1/chat/messages/<int:pk>/` | GET/PUT/DELETE | Manage message | Required |
| `/api/v1/chat/participants/` | GET | List chat participants | Required |
| `/api/v1/chat/participants/create/` | POST | Add participant to chat | Required |
| `/api/v1/chat/attachments/` | GET | List chat attachments | Required |
| `/api/v1/chat/attachments/create/` | POST | Upload chat attachment | Required |
| `/api/v1/chat/attachments/<int:pk>/` | GET/PUT/DELETE | Manage chat attachment | Required |
| `/api/v1/chat/websocket-info/` | GET | WebSocket connection info | Required |

---

## 🔔 **Notification System**

### Notifications App

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/v1/notifications/` | GET | List notifications | Required |
| `/api/v1/notifications/create/` | POST | Create new notification | Required |
| `/api/v1/notifications/<int:pk>/` | GET/PUT/DELETE | Manage notification | Required |
| `/api/v1/notifications/settings/` | GET | User notification preferences | Required |
| `/api/v1/notifications/templates/` | GET | List notification templates | Required |
| `/api/v1/notifications/templates/create/` | POST | Create notification template | Required |
| `/api/v1/notifications/templates/<int:pk>/` | GET/PUT/DELETE | Manage notification template | Required |

---

## 📊 **Analytics & Reporting**

### Analytics App

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/v1/analytics/dashboard/` | GET | Main analytics dashboard | Required |
| `/api/v1/analytics/activities/` | GET | List user activities | Required |
| `/api/v1/analytics/activities/create/` | POST | Create user activity | Required |
| `/api/v1/analytics/categories/` | GET | Service category analytics | Required |
| `/api/v1/analytics/categories/create/` | POST | Create category analytics | Required |
| `/api/v1/analytics/orders/` | GET | Order-related analytics | Required |
| `/api/v1/analytics/orders/create/` | POST | Create order analytics | Required |
| `/api/v1/analytics/business/` | GET | Business metrics | Required |
| `/api/v1/analytics/business/create/` | POST | Create business metrics | Required |
| `/api/v1/analytics/performance/` | GET | Performance metrics | Required |

---

## ⭐ **Reviews & Ratings**

### Reviews App

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/v1/reviews/` | GET/POST | List and create reviews | Required |
| `/api/v1/reviews/<int:pk>/` | GET/PUT/DELETE | Manage specific review | Required |
| `/api/v1/reviews/provider/<int:provider_id>/` | GET | Get reviews for provider | Required |
| `/api/v1/reviews/order/<int:order_id>/` | GET | Get reviews for order | Required |
| `/api/v1/reviews/analytics/` | GET | Review analytics | Required |

---

## 🔍 **Search & Discovery**

### Search App

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/v1/search/global/` | GET | Global search across all content | Required |
| `/api/v1/search/orders/` | GET | Search for orders | Required |
| `/api/v1/search/providers/` | GET | Search for service providers | Required |

---

## 📚 **API Documentation**

### Interactive Documentation

- **Swagger UI**: `/api/schema/swagger-ui/`
- **ReDoc**: `/api/schema/redoc/`
- **OpenAPI Schema**: `/api/schema/`

---

## 🔐 **Authentication**

- **Firebase Authentication**: Primary method with JWT tokens
- **Session Authentication**: Fallback for web interface
- **Rate Limiting**: Applied based on endpoint type
