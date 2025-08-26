# Complete Database Schema Documentation

This document provides comprehensive database schema documentation for the kg-job-portal-my application, including all models, relationships, soft delete functionality, and database design principles.

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
- **Key Fields**: `code`, `name`, `native_name`, `is_active`, `is_default`, `flag_icon`, `rtl_support`, `locale_code`, `currency_code`
- **Relationships**: Referenced by UserProfile
- **Soft Delete**: Inherits from AbstractSoftDeleteModel

#### **ServiceCategory**
- **Purpose**: Main service categories (e.g., Cleaning, Plumbing, etc.)
- **Key Fields**: `name`, `description`, `icon`, `color`, `sort_order`, `banner_image`, `featured`, `commission_rate`, `min_price`, `max_price`, `estimated_duration_min`, `estimated_duration_max`, `meta_title`, `meta_description`, `keywords`, `slug`, `requires_license`, `requires_insurance`, `requires_background_check`
- **Relationships**: Has many ServiceSubcategories, referenced by Orders
- **Soft Delete**: Inherits from AbstractSoftDeleteModel

#### **ServiceSubcategory**
- **Purpose**: Specific services within main categories
- **Key Fields**: `name`, `description`, `icon`, `sort_order`, `image`, `featured`, `base_price`, `price_range_min`, `price_range_max`, `estimated_duration`, `complexity_level`, `required_tools`, `required_materials`, `safety_requirements`, `slug`, `meta_title`, `meta_description`
- **Relationships**: Belongs to ServiceCategory, has many ServiceAddons, referenced by Orders
- **Soft Delete**: Inherits from AbstractSoftDeleteModel

#### **ServiceAddon**
- **Purpose**: Optional add-ons for services
- **Key Fields**: `name`, `description`, `price`, `image`, `featured`, `duration_addition`, `max_quantity`, `min_quantity`, `price_type`, `requires_approval`, `prerequisites`
- **Relationships**: Belongs to ServiceSubcategory, used in Orders and ServiceProviderServices
- **Soft Delete**: Inherits from AbstractSoftDeleteModel

#### **ServicePackage**
- **Purpose**: Predefined service packages combining multiple addons
- **Key Fields**: `name`, `description`, `addons`, `package_price`, `discount_percentage`, `is_popular`, `is_best_value`, `estimated_duration`, `valid_from`, `valid_until`
- **Relationships**: Belongs to ServiceSubcategory, has many ServiceAddons
- **Soft Delete**: Inherits from AbstractSoftDeleteModel

#### **ServiceArea**
- **Purpose**: Geographic service areas
- **Key Fields**: `name`, `city`, `state`, `country`, `latitude`, `longitude`, `postal_codes`, `is_active`, `service_categories`, `base_price_multiplier`, `travel_fee`
- **Relationships**: Many-to-many with ServiceCategory
- **Soft Delete**: Inherits from AbstractSoftDeleteModel

#### **SystemSettings**
- **Purpose**: Application-wide configuration
- **Key Fields**: `key`, `value`, `description`, `is_public`, `setting_type`, `validation_regex`, `min_value`, `max_value`, `requires_admin`, `category`
- **Soft Delete**: Inherits from AbstractTimestampedModel

#### **AppVersion**
- **Purpose**: Track app versions and updates
- **Key Fields**: `version`, `build_number`, `release_notes`, `is_forced_update`, `is_active`, `release_date`, `platform`, `download_url`, `file_size`, `checksum`, `min_os_version`, `max_os_version`, `device_requirements`
- **Soft Delete**: Inherits from AbstractTimestampedModel

---

### **2. Users App (`users/`)**

#### **UserProfile**
- **Purpose**: Extended user profile for job portal functionality
- **Key Fields**: `user_type`, `bio`, `date_of_birth`, `gender`, `phone_number`, `address`, `city`, `state`, `country`, `postal_code`, `preferred_language`, `notification_preferences`, `is_verified`, `verification_date`
- **Relationships**: OneToOne with UserModel, has ServiceProviderProfile or ClientProfile
- **Soft Delete**: Inherits from AbstractSoftDeleteModel

