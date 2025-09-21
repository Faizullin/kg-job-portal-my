# 📱 MOBILE APP SCREENS

## **INITIAL LOADING & ACCOUNT CREATION**

### **SCREEN 1: SPLASH/LOGO**
**Description:** App startup screen with logo
**Actions:** App initialization, check user auth status
**Conditions:** None
**API Requests:** None
**Models:** None

### **SCREEN 2: PHONE REGISTRATION**
**Description:** Enter phone number for registration
**Actions:** Enter phone number, send SMS verification code
**Conditions:** Valid phone number format
**API Requests:**
```
POST /api/v1/auth/firebase/
Body: { "phone_number": "+996..." }
```
**Models:** `UserModel.phone_number`

### **SCREEN 3: SMS CONFIRMATION**
**Description:** Enter 4-digit SMS verification code
**Actions:** Enter verification code, verify phone
**Conditions:** Valid 4-digit code
**API Requests:** Firebase OTP verification
**Models:** Firebase handles verification

### **SCREEN 4: TERMS ACCEPTANCE**
**Description:** Accept terms and conditions
**Actions:** Read terms, accept legal terms
**Conditions:** Must accept terms to continue
**API Requests:**
```
POST /api/v1/users/profile/update/
Body: { "terms_accepted": true, "terms_accepted_at": "2024-01-15T10:30:00Z" }
```
**Models:** `UserProfile.terms_accepted`, `UserProfile.terms_accepted_at`

### **SCREEN 5: ROLE SELECTION**
**Description:** Choose "I'm looking for services" or "I offer services"
**Actions:** Select user role (client or service provider)
**Conditions:** Must select one role
**API Requests:**
```
POST /api/v1/users/profile/update/
Body: { "user_type": "client" | "service_provider" }
```
**Models:** `UserProfile.user_type`

### **SCREEN 6: PERSONAL INFORMATION**
**Description:** Enter name, email, accept terms
**Actions:** Fill personal details, upload avatar
**Conditions:** Required fields: first_name, last_name, email
**API Requests:**
```
POST /api/v1/users/profile/advanced/
Body: { "user_data": { "first_name": "...", "last_name": "...", "email": "..." } }
```
**Models:** `UserModel.first_name`, `UserModel.last_name`, `UserModel.email`

### **SCREEN 7: CLIENT SERVICE PREFERENCES**
**Description:** Select preferred service types (only for clients)
**Actions:** Choose services of interest from dropdown
**Conditions:** Only shown if user_type = "client"
**API Requests:**
```
GET /api/v1/core/service-subcategories/
POST /api/v1/users/client/update/
Body: { "preferred_services": [1, 2, 3] }
```
**Models:** `ClientProfile.preferred_services` (ServiceSubcategory)

### **SCREEN 8: PROVIDER SETUP**
**Description:** Complete provider profile (only for service providers)
**Actions:** Services offered → Address → Work modes → Service areas → Photo
**Conditions:** Only shown if user_type = "service_provider"
**API Requests:**
```
GET /api/v1/core/service-subcategories/
GET /api/v1/core/service-areas/
POST /api/v1/users/provider/update/
POST /api/v1/profile/avatar/
```
**Models:** `ServiceProviderProfile.services_offered`, `ServiceProviderProfile.service_areas`, work modes

---

## **MAIN FUNCTIONS**

### **SCREEN 9: HOME/DASHBOARD**
**Description:** Main dashboard with featured providers and categories
**Actions:** Load featured providers, browse categories, search services, view top specialists
**Conditions:** User must be authenticated
**API Requests:**
```
GET /api/v1/users/providers/featured/
GET /api/v1/core/service-categories/
GET /api/v1/core/service-subcategories/
```
**Models:** `ServiceCategory`, `ServiceSubcategory`, `ServiceProviderProfile`

### **SCREEN 10: SELECT MASTER**
**Description:** Browse and filter service providers
**Actions:** Search providers, filter by location/rating, view provider cards, select provider
**Conditions:** User must be authenticated, can filter by location, rating, service type
**API Requests:**
```
GET /api/v1/users/providers/?search=cleaning&is_verified_provider=true
GET /api/v1/core/service-areas/
```
**Models:** `ServiceProviderProfile`, `ServiceArea`, `ServiceSubcategory`, `Review`

