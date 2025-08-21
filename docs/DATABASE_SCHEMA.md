# Database Schema Documentation

This document outlines the comprehensive database schema for the kg-job-portal-my application, designed based on the user flow analysis and business requirements.

## 🏗️ **Architecture Overview**

The application follows a modular architecture with separate Django apps for different functionalities, all integrated through the main job_portal app. Each app handles specific business logic while maintaining clean separation of concerns.

## 📱 **App Structure**

```
job_portal/
├── apps/
│   ├── core/           # Core services, categories, languages
│   ├── users/          # User profiles, verification, roles
│   ├── orders/         # Order management, bidding, disputes
│   ├── chat/           # Communication system
│   ├── payments/       # Payment processing, invoices, subscriptions
│   ├── notifications/  # Notification system
│   └── analytics/      # Business intelligence, metrics
└── models.py           # Main app models (if needed)
```

## 🗄️ **Database Schema**

### **1. Core App (`core/`)**

#### **Language**
- **Purpose**: Multi-language support for the application
- **Key Fields**: `code`, `name`, `native_name`, `is_active`, `is_default`
- **Relationships**: Referenced by UserProfile

#### **ServiceCategory**
- **Purpose**: Main service categories (e.g., Cleaning, Plumbing, etc.)
- **Key Fields**: `name`, `description`, `icon`, `color`, `sort_order`
- **Relationships**: Has many ServiceSubcategories, referenced by Orders

#### **ServiceSubcategory**
- **Purpose**: Specific services within main categories
- **Key Fields**: `name`, `description`, `icon`, `sort_order`
- **Relationships**: Belongs to ServiceCategory, has many ServiceAddons, referenced by Orders

#### **ServiceAddon**
- **Purpose**: Optional add-ons for services
- **Key Fields**: `name`, `description`, `price`
- **Relationships**: Belongs to ServiceSubcategory, used in Orders and ServiceProviderServices

#### **SystemSettings**
- **Purpose**: Application-wide configuration
- **Key Fields**: `key`, `value`, `description`, `is_public`

#### **AppVersion**
- **Purpose**: Track app versions and updates
- **Key Fields**: `version`, `build_number`, `release_notes`, `is_forced_update`

---

### **2. Users App (`users/`)**

#### **UserProfile**
- **Purpose**: Extended user profile for job portal functionality
- **Key Fields**: `user_type`, `bio`, `contact_info`, `preferences`, `verification_status`
- **Relationships**: OneToOne with UserModel, has ServiceProviderProfile or ClientProfile

#### **ServiceProviderProfile**
- **Purpose**: Business profile for service providers
- **Key Fields**: `business_name`, `experience`, `service_areas`, `availability`, `ratings`
- **Relationships**: OneToOne with UserProfile, has many ServiceProviderServices

#### **ServiceProviderService**
- **Purpose**: Services offered by providers
- **Key Fields**: `description`, `base_price`, `price_type`, `availability`
- **Relationships**: Belongs to ServiceProviderProfile and ServiceSubcategory

#### **ClientProfile**
- **Purpose**: Profile for service clients
- **Key Fields**: `preferences`, `order_history`, `favorite_providers`
- **Relationships**: OneToOne with UserProfile, has many Orders

#### **UserVerification**
- **Purpose**: Track user verification processes
- **Key Fields**: `verification_type`, `status`, `evidence`, `admin_notes`
- **Relationships**: Belongs to UserProfile

---

### **3. Orders App (`orders/`)**

#### **Order**
- **Purpose**: Main service request entity
- **Key Fields**: `title`, `description`, `location`, `budget`, `status`, `timestamps`
- **Relationships**: Belongs to ClientProfile and ServiceSubcategory, has many Bids, OrderAddons, OrderPhotos
- **Soft Delete**: Uses cascading soft delete for related objects

#### **OrderAddon**
- **Purpose**: Add-ons selected for orders
- **Key Fields**: `quantity`, `price`
- **Relationships**: Belongs to Order and ServiceAddon

#### **OrderPhoto**
- **Purpose**: Photos attached to orders
- **Key Fields**: `photo_url`, `caption`, `is_primary`
- **Relationships**: Belongs to Order

#### **Bid**
- **Purpose**: Service provider bids on orders
- **Key Fields**: `amount`, `description`, `estimated_duration`, `status`
- **Relationships**: Belongs to Order and ServiceProviderProfile