#### **ServiceProviderProfile**
- **Purpose**: Business profile for service providers
- **Key Fields**: `business_name`, `business_description`, `business_license`, `years_of_experience`, `service_areas`, `travel_radius`, `is_available`, `availability_schedule`, `average_rating`, `total_reviews`, `is_verified_provider`, `verification_documents`
- **Relationships**: OneToOne with UserProfile, has many ServiceProviderServices
- **Soft Delete**: Inherits from AbstractSoftDeleteModel

#### **ServiceProviderService**
- **Purpose**: Services offered by providers
- **Key Fields**: `description`, `base_price`, `price_type`, `is_available`, `estimated_duration`, `available_addons`
- **Relationships**: Belongs to ServiceProviderProfile and ServiceSubcategory
- **Soft Delete**: Inherits from AbstractSoftDeleteModel

#### **ClientProfile**
- **Purpose**: Profile for service clients
- **Key Fields**: `preferred_service_areas`, `budget_preferences`, `total_orders`, `completed_orders`, `cancelled_orders`, `favorite_providers`
- **Relationships**: OneToOne with UserProfile, has many Orders
- **Soft Delete**: Inherits from AbstractSoftDeleteModel

#### **UserVerification**
- **Purpose**: Track user verification processes
- **Key Fields**: `verification_type`, `status`, `evidence`, `admin_notes`
- **Relationships**: Belongs to UserProfile
- **Soft Delete**: Inherits from AbstractTimestampedModel

---

### **3. Orders App (`orders/`)**

#### **Order**
- **Purpose**: Main service request entity
- **Key Fields**: `title`, `description`, `location`, `city`, `state`, `country`, `postal_code`, `service_date`, `service_time`, `urgency`, `budget_min`, `budget_max`, `final_price`, `status`, `published_at`, `assigned_at`, `started_at`, `completed_at`, `cancelled_at`, `attachments`, `special_requirements`, `is_featured`
- **Relationships**: Belongs to ClientProfile and ServiceSubcategory, has many Bids, OrderAddons, OrderPhotos
- **Soft Delete**: Uses cascading soft delete for related objects

#### **OrderAddon**
- **Purpose**: Add-ons selected for orders
- **Key Fields**: `quantity`, `price`
- **Relationships**: Belongs to Order and ServiceAddon
- **Soft Delete**: Inherits from AbstractSoftDeleteModel

#### **OrderPhoto**
- **Purpose**: Visual documentation for orders
- **Key Fields**: `photo_url`, `caption`, `is_primary`
- **Relationships**: Belongs to Order
- **Soft Delete**: Inherits from AbstractSoftDeleteModel

#### **Bid**
- **Purpose**: Service provider proposals for orders
- **Key Fields**: `amount`, `description`, `estimated_duration`, `status`, `accepted_at`, `rejected_at`, `withdrawn_at`, `terms_conditions`, `is_negotiable`
- **Relationships**: Belongs to Order and ServiceProviderProfile
- **Soft Delete**: Inherits from AbstractSoftDeleteModel

#### **OrderAssignment**
- **Purpose**: Assignment of orders to service providers
- **Key Fields**: `assigned_at`, `start_date`, `start_time`, `progress_notes`, `completion_notes`, `client_rating`, `client_review`
- **Relationships**: OneToOne with Order, belongs to ServiceProviderProfile and Bid
- **Soft Delete**: Inherits from AbstractTimestampedModel

#### **OrderDispute**
- **Purpose**: Handle conflicts between clients and providers
- **Key Fields**: `dispute_type`, `description`, `evidence`, `status`, `admin_notes`, `resolved_by`, `resolved_at`, `resolution`
- **Relationships**: Belongs to Order
- **Soft Delete**: Inherits from AbstractTimestampedModel