### **SCREEN 11: MASTER PROFILE**
**Description:** Detailed provider profile with stats and reviews
**Actions:** View complete profile, see work examples, reviews, contact provider, create order
**Conditions:** User must be authenticated, provider must be available
**API Requests:**
```
GET /api/v1/users/providers/{id}/details/
GET /api/v1/orders/bids/?provider={id}
```
**Models:** `ServiceProviderProfile`, `Order`, `Review`, `UserModel`, `ServiceSubcategory`

---

## **ORDER CREATION FLOW**

### **SCREEN 12: ORDER DETAILS**
**Description:** "Создать заказ" - Order details form
**Actions:** Fill order name, description, address, budget
**Conditions:** User must be authenticated client, required fields: title, description
**API Requests:**
```
POST /api/v1/orders/create/
Body: { "title": "Собрать шкаф IKEA", "description": "Опишите подробности работы...", "location": "Адрес выполнения", "budget_min": 100, "budget_max": 200 }
```
**Models:** `Order.title`, `Order.description`, `Order.location`, `Order.budget_min`, `Order.budget_max`

### **SCREEN 13: SERVICE SELECTION**
**Description:** "Выберите услугу" - Choose service type
**Actions:** Select service from dropdown
**Conditions:** Order must be created, service must be available
**API Requests:**
```
GET /api/v1/core/service-subcategories/
POST /api/v1/orders/{id}/update/
Body: { "service_subcategory": 1 }
```
**Models:** `Order.service_subcategory` (ServiceSubcategory)

### **SCREEN 14: DATE & TIME SELECTION**
**Description:** "Выберите дату и время" - Schedule the service
**Actions:** Select date from calendar, choose time from picker
**Conditions:** Order must have service selected, date must be future
**API Requests:**
```
POST /api/v1/orders/{id}/update/
Body: { "service_date": "2024-01-20", "service_time": "14:30:00" }
```
**Models:** `Order.service_date`, `Order.service_time`

---

## **CHAT/MESSAGES**

### **SCREEN 15: MESSAGES LIST**
**Description:** "Сообщения" - List of chat conversations
**Actions:** View conversation list, search dialogues, see unread counts, online status
**Conditions:** User must be authenticated, shows conversations with unread counts
**API Requests:**
```
GET /api/v1/chat/conversations/
GET /api/v1/chat/conversations/?search=maria
```
**Models:** `ChatRoom`, `ChatMessage`, `ChatParticipant`, `UserModel`

### **SCREEN 16: INDIVIDUAL CHAT**
**Description:** Chat with specific user (e.g., Maria Gonzalez)
**Actions:** Send/receive messages, share images, see online status, view service info
**Conditions:** User must be participant in chat room
**API Requests:**
```
GET /api/v1/chat/conversations/{id}/
POST /api/v1/chat/conversations/{id}/send/
Body: { "message": "Hi! I can start tomorrow...", "message_type": "text" }
ws://domain/ws/chat/{id}/?token={token}
```
**Models:** `ChatMessage`, `ChatRoom`, `UserModel`, `Order`

---

## **ORDERS MANAGEMENT**

### **SCREEN 17: MY ORDERS (CLIENT)**
**Description:** Client's order management screen
**Actions:** View active orders, completed orders, order history
**Conditions:** User must be authenticated client
**API Requests:**
```
GET /api/v1/orders/?status=active
GET /api/v1/orders/?status=completed
```
**Models:** `Order`, `Bid`, `OrderAssignment`

### **SCREEN 18: MY APPLICATIONS (PROVIDER)**
**Description:** Provider's bid applications screen
**Actions:** View sent bids, accepted bids, rejected bids, bid history
**Conditions:** User must be authenticated provider
**API Requests:**
```
GET /api/v1/orders/bids/?status=pending
GET /api/v1/orders/bids/?status=accepted
```
**Models:** `Bid`, `Order`, `ServiceProviderProfile`

### **SCREEN 19: INCOMING APPLICATIONS (CLIENT)**
**Description:** Client's incoming bid applications screen
**Actions:** View received bids, accept/reject bids, see provider details
**Conditions:** User must be authenticated client with active orders
**API Requests:**
```
GET /api/v1/orders/bids/?order__client__user_profile__user={user_id}
POST /api/v1/orders/bids/{id}/accept/
POST /api/v1/orders/bids/{id}/reject/
```
**Models:** `Bid`, `Order`, `ServiceProviderProfile`