#### **OrderAssignment**
- **Purpose**: Assignment of orders to providers
- **Key Fields**: `start_date`, `progress_notes`, `client_rating`
- **Relationships**: OneToOne with Order, references accepted Bid

#### **OrderDispute**
- **Purpose**: Handle order-related disputes
- **Key Fields**: `dispute_type`, `description`, `evidence`, `resolution`
- **Relationships**: Belongs to Order

---

### **4. Chat App (`chat/`)**

#### **ChatRoom**
- **Purpose**: Communication channels between users
- **Key Fields**: `title`, `chat_type`, `is_active`, `last_message_at`
- **Relationships**: Belongs to Order, has many participants and messages

#### **ChatMessage**
- **Purpose**: Individual chat messages
- **Key Fields**: `message_type`, `content`, `attachments`, `is_read`
- **Relationships**: Belongs to ChatRoom, can reply to other messages

#### **ChatParticipant**
- **Purpose**: Track participant status in chat rooms
- **Key Fields**: `is_online`, `last_seen`, `unread_count`, `notification_preferences`
- **Relationships**: Belongs to ChatRoom and UserModel

#### **ChatTemplate**
- **Purpose**: Predefined message templates
- **Key Fields**: `name`, `category`, `content`, `variables`
- **Relationships**: Standalone entity

#### **ChatNotification**
- **Purpose**: Chat-related notifications
- **Key Fields**: `notification_type`, `status`, `delivery_channels`
- **Relationships**: Belongs to UserModel and ChatRoom

#### **ChatReport**
- **Purpose**: Report inappropriate chat content
- **Key Fields**: `reason`, `description`, `evidence`, `status`
- **Relationships**: Belongs to ChatMessage

---

### **5. Payments App (`payments/`)**

#### **PaymentMethod**
- **Purpose**: User payment methods
- **Key Fields**: `method_type`, `card_info`, `bank_info`, `wallet_info`
- **Relationships**: Belongs to UserModel, has many Payments

#### **Invoice**
- **Purpose**: Billing for orders and services
- **Key Fields**: `invoice_number`, `amounts`, `status`, `due_date`
- **Relationships**: Belongs to Order, ClientProfile, and ServiceProviderProfile

#### **InvoiceItem**
- **Purpose**: Individual items on invoices
- **Key Fields**: `description`, `quantity`, `unit_price`, `total_price`
- **Relationships**: Belongs to Invoice

#### **Payment**
- **Purpose**: Payment transactions
- **Key Fields**: `payment_id`, `amount`, `status`, `processor_response`
- **Relationships**: Belongs to Invoice and PaymentMethod

#### **Refund**
- **Purpose**: Handle payment refunds
- **Key Fields**: `refund_id`, `amount`, `reason`, `status`
- **Relationships**: Belongs to Payment and Invoice

#### **Subscription**
- **Purpose**: Subscription plans for service providers
- **Key Fields**: `plan_details`, `pricing`, `features`, `billing_cycle`
- **Relationships**: Belongs to ServiceProviderProfile

---

### **6. Notifications App (`notifications/`)**

#### **NotificationTemplate**
- **Purpose**: Templates for different notification types
- **Key Fields**: `name`, `notification_type`, `content`, `channels`
- **Relationships**: Has many UserNotifications

#### **UserNotification**
- **Purpose**: Individual notifications sent to users
- **Key Fields**: `subject`, `message`, `status`, `priority`, `context_data`
- **Relationships**: Belongs to UserModel and NotificationTemplate

#### **NotificationDelivery**
- **Purpose**: Track notification delivery across channels
- **Key Fields**: `channel`, `status`, `timestamps`, `external_response`
- **Relationships**: Belongs to UserNotification

#### **NotificationPreference**
- **Purpose**: User notification preferences
- **Key Fields**: `channel_preferences`, `type_preferences`, `timing_preferences`
- **Relationships**: OneToOne with UserModel

#### **NotificationLog**
- **Purpose**: Log notification activities
- **Key Fields**: `action`, `details`, `performance_metrics`
- **Relationships**: Belongs to UserNotification

#### **NotificationQueue**
- **Purpose**: Queue for processing notifications
- **Key Fields**: `priority`, `scheduled_at`, `retry_count`, `status`
- **Relationships**: Belongs to UserNotification

---

### **7. Analytics App (`analytics/`)**