---

### **4. Chat App (`chat/`)**

#### **ChatRoom**
- **Purpose**: Communication channel between users
- **Key Fields**: `order`, `participants`, `title`, `is_active`, `last_message_at`, `chat_type`
- **Relationships**: Belongs to Order, has many ChatMessage
- **Soft Delete**: Inherits from AbstractSoftDeleteModel

#### **ChatMessage**
- **Purpose**: Individual messages in chat rooms
- **Key Fields**: `message_type`, `content`, `attachment_url`, `attachment_name`, `attachment_size`, `is_read`, `read_at`, `reply_to`
- **Relationships**: Belongs to ChatRoom and User
- **Soft Delete**: Inherits from AbstractSoftDeleteModel

#### **ChatParticipant**
- **Purpose**: Track participant status in chat rooms
- **Key Fields**: `is_online`, `last_seen`, `unread_count`, `notifications_enabled`, `mute_until`
- **Relationships**: Belongs to ChatRoom and User
- **Soft Delete**: Inherits from AbstractTimestampedModel

#### **ChatTemplate**
- **Purpose**: Predefined chat message templates
- **Key Fields**: `name`, `category`, `subject`, `content`, `variables`, `is_active`, `usage_count`
- **Relationships**: None
- **Soft Delete**: Inherits from AbstractSoftDeleteModel

#### **ChatNotification**
- **Purpose**: Chat notifications for users
- **Key Fields**: `notification_type`, `is_read`, `read_at`, `sent_via`
- **Relationships**: Belongs to User, ChatRoom, and ChatMessage
- **Soft Delete**: Inherits from AbstractTimestampedModel

#### **ChatReport**
- **Purpose**: Reports of inappropriate chat content
- **Key Fields**: `reason`, `description`, `evidence`, `status`, `admin_notes`, `resolved_by`, `resolved_at`, `action_taken`
- **Relationships**: Belongs to ChatMessage and User
- **Soft Delete**: Inherits from AbstractTimestampedModel

---

### **5. Payments App (`payments/`)**

#### **PaymentMethod**
- **Purpose**: Stored payment methods for users
- **Key Fields**: `method_type`, `card_last4`, `card_brand`, `card_exp_month`, `card_exp_year`, `bank_name`, `account_last4`, `wallet_type`, `wallet_id`, `is_default`, `is_active`, `processor_token`
- **Relationships**: Belongs to User
- **Soft Delete**: Inherits from AbstractSoftDeleteModel

#### **Invoice**
- **Purpose**: Generate invoices for payments
- **Key Fields**: `invoice_number`, `invoice_date`, `due_date`, `subtotal`, `tax_amount`, `discount_amount`, `total_amount`, `status`, `paid_amount`, `paid_date`, `notes`, `terms_conditions`
- **Relationships**: Belongs to Order, ClientProfile, and ServiceProviderProfile
- **Soft Delete**: Inherits from AbstractSoftDeleteModel

#### **Payment**
- **Purpose**: Track payment transactions
- **Key Fields**: `payment_id`, `amount`, `currency`, `status`, `transaction_id`, `processor_response`, `processed_at`, `failed_at`, `error_message`, `retry_count`, `refund_amount`, `refund_reason`, `refunded_at`
- **Relationships**: Belongs to Invoice and PaymentMethod
- **Soft Delete**: Inherits from AbstractSoftDeleteModel

#### **StripeWebhookEvent**
- **Purpose**: Stripe webhook events for tracking and debugging
- **Key Fields**: `stripe_event_id`, `event_type`, `event_data`, `processed`, `processed_at`, `error_message`, `retry_count`
- **Relationships**: None
- **Soft Delete**: Inherits from AbstractTimestampedModel