---

## **PROFILE MANAGEMENT**

### **SCREEN 20: MY PROFILE**
**Description:** User's profile management screen
**Actions:** Edit profile info, upload avatar, change settings, view task history, reviews, notifications, support
**Conditions:** User must be authenticated
**API Requests:**
```
GET /api/v1/users/profile/advanced/
POST /api/v1/users/profile/advanced/
GET /api/v1/users/task-history/
GET /api/v1/orders/reviews/?reviewer={user_id}
GET /api/v1/notifications/
GET /api/v1/core/support/faq/
```
**Models:** `UserModel`, `UserProfile`, `ServiceProviderProfile`, `ClientProfile`, `Order`, `Review`, `UserNotification`

### **SCREEN 21: EDIT PROFILE**
**Description:** Edit profile information
**Actions:** Update profile data, delete account, logout
**Conditions:** User must be authenticated
**API Requests:**
```
POST /api/v1/users/profile/advanced/
```
**Models:** `UserModel`, `UserProfile`

### **SCREEN 22: REVIEWS**
**Description:** User's reviews given and received
**Actions:** View reviews, leave reviews
**Conditions:** User must be authenticated
**API Requests:**
```
GET /api/v1/orders/reviews/?reviewer={user_id}
GET /api/v1/orders/reviews/?provider={provider_id}
POST /api/v1/orders/reviews/
```
**Models:** `Review`, `Order`, `ServiceProviderProfile`

### **SCREEN 23: NOTIFICATION SETTINGS**
**Description:** Configure notification preferences
**Actions:** Toggle SMS, push notifications, mailings
**Conditions:** User must be authenticated
**API Requests:**
```
GET /api/v1/users/profile/
POST /api/v1/users/profile/update/
```
**Models:** `UserProfile.notification_preferences`

### **SCREEN 24: SUPPORT**
**Description:** Support FAQ and contact support
**Actions:** Browse FAQ, contact support chat
**Conditions:** None (FAQ public, support requires auth)
**API Requests:**
```
GET /api/v1/core/support/faq/
GET /api/v1/core/support/faq/?category=general
GET /api/v1/chat/conversations/?chat_type=support
```
**Models:** `SupportFAQ`, `ChatRoom`

### **SCREEN 25: ABOUT APP**
**Description:** App information and legal links
**Actions:** View app version, device info, legal documents, social media
**Conditions:** None
**API Requests:**
```
GET /api/v1/core/app-versions/
GET /api/v1/core/system-settings/
```
**Models:** `AppVersion`, `SystemSettings`

### **SCREEN 26: APP RATING**
**Description:** Rate app with predefined options
**Actions:** Select rating options, submit feedback
**Conditions:** User must be authenticated
**API Requests:**
```
POST /api/v1/reviews/feedback/
Body: { "rating_options": ["excellent_design", "everything_suits"], "app_version": "1.01.1", "device_info": "iPhone 15.0.4" }
```
**Models:** `AppFeedback`

### **SCREEN 27: DETAILED FEEDBACK**
**Description:** Detailed feedback form
**Actions:** Write detailed feedback, submit
**Conditions:** User must be authenticated
**API Requests:**
```
POST /api/v1/reviews/feedback/
Body: { "detailed_feedback": "Describe your experience here...", "app_version": "1.01.1", "device_info": "iPhone 15.0.4" }
```
**Models:** `AppFeedback`

---

## **NAVIGATION FLOW:**

### **Bottom Navigation:**
- **Главная (Home):** Screen 9 (Dashboard)
- **Мастера (Masters):** Screen 10 (Select Master)  
- **Сообщения (Messages):** Screen 15 (Messages List)
- **Заказы (Orders):** Screen 17/18 (My Orders/Applications)
- **Профиль (Profile):** Screen 20 (My Profile)

### **Screen Triggers:**
- **Order Creation:** Screen 11 (Master Profile) → Screen 12 (Order Details)
- **Chat Access:** Screen 15 (Messages List) → Screen 16 (Individual Chat)
- **Bid Management:** Screen 17 (My Orders) → Screen 19 (Incoming Applications)
- **Profile Setup:** Screen 2-8 (Registration Flow) → Screen 20 (My Profile)