#### **UserActivity**
- **Purpose**: Track user behavior and actions
- **Key Fields**: `activity_type`, `context_data`, `performance_metrics`
- **Relationships**: Belongs to UserModel

#### **OrderAnalytics**
- **Purpose**: Daily order and financial metrics
- **Key Fields**: `order_counts`, `revenue_metrics`, `user_metrics`
- **Relationships**: Standalone entity

#### **ServiceCategoryAnalytics**
- **Purpose**: Performance metrics by service category
- **Key Fields**: `order_count`, `revenue`, `completion_rate`
- **Relationships**: Belongs to ServiceCategory

#### **UserRetentionAnalytics**
- **Purpose**: User retention and engagement metrics
- **Key Fields**: `cohort_metrics`, `retention_rates`, `engagement_metrics`
- **Relationships**: Standalone entity

#### **SearchAnalytics**
- **Purpose**: Search functionality performance
- **Key Fields**: `search_metrics`, `popular_terms`, `conversion_rates`
- **Relationships**: Standalone entity

#### **PerformanceMetrics**
- **Purpose**: System performance and technical metrics
- **Key Fields**: `response_times`, `error_rates`, `infrastructure_metrics`
- **Relationships**: Standalone entity

#### **BusinessMetrics**
- **Purpose**: Key business performance indicators
- **Key Fields**: `financial_kpis`, `operational_kpis`, `growth_metrics`
- **Relationships**: Standalone entity

---

## 🔗 **Key Relationships**

### **User Flow Relationships**
1. **Client Journey**: UserProfile → ClientProfile → Order → Bid → OrderAssignment → ChatRoom
2. **Provider Journey**: UserProfile → ServiceProviderProfile → ServiceProviderService → Bid → OrderAssignment
3. **Payment Flow**: Order → Invoice → Payment → Refund (if needed)
4. **Communication**: Order → ChatRoom → ChatMessage → Notification

### **Soft Delete Cascading**
- **Order**: Cascades to Bids, OrderAddons, OrderPhotos
- **ServiceCategory**: Cascades to ServiceSubcategories and related Orders
- **UserProfile**: Cascades to related profiles and services

### **Audit Trail**
- All models include `created_at` and `updated_at` timestamps
- Soft delete models include `deleted_at` and `restored_at` timestamps
- User activity tracking for compliance and analytics

---

## 📊 **Database Indexes**

### **Performance Indexes**
- User activity tracking: `(user, activity_type, created_at)`
- Order queries: `(status, created_at)`, `(client, status)`
- Chat messages: `(chat_room, created_at)`
- Payment tracking: `(status, created_at)`
- Analytics queries: `(date, category)` for time-series data

### **Soft Delete Indexes**
- `is_deleted` field indexed on all soft delete models
- Composite indexes with soft delete status for efficient queries

---

## 🚀 **Scalability Considerations**

### **Data Partitioning**
- Analytics tables can be partitioned by date
- Chat messages can be partitioned by chat room or date
- User activities can be partitioned by user or date

### **Caching Strategy**
- Service categories and subcategories cached for performance
- User preferences and settings cached
- Popular search terms and analytics cached

### **Archival Strategy**
- Old analytics data archived to data warehouse
- Completed orders older than X years archived
- Chat messages older than X months archived

---

## 🔒 **Security & Privacy**

### **Data Encryption**
- Payment method details encrypted
- Personal identification information encrypted
- Chat messages encrypted in transit and at rest

### **Access Control**
- Role-based access control (RBAC)
- Data isolation between clients and providers
- Admin-only access to sensitive analytics

### **Compliance**
- GDPR compliance for user data
- Audit trails for all data modifications
- Data retention policies implemented

---

## 📈 **Migration Strategy**

### **Phase 1: Core Infrastructure**
1. Core app models and basic user management
2. Service categories and basic structure

### **Phase 2: User Management**
1. User profiles and verification system
2. Service provider and client profiles

### **Phase 3: Order Management**
1. Order creation and management
2. Bidding system and order assignment

### **Phase 4: Communication & Payments**
1. Chat system implementation
2. Payment processing and invoicing

### **Phase 5: Analytics & Optimization**
1. Analytics data collection
2. Performance monitoring and optimization

---

This schema provides a robust foundation for the job portal application, supporting all the user flows identified in the flowchart while maintaining scalability, security, and maintainability.