#### **PaymentProvider**
- **Purpose**: Payment provider configurations
- **Key Fields**: `name`, `is_active`, `api_key`, `secret_key`, `webhook_secret`, `test_mode`, `supported_currencies`, `config_data`
- **Relationships**: None
- **Soft Delete**: Inherits from AbstractTimestampedModel

---

### **6. Notifications App (`notifications/`)**

#### **NotificationTemplate**
- **Purpose**: Templates for different types of notifications
- **Key Fields**: `name`, `notification_type`, `subject`, `message`, `short_message`, `email_enabled`, `push_enabled`, `sms_enabled`, `in_app_enabled`, `variables`, `is_active`
- **Relationships**: Has many UserNotifications
- **Soft Delete**: Inherits from AbstractSoftDeleteModel

#### **UserNotification**
- **Purpose**: Individual notifications sent to users
- **Key Fields**: `subject`, `message`, `short_message`, `context_data`, `related_object_type`, `related_object_id`, `status`, `sent_at`, `delivered_at`, `failed_at`, `is_read`, `read_at`, `priority`
- **Relationships**: Belongs to User and NotificationTemplate
- **Soft Delete**: Inherits from AbstractSoftDeleteModel

#### **NotificationDelivery**
- **Purpose**: Track delivery of notifications across different channels
- **Key Fields**: `channel`, `status`, `sent_at`, `delivered_at`, `failed_at`, `error_message`, `retry_count`, `external_id`, `external_response`
- **Relationships**: Belongs to UserNotification
- **Soft Delete**: Inherits from AbstractTimestampedModel

#### **NotificationPreference**
- **Purpose**: User preferences for notifications
- **Key Fields**: `email_notifications`, `push_notifications`, `sms_notifications`, `in_app_notifications`, `order_updates`, `bid_notifications`, `payment_notifications`, `chat_notifications`, `promotional_notifications`, `system_notifications`, `quiet_hours_start`, `quiet_hours_end`, `timezone`, `digest_frequency`
- **Relationships**: OneToOne with User
- **Soft Delete**: Inherits from AbstractTimestampedModel

#### **NotificationLog**
- **Purpose**: Log of all notification activities for debugging and analytics
- **Key Fields**: `action`, `details`, `error_message`, `processing_time`
- **Relationships**: Belongs to UserNotification and NotificationDelivery
- **Soft Delete**: Inherits from AbstractTimestampedModel

#### **NotificationQueue**
- **Purpose**: Queue for processing notifications asynchronously
- **Key Fields**: `priority`, `scheduled_at`, `retry_count`, `max_retries`, `status`, `started_at`, `completed_at`
- **Relationships**: Belongs to UserNotification
- **Soft Delete**: Inherits from AbstractTimestampedModel

---

### **7. Analytics App (`analytics/`)**

#### **UserActivity**
- **Purpose**: Track user activity and behavior patterns
- **Key Fields**: `activity_type`, `context_data`, `ip_address`, `user_agent`, `session_id`, `related_object_type`, `related_object_id`, `response_time`
- **Relationships**: Belongs to User
- **Soft Delete**: Inherits from AbstractTimestampedModel

#### **OrderAnalytics**
- **Purpose**: Analytics data for orders and services
- **Key Fields**: `date`, `total_orders`, `new_orders`, `completed_orders`, `cancelled_orders`, `total_revenue`, `average_order_value`, `total_fees`, `total_bids`, `average_bids_per_order`, `active_clients`, `active_providers`, `new_users`
- **Relationships**: None
- **Soft Delete**: Inherits from AbstractTimestampedModel

#### **ServiceCategoryAnalytics**
- **Purpose**: Analytics for service categories
- **Key Fields**: `date`, `order_count`, `total_revenue`, `average_order_value`, `bid_count`, `completion_rate`
- **Relationships**: Belongs to ServiceCategory
- **Soft Delete**: Inherits from AbstractTimestampedModel

#### **UserRetentionAnalytics**
- **Purpose**: User retention and engagement analytics
- **Key Fields**: `date`, `user_type`, `cohort_size`, `day_1_retention`, `day_7_retention`, `day_30_retention`, `average_sessions_per_user`, `average_session_duration`
- **Relationships**: None
- **Soft Delete**: Inherits from AbstractTimestampedModel

#### **SearchAnalytics**
- **Purpose**: Analytics for search functionality
- **Key Fields**: `date`, `total_searches`, `unique_searchers`, `searches_with_results`, `searches_without_results`, `top_search_terms`, `top_categories_searched`, `searches_leading_to_orders`, `search_to_order_conversion_rate`
- **Relationships**: None
- **Soft Delete**: Inherits from AbstractTimestampedModel

#### **PerformanceMetrics**
- **Purpose**: System performance and technical metrics
- **Key Fields**: `date`, `time_period`, `average_response_time`, `max_response_time`, `min_response_time`, `total_errors`, `error_rate`, `active_users`, `concurrent_users`, `database_queries`, `cpu_usage`, `memory_usage`, `disk_usage`
- **Relationships**: None
- **Soft Delete**: Inherits from AbstractTimestampedModel

#### **BusinessMetrics**
- **Purpose**: Key business performance indicators
- **Key Fields**: `date`, `gross_merchandise_volume`, `net_revenue`, `profit_margin`, `order_fulfillment_rate`, `average_order_processing_time`, `customer_satisfaction_score`, `month_over_month_growth`, `year_over_year_growth`, `market_share`, `competitive_position`
- **Relationships**: None
- **Soft Delete**: Inherits from AbstractTimestampedModel

---

### **8. Accounts App (`accounts/`)**

#### **UserModel**
- **Purpose**: Core user model with extended functionality
- **Key Fields**: `user_type`, `blocked`, `firebase_user_id`, `fcm_token`, `name`, `email`, `description`, `photo`, `photo_url`, `friends`, `friendship_requests`, `timezone_difference`, `points`, `day_streak`, `max_day_streak`
- **Relationships**: OneToOne with UserProfile, has many Orders, Payments, Notifications
- **Soft Delete**: Inherits from AbstractCascadingSoftDeleteModel

---

## 🔄 **Soft Delete System**

### **Overview**

The application implements a comprehensive soft delete system that provides:
- **Automatic filtering** of soft-deleted objects in queries
- **Custom managers** that handle soft delete operations
- **Cascading soft delete** for related objects
- **Clean separation** of concerns (models handle deletion, views handle presentation)

### **Architecture**

#### **1. Abstract Models**

##### `AbstractSoftDeleteModel`
Basic soft delete functionality with fields:
- `is_deleted`: Boolean flag indicating deletion status
- `deleted_at`: Timestamp when object was soft deleted
- `restored_at`: Timestamp when object was restored

##### `AbstractCascadingSoftDeleteModel`
Advanced soft delete with automatic cascading to related objects.

#### **2. Custom Managers**

##### `SoftDeleteManager`
- Automatically filters out soft-deleted objects in queries
- Provides methods for working with deleted objects
- Handles bulk operations

##### `CascadingSoftDeleteManager`
- Extends `SoftDeleteManager`
- Automatically soft deletes related objects
- Handles cascading restore operations

##### `UserManager`
- Specialized manager for UserModel
- Combines soft delete with Django's user creation methods
- Provides user-specific query methods

### **Usage Examples**

#### **Basic Soft Delete**

```python
from utils.abstract_models import AbstractSoftDeleteModel

class MyModel(AbstractSoftDeleteModel):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

# Usage:
obj = MyModel.objects.create(name="Test")
obj.delete()  # Soft delete - sets is_deleted=True

# Queries automatically exclude soft-deleted objects
active_objects = MyModel.objects.all()  # Only non-deleted objects
all_objects = MyModel.objects.all_with_deleted()  # Including deleted
deleted_objects = MyModel.objects.deleted_only()  # Only deleted objects
```

#### **Cascading Soft Delete**

```python
from utils.abstract_models import AbstractCascadingSoftDeleteModel

class Company(AbstractCascadingSoftDeleteModel):
    name = models.CharField(max_length=200)
    
    def get_cascade_fields(self):
        """Specify which fields should cascade soft delete."""
        return ['jobs', 'employees']

class Job(AbstractCascadingSoftDeleteModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=200)
    
    def get_cascade_fields(self):
        return ['applications']

# Usage:
company = Company.objects.create(name="Tech Corp")
job = Job.objects.create(company=company, title="Developer")
application = Application.objects.create(job=job, applicant=user)

# Soft delete company - automatically soft deletes jobs and applications
company.delete()

# All related objects are now soft deleted
assert company.is_deleted == True
assert job.is_deleted == True
assert application.is_deleted == True
```

#### **User Model with Soft Delete**

```python
from utils.abstract_models import AbstractCascadingSoftDeleteModel

class UserModel(AbstractCascadingSoftDeleteModel):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    
    objects = UserManager()
    
    def get_cascade_fields(self):
        return ['profile', 'orders', 'payments']

# Usage:
user = UserModel.objects.create_user(username="john", email="john@example.com")
user.delete()  # Soft delete user and all related objects
```

### **Manager Methods**

#### **SoftDeleteManager Methods**

- `all()`: Returns only non-deleted objects
- `all_with_deleted()`: Returns all objects including deleted
- `deleted_only()`: Returns only deleted objects
- `restore()`: Restore a soft-deleted object
- `hard_delete()`: Permanently delete an object
- `bulk_restore()`: Restore multiple objects
- `bulk_soft_delete()`: Soft delete multiple objects

#### **CascadingSoftDeleteManager Methods**

- `cascade_delete()`: Soft delete with cascading
- `cascade_restore()`: Restore with cascading
- `get_cascade_fields()`: Define which fields cascade

### **Best Practices**

1. **Always use soft delete** for user-generated content
2. **Implement cascading** for related objects that should be deleted together
3. **Use custom managers** for consistent soft delete behavior
4. **Handle soft delete in views** for proper user experience
5. **Implement cleanup tasks** for old soft-deleted data

---

## 🗂️ **Database Indexes and Performance**

### **Primary Indexes**
- All models have primary key indexes
- Foreign key fields are automatically indexed
- Unique fields have unique indexes

### **Custom Indexes**
- `UserModel.email` - Unique index for email lookups
- `UserModel.username` - Unique index for username lookups
- `Order.status` - Index for status filtering
- `Order.created_at` - Index for date-based queries
- `ChatMessage.timestamp` - Index for message ordering
- `UserActivity.user, activity_type, created_at` - Composite index for user activity queries
- `ServiceCategoryAnalytics.category, date` - Composite index for category analytics

### **Composite Indexes**
- `Order(client_profile, status)` - For client order queries
- `Order(service_subcategory, status)` - For service-based queries
- `Bid(order, provider)` - For bid lookups

---

## 🔒 **Security and Compliance**

### **Data Protection**
- All sensitive data is encrypted at rest
- User passwords are hashed using Django's password hashers
- API keys and secrets are stored securely
- Stripe integration follows PCI compliance standards

### **Access Control**
- Role-based access control (RBAC) implementation
- API endpoints require proper authentication
- Soft delete prevents unauthorized data access
- Firebase authentication with JWT tokens

### **Audit Trail**
- All model changes are logged
- Soft delete maintains data history
- User activity is tracked for compliance
- Payment transactions are fully auditable

---

## 📊 **Scalability Considerations**

### **Database Design**
- Normalized schema for data integrity
- Efficient indexing for query performance
- Soft delete maintains referential integrity
- JSON fields for flexible data storage

### **Performance Optimization**
- Database connection pooling
- Query optimization with select_related/prefetch_related
- Caching for frequently accessed data
- Background task processing for notifications

### **Horizontal Scaling**
- Stateless application design
- Database read replicas support
- Microservices architecture ready
- WebSocket support for real-time features

---

## 🚀 **Migration Strategy**

### **Current State**
- All models use soft delete system
- Database migrations are up to date
- Soft delete fields are properly indexed
- Stripe integration is fully implemented

### **Future Considerations**
- Regular cleanup of old soft-deleted data
- Performance monitoring for soft delete queries
- Consider archiving strategy for historical data
- Implement data retention policies

---

## 📝 **Model Relationships Summary**

### **One-to-One Relationships**
- `UserModel` ↔ `UserProfile`
- `UserProfile` ↔ `ServiceProviderProfile` (conditional)
- `UserProfile` ↔ `ClientProfile` (conditional)
- `Order` ↔ `OrderAssignment`
- `UserNotification` ↔ `NotificationPreference`

### **One-to-Many Relationships**
- `ServiceCategory` → `ServiceSubcategory`
- `ServiceSubcategory` → `ServiceAddon`
- `ServiceSubcategory` → `ServicePackage`
- `UserProfile` → `UserVerification`
- `ClientProfile` → `Order`
- `Order` → `OrderAddon`
- `Order` → `OrderPhoto`
- `Order` → `Bid`
- `Order` → `OrderDispute`
- `Order` → `ChatRoom`
- `Order` → `Invoice`
- `ChatRoom` → `ChatMessage`
- `ChatRoom` → `ChatParticipant`
- `ChatRoom` → `ChatNotification`
- `User` → `UserNotification`
- `User` → `UserActivity`
- `User` → `PaymentMethod`
- `Invoice` → `Payment`
- `UserNotification` → `NotificationDelivery`
- `UserNotification` → `NotificationLog`
- `UserNotification` → `NotificationQueue`

### **Many-to-Many Relationships**
- `UserProfile` ↔ `ServiceArea` (through ServiceProviderProfile)
- `Order` ↔ `ServiceAddon` (through OrderAddon)
- `ServiceProviderProfile` ↔ `ServiceAddon` (through ServiceProviderService)
- `ServiceCategory` ↔ `ServiceArea`
- `UserModel` ↔ `UserModel` (friends, friendship_requests)
- `ClientProfile` ↔ `ServiceProviderProfile` (favorite_providers)

---

## 🔧 **Database Utilities**

### **Custom Model Methods**
- `soft_delete()`: Perform soft delete operation
- `restore()`: Restore soft-deleted object
- `is_soft_deleted()`: Check deletion status
- `get_deletion_info()`: Get deletion details
- `get_cascade_fields()`: Define cascading behavior

### **Query Utilities**
- `with_deleted()`: Include deleted objects in query
- `deleted_only()`: Query only deleted objects
- `active_only()`: Query only active objects

### **Bulk Operations**
- `bulk_soft_delete()`: Soft delete multiple objects
- `bulk_restore()`: Restore multiple objects
- `bulk_hard_delete()`: Permanently delete multiple objects

---

## 💳 **Payment Integration**

### **Stripe Integration**
- **Payment Methods**: Credit cards, debit cards, digital wallets
- **Webhook Handling**: Real-time payment status updates
- **Security**: PCI-compliant payment processing
- **Error Handling**: Comprehensive error tracking and retry logic

### **Payment Flow**
1. **Order Creation**: Client creates service request
2. **Bid Submission**: Providers submit bids
3. **Order Assignment**: Client selects provider
4. **Payment Processing**: Stripe handles payment
5. **Invoice Generation**: Automatic invoice creation
6. **Webhook Updates**: Real-time status synchronization

---

This comprehensive database schema provides a solid foundation for the job portal application with robust soft delete functionality, efficient indexing, scalable architecture, and full Stripe payment integration. The schema reflects the current implementation and provides a roadmap for future development.
