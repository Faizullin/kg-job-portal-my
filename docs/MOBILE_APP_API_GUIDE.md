# 📱 Mobile App API Integration Guide

## 🎯 Overview
This guide provides step-by-step API integration instructions for building a mobile job portal app. All examples are in Postman format with complete request/response data.

**Base URL:** `https://your-domain.com/api/v1`

---

## 📖 How the Job Portal Works

### **Core Concept**
The job portal connects **Clients** (who need work done) with **Service Providers** (who offer services). It follows a simple workflow: job posting → application → selection → project completion.

### **Key Terms & Entities**

#### 🏢 **Order (Job)**
- A job posting created by a **Client**
- Contains: title, description, budget range, deadline, required skills
- **Status flow**: `draft` → `published` → `bidding` → `assigned` → `in_progress` → `completed`
- Example: "Build a React Native mobile app for food delivery"

#### 💼 **Bid (Application)**
- A **Service Provider's** application to work on an **Order**
- Contains: proposed price, estimated hours, delivery time, detailed proposal
- **Status flow**: `pending` → `accepted`/`rejected`/`withdrawn`
- Example: "I can build your app for $4,500 in 5 weeks"

#### 👥 **User Roles**
- **Client**: Posts jobs, reviews applications, hires providers
- **Service Provider**: Browses jobs, submits applications, delivers work
- **Both**: Users can be both clients and providers

#### 📋 **Assignment**
- Created automatically when a Client **accepts** a Bid
- Links the Order, chosen Provider, and accepted Bid
- Tracks project progress and deliverables

#### 💬 **Chat System**
- Real-time messaging between Clients and Providers
- Auto-created when an assignment is made
- Used for project communication and file sharing

---

## 🔄 Complete User Journey

### **For Clients (Job Posters)**
1. **Register** → Create client profile
2. **Post Job** → Create order with requirements
3. **Review Applications** → View incoming bids from providers
4. **Select Provider** → Accept the best bid (auto-creates assignment)
5. **Manage Project** → Chat with provider, track progress
6. **Complete & Review** → Mark project done, leave feedback

### **For Service Providers (Freelancers)**
1. **Register** → Create provider profile with skills/portfolio
2. **Browse Jobs** → Search available orders by category/budget
3. **Apply** → Submit bids with proposals and pricing
4. **Get Hired** → Receive acceptance notification
5. **Deliver Work** → Complete project, update progress
6. **Get Paid** → Receive payment, collect reviews

---

## 💼 Portfolio & History Construction

### **🎨 Service Provider Portfolio System**

The backend provides multiple layers for service providers to showcase their work and build credibility:

#### **📋 Profile Foundation**
- **Business Profile**: Company name, description, years of experience
- **Avatar Upload**: Profile picture via `/api/v1/profile/` endpoint
- **Bio & Details**: Professional summary, location, contact info
- **Skills & Categories**: JSON field for service areas and specializations

#### **📊 Work History Tracking**
- **Completed Orders**: Automatic tracking via `OrderAssignment` model
- **Reviews & Ratings**: Client feedback stored in `Review` model  
- **Performance Metrics**: Average rating, total reviews, completion rate
- **Order Status History**: Full timeline from bid to completion

#### **🖼️ Portfolio Assets (Current)**
```json
// ServiceProviderProfile.verification_documents
[
  {
    "type": "portfolio_image",
    "url": "https://storage.com/portfolio1.jpg",
    "title": "E-commerce Website",
    "description": "Modern React-based online store"
  },
  {
    "type": "cv_document", 
    "url": "https://storage.com/resume.pdf",
    "title": "Professional CV"
  }
]
```

#### **📁 File Upload Capabilities**
- **Avatar Images**: Via accounts app (`/api/v1/profile/`)
- **Order Attachments**: Via orders app (`Order.attachments` JSON field)
- **Chat Files**: Via chat system (`ChatAttachment` model)
- **Verification Documents**: Via users app (`verification_documents` JSON field)

### **🏢 Client Company Portfolio System**

#### **📈 Company History**
- **Order History**: Track all posted jobs via `ClientProfile.total_orders`
- **Success Metrics**: Completed vs cancelled order ratios
- **Favorite Providers**: Build preferred contractor relationships
- **Budget Analytics**: Historical spending patterns

#### **🏆 Reputation Building**
- **Order Quality**: Detailed job postings with clear requirements
- **Payment History**: Reliable payment track record
- **Communication**: Professional interaction history
- **Provider Reviews**: Feedback received from service providers

### **📊 Automatic History Generation**

#### **For Service Providers**
```json
// Auto-generated from completed OrderAssignments
{
  "work_history": [
    {
      "order_id": 123,
      "title": "Mobile App Development", 
      "client": "Tech Startup Inc",
      "amount": 4500.00,
      "completion_date": "2024-01-15",
      "rating": 5,
      "review": "Excellent work, delivered on time"
    }
  ],
  "portfolio_stats": {
    "total_projects": 15,
    "average_rating": 4.8,
    "total_earnings": 67500.00,
    "repeat_clients": 3
  }
}
```

#### **For Clients**
```json
// Auto-generated from order history
{
  "hiring_history": [
    {
      "order_id": 123,
      "provider": "John's Dev Services",
      "project_type": "Mobile App",
      "budget": 5000.00,
      "status": "completed",
      "satisfaction": 5
    }
  ],
  "company_stats": {
    "total_projects_posted": 8,
    "average_budget": 3500.00,
    "preferred_categories": ["web_development", "mobile_apps"],
    "hiring_success_rate": 87.5
  }
}
```

### **🔄 Portfolio APIs Available**

#### **Service Provider Portfolio**
- `GET /api/v1/users/providers/` - List all providers with portfolio data
- `GET /api/v1/users/provider/` - Get specific provider's full portfolio
- `POST /api/v1/users/provider/update/` - Update portfolio information
- `GET /api/v1/orders/assignments/` - Get work history and projects
- `GET /api/v1/reviews/provider/{id}/` - Get all reviews and ratings

#### **Client Portfolio** 
- `GET /api/v1/users/clients/` - List all clients with history
- `GET /api/v1/users/client/` - Get specific client's hiring history  
- `POST /api/v1/users/client/update/` - Update client preferences
- `GET /api/v1/orders/` - Get all posted orders and their outcomes

#### **Advanced Profile Management**
- `GET /api/v1/users/profile/advanced/` - Get combined user account + job portal profile data
- `POST /api/v1/users/profile/advanced/` - Update both user account and job portal profile

#### **File Upload Endpoints**
- `POST /api/v1/profile/` - Upload avatar/profile images
- `POST /api/v1/chat/attachments/create/` - Upload portfolio files via chat
- `POST /api/v1/orders/create/` - Include attachments in order posting

### **📱 Advanced Profile API Example**

#### **GET Combined Profile Data**
```http
GET /api/v1/users/profile/advanced/
Authorization: Bearer {jwt_token}
```

**Response:**
```json
{
  "user_data": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "name": "John Doe",
    "description": "Full-stack developer",
    "photo_url": "https://storage.com/avatar.jpg",
    "groups": ["service_provider"],
    "permissions": ["add_order", "add_bid"]
  },
  "job_portal_profile": {
    "id": 1,
    "user_type": "service_provider",
    "bio": "Experienced React and Node.js developer",
    "phone_number": "+1234567890",
    "city": "New York",
    "country": "USA",
    "is_verified": true,
    "created_at": "2024-01-01T10:00:00Z"
  }
}
```

#### **POST Update Combined Profile**
```http
POST /api/v1/users/profile/advanced/
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "user_data": {
    "name": "John Smith",
    "description": "Senior Full-stack Developer",
    "photo_url": "https://new-avatar.jpg"
  },
  "job_portal_profile": {
    "bio": "Senior React and Node.js developer with 5+ years experience",
    "phone_number": "+1234567890",
    "city": "San Francisco",
    "state": "California"
  }
}
```

**Response:**
```json
{
  "message": "Profile updated successfully",
  "data": {
    "user_data": { /* updated user data */ },
    "job_portal_profile": { /* updated job portal profile */ }
  }
}
```

### **⚠️ Current Limitations & Opportunities**

#### **Missing Features for Enhanced Portfolio**
1. **Dedicated Portfolio Model**: No separate model for organized portfolio items
2. **CV Upload Endpoint**: No specific endpoint for resume/CV uploads  
3. **Portfolio Categories**: No categorization of work samples
4. **Project Showcase**: No detailed project case studies
5. **Skill Verification**: No system for validating claimed skills
6. **Media Management**: Limited image/video portfolio organization

#### **Recommended Enhancements**
```python
# Suggested Portfolio model structure
class PortfolioItem(models.Model):
    provider = models.ForeignKey(ServiceProviderProfile)
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(ServiceSubcategory)
    media_url = models.URLField()  # Image/video
    project_url = models.URLField(blank=True)  # Live demo
    technologies = models.JSONField(default=list)
    completion_date = models.DateField()
    client_testimonial = models.TextField(blank=True)
```

The backend provides a **solid foundation** for portfolio construction through existing models and APIs, with **significant opportunities** for enhancement to create more comprehensive portfolio management features.

---

## 🔐 Authentication Flow

### 1. Firebase Login Screen
**Endpoint:** `POST /api/v1/auth/firebase/`

```javascript
// Request Headers
Content-Type: application/json

// Request Body
{
  "id_token": "firebase_id_token_here"
}

// Response (200 OK)
{
  "access": "jwt_access_token_here",
  "refresh": "jwt_refresh_token_here",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

### 2. Check User Profile Status
**Endpoint:** `GET /api/v1/users/profile/`

```javascript
// Request Headers
Authorization: Bearer jwt_access_token_here
Content-Type: application/json

// Response - New User (no profile)
{
  "detail": "User profile not found"
}

// Response - Existing User
{
  "id": 1,
  "user_type": "client", // or "service_provider" or "both"
  "phone_number": "+1234567890",
  "date_of_birth": "1990-01-01",
  "gender": "male",
  "address": "123 Main St",
  "city": "New York",
  "country": "US",
  "bio": "Software developer",
  "avatar": "https://example.com/avatar.jpg",
  "is_verified": true,
  "verification_status": "approved"
}
```

---

## 👤 Multi-Step User Registration

### Step 1: Create Basic Profile
**Endpoint:** `POST /api/v1/users/profile/update/`

```javascript
// Request Headers
Authorization: Bearer jwt_access_token_here
Content-Type: application/json

// Request Body
{
  "user_type": "client", // or "service_provider" or "both"
  "phone_number": "+1234567890",
  "date_of_birth": "1990-01-01",
  "gender": "male",
  "address": "123 Main St",
  "city": "New York",
  "country": "US",
  "bio": "Looking for reliable services"
}

// Response (201 Created)
{
  "id": 1,
  "user_type": "client",
  "phone_number": "+1234567890",
  // ... other fields
  "is_verified": false,
  "verification_status": "pending"
}
```

### Step 2: Upload Avatar (Optional)
**Endpoint:** `POST /api/v1/profile/`

```javascript
// Request Headers
Authorization: Bearer jwt_access_token_here
Content-Type: multipart/form-data

// Request Body (Form Data)
photo: [image_file]

// Response (200 OK)
{
  "message": "Profile image uploaded successfully",
  "image_url": "https://example.com/media/user_photos/1/profile_abc123.jpg"
}
```

### Step 3A: Client Profile Setup
**Endpoint:** `POST /api/v1/users/client/update/`

```javascript
// Request Headers
Authorization: Bearer jwt_access_token_here
Content-Type: application/json

// Request Body
{
  "company_name": "Tech Corp",
  "company_website": "https://techcorp.com",
  "business_type": "technology",
  "company_size": "medium",
  "preferred_communication": "email"
}

// Response (201 Created)
{
  "id": 1,
  "company_name": "Tech Corp",
  "company_website": "https://techcorp.com",
  "business_type": "technology",
  "company_size": "medium",
  "preferred_communication": "email",
  "created_at": "2024-01-01T10:00:00Z"
}
```

### Step 3B: Service Provider Profile Setup
**Endpoint:** `POST /api/v1/users/provider/update/`

```javascript
// Request Headers
Authorization: Bearer jwt_access_token_here
Content-Type: application/json

// Request Body
{
  "business_name": "John's Services",
  "business_type": "individual",
  "years_of_experience": 5,
  "hourly_rate": 50.00,
  "availability": "full_time",
  "skills": ["web_development", "mobile_apps"],
  "certifications": ["AWS Certified"],
  "languages": ["English", "Spanish"],
  "service_radius": 25,
  "emergency_services": false
}

// Response (201 Created)
{
  "id": 1,
  "business_name": "John's Services",
  "business_type": "individual",
  "years_of_experience": 5,
  "hourly_rate": "50.00",
  "is_verified_provider": false,
  // ... other fields
}
```

### Step 4: Portfolio Upload (Service Providers)
**Note:** Portfolio uploads should be handled through the service provider profile update endpoint or as part of order attachments. The accounts app handles user avatar uploads, while portfolio images are typically managed through the provider profile or project submissions.

---

## 🏠 Homepage APIs

### 1. Dashboard Data
**Endpoint:** `GET /api/v1/analytics/dashboard/`

```javascript
// Request Headers
Authorization: Bearer jwt_access_token_here

// Response (200 OK)
{
  "total_orders": 25,
  "active_orders": 5,
  "total_earnings": 2500.00,
  "average_rating": 4.8,
  "recent_activity": [
    {
      "type": "order_completed",
      "message": "Order #123 completed",
      "timestamp": "2024-01-01T10:00:00Z"
    }
  ],
  "quick_stats": {
    "pending_bids": 3,
    "upcoming_deadlines": 2,
    "new_messages": 5
  }
}
```

### 2. Recent Orders/Jobs
**Endpoint:** `GET /api/v1/orders/?ordering=-created_at&limit=5`

```javascript
// Request Headers
Authorization: Bearer jwt_access_token_here

// Response (200 OK)
{
  "count": 50,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Website Development",
      "description": "Need a modern website",
      "status": "published",
      "budget_min": 1000.00,
      "budget_max": 2000.00,
      "deadline": "2024-02-01T00:00:00Z",
      "created_at": "2024-01-01T10:00:00Z",
      "client": {
        "company_name": "Tech Corp",
        "user": {
          "first_name": "John",
          "last_name": "Doe"
        }
      },
      "category": {
        "name": "Web Development"
      },
      "bids_count": 5
    }
  ]
}
```

---

## 🔍 Search & Browse Jobs

### 1. Search Jobs (Service Providers)
**Endpoint:** `GET /api/v1/search/orders/?q=website&category=1&budget_min=500`

```javascript
// Request Headers
Authorization: Bearer jwt_access_token_here

// Query Parameters
q: "website development"
category: 1
budget_min: 500
budget_max: 2000
location: "New York"
status: "published"
ordering: "-created_at"

// Response (200 OK)
{
  "count": 15,
  "next": "http://api/search/orders/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "E-commerce Website",
      "description": "Build a modern e-commerce site",
      "status": "published",
      "budget_min": 1500.00,
      "budget_max": 3000.00,
      "deadline": "2024-03-01T00:00:00Z",
      "created_at": "2024-01-01T10:00:00Z",
      "client": {
        "company_name": "Online Store Inc",
        "user": {
          "first_name": "Jane",
          "last_name": "Smith"
        }
      },
      "category": {
        "name": "Web Development"
      },
      "subcategory": {
        "name": "E-commerce"
      },
      "location": "New York, NY",
      "required_skills": ["React", "Node.js", "MongoDB"],
      "bids_count": 8,
      "average_bid": 2250.00
    }
  ]
}
```

### 2. Search Service Providers (Clients)
**Endpoint:** `GET /api/v1/search/providers/?q=web developer&skills=react`

```javascript
// Request Headers
Authorization: Bearer jwt_access_token_here

// Query Parameters
q: "web developer"
skills: "react,nodejs"
location: "New York"
hourly_rate_min: 30
hourly_rate_max: 100
rating_min: 4.0

// Response (200 OK)
{
  "count": 12,
  "results": [
    {
      "id": 1,
      "business_name": "Web Solutions Pro",
      "business_type": "individual",
      "years_of_experience": 5,
      "hourly_rate": "75.00",
      "average_rating": 4.8,
      "total_reviews": 24,
      "skills": ["React", "Node.js", "MongoDB"],
      "location": "New York, NY",
      "user": {
        "first_name": "Mike",
        "last_name": "Johnson",
        "avatar": "https://example.com/avatar.jpg"
      },
      "portfolio_samples": [
        {
          "image": "https://example.com/portfolio1.jpg",
          "title": "E-commerce Site"
        }
      ],
      "is_verified_provider": true,
      "is_online": true,
      "response_time": "within 2 hours"
    }
  ]
}
```

---

## 📋 Job Details & Applications

### 1. View Job Details
**Endpoint:** `GET /api/v1/orders/1/`

```javascript
// Request Headers
Authorization: Bearer jwt_access_token_here

// Response (200 OK)
{
  "id": 1,
  "title": "Mobile App Development",
  "description": "Need a React Native mobile app for food delivery",
  "status": "published",
  "budget_min": 3000.00,
  "budget_max": 5000.00,
  "deadline": "2024-04-01T00:00:00Z",
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z",
  "client": {
    "id": 1,
    "company_name": "FoodCorp",
    "user": {
      "first_name": "Alice",
      "last_name": "Brown",
      "avatar": "https://example.com/avatar.jpg"
    },
    "average_rating": 4.9,
    "total_orders": 15
  },
  "category": {
    "id": 2,
    "name": "Mobile Development"
  },
  "subcategory": {
    "id": 5,
    "name": "React Native"
  },
  "location": "Remote",
  "required_skills": ["React Native", "Redux", "Firebase"],
  "attachments": [
    {
      "id": 1,
      "file_url": "https://example.com/requirements.pdf",
      "file_name": "Project Requirements.pdf"
    }
  ],
  "bids": [
    {
      "id": 1,
      "amount": 4000.00,
      "estimated_hours": 160,
      "delivery_time": 30,
      "proposal": "I can deliver a high-quality app...",
      "status": "pending",
      "created_at": "2024-01-02T09:00:00Z",
      "provider": {
        "business_name": "Mobile Dev Pro",
        "user": {
          "first_name": "David",
          "last_name": "Wilson"
        },
        "average_rating": 4.7
      }
    }
  ],
  "bids_count": 12,
  "average_bid": 4200.00,
  "can_apply": true // false if already applied or not a service provider
}
```

### 2. Submit Job Application (Bid)
**Endpoint:** `POST /api/v1/orders/1/bids/`

```javascript
// Request Headers
Authorization: Bearer jwt_access_token_here
Content-Type: application/json

// Request Body
{
  "amount": 4500.00,
  "estimated_hours": 180,
  "delivery_time": 35,
  "proposal": "I have 6 years of experience in React Native development. I've built similar food delivery apps for 3 other clients. I can provide:\n\n1. Clean, maintainable code\n2. Regular progress updates\n3. Full testing coverage\n4. Post-launch support\n\nI'm available to start immediately and can deliver within 5 weeks.",
  "is_negotiable": true
}

// Response (201 Created)
{
  "id": 15,
  "amount": "4500.00",
  "estimated_hours": 180,
  "delivery_time": 35,
  "proposal": "I have 6 years of experience...",
  "status": "pending",
  "is_negotiable": true,
  "created_at": "2024-01-03T14:30:00Z",
  "provider": {
    "id": 2,
    "business_name": "Your Business Name",
    "user": {
      "first_name": "Your",
      "last_name": "Name"
    }
  }
}
```

---

## 📥 Applications Management

### 1. View My Applications (Service Provider)
**Endpoint:** `GET /api/v1/orders/bids/`

```javascript
// Request Headers
Authorization: Bearer jwt_access_token_here

// Response (200 OK)
{
  "count": 8,
  "results": [
    {
      "id": 15,
      "amount": "4500.00",
      "status": "pending",
      "created_at": "2024-01-03T14:30:00Z",
      "order": {
        "id": 1,
        "title": "Mobile App Development",
        "status": "bidding",
        "deadline": "2024-04-01T00:00:00Z",
        "client": {
          "company_name": "FoodCorp"
        }
      }
    },
    {
      "id": 12,
      "amount": "2800.00",
      "status": "accepted",
      "accepted_at": "2024-01-02T16:20:00Z",
      "order": {
        "id": 2,
        "title": "Website Redesign",
        "status": "assigned"
      }
    }
  ]
}
```

### 2. View Incoming Applications (Client)
**Endpoint:** `GET /api/v1/orders/bids/?order=1`

```javascript
// Request Headers
Authorization: Bearer jwt_access_token_here

// Response (200 OK)
{
  "count": 12,
  "results": [
    {
      "id": 15,
      "amount": "4500.00",
      "estimated_hours": 180,
      "delivery_time": 35,
      "proposal": "I have 6 years of experience...",
      "status": "pending",
      "is_negotiable": true,
      "created_at": "2024-01-03T14:30:00Z",
      "provider": {
        "id": 2,
        "business_name": "Mobile Dev Pro",
        "years_of_experience": 6,
        "hourly_rate": "25.00",
        "average_rating": 4.8,
        "total_reviews": 31,
        "user": {
          "first_name": "Sarah",
          "last_name": "Connor",
          "avatar": "https://example.com/avatar.jpg"
        },
        "skills": ["React Native", "Redux", "Firebase"],
        "portfolio_highlights": [
          {
            "title": "Food Delivery App",
            "image": "https://example.com/portfolio1.jpg"
          }
        ]
      }
    }
  ]
}
```

---

## ✅ Approval & Assignment Process

### 1. Accept Application (Client)
**Endpoint:** `POST /api/v1/orders/bids/15/accept/`

```javascript
// Request Headers
Authorization: Bearer jwt_access_token_here
Content-Type: application/json

// Request Body
{
  "message": "Great proposal! Looking forward to working with you."
}

// Response (200 OK)
{
  "message": "Bid accepted successfully",
  "bid": {
    "id": 15,
    "status": "accepted",
    "accepted_at": "2024-01-03T16:45:00Z",
    "amount": "4500.00",
    "provider": {
      "business_name": "Mobile Dev Pro",
      "user": {
        "first_name": "Sarah",
        "last_name": "Connor"
      }
    }
  },
  "assignment": {
    "id": 1,
    "order_id": 1,
    "provider_id": 2,
    "status": "assigned",
    "assigned_at": "2024-01-03T16:45:00Z",
    "expected_completion": "2024-02-07T16:45:00Z"
  }
}
```

### 2. Reject Application (Client)
**Endpoint:** `POST /api/v1/orders/bids/14/reject/`

```javascript
// Request Headers
Authorization: Bearer jwt_access_token_here
Content-Type: application/json

// Request Body
{
  "message": "Thank you for your proposal, but we've decided to go with another candidate."
}

// Response (200 OK)
{
  "message": "Bid rejected successfully",
  "bid": {
    "id": 14,
    "status": "rejected",
    "rejected_at": "2024-01-03T16:40:00Z"
  }
}
```

### 3. Withdraw Application (Service Provider)
**Endpoint:** `POST /api/v1/orders/bids/15/withdraw/`

```javascript
// Request Headers
Authorization: Bearer jwt_access_token_here
Content-Type: application/json

// Request Body
{
  "message": "I need to withdraw my application due to scheduling conflicts."
}

// Response (200 OK)
{
  "message": "Bid withdrawn successfully",
  "bid": {
    "id": 15,
    "status": "withdrawn",
    "withdrawn_at": "2024-01-03T15:30:00Z"
  }
}
```

---

## 📊 Active Projects & Orders

### 1. View My Active Projects
**Endpoint:** `GET /api/v1/orders/assignments/?status=assigned`

```javascript
// Request Headers
Authorization: Bearer jwt_access_token_here

// Response (200 OK)
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "status": "assigned",
      "assigned_at": "2024-01-03T16:45:00Z",
      "expected_completion": "2024-02-07T16:45:00Z",
      "progress_percentage": 25,
      "order": {
        "id": 1,
        "title": "Mobile App Development",
        "description": "React Native food delivery app",
        "status": "assigned",
        "final_price": "4500.00",
        "deadline": "2024-04-01T00:00:00Z",
        "client": {
          "company_name": "FoodCorp",
          "user": {
            "first_name": "Alice",
            "last_name": "Brown"
          }
        }
      },
      "accepted_bid": {
        "amount": "4500.00",
        "delivery_time": 35,
        "estimated_hours": 180
      },
      "milestones": [
        {
          "id": 1,
          "title": "UI/UX Design",
          "status": "completed",
          "completed_at": "2024-01-10T14:00:00Z"
        },
        {
          "id": 2,
          "title": "Backend API",
          "status": "in_progress",
          "expected_completion": "2024-01-20T14:00:00Z"
        }
      ]
    }
  ]
}
```

### 2. Update Project Progress
**Endpoint:** `PATCH /api/v1/orders/assignments/1/`

```javascript
// Request Headers
Authorization: Bearer jwt_access_token_here
Content-Type: application/json

// Request Body
{
  "progress_percentage": 45,
  "status_update": "Backend API development is 80% complete. Moving on to mobile app integration next week."
}

// Response (200 OK)
{
  "id": 1,
  "progress_percentage": 45,
  "status_update": "Backend API development is 80% complete...",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

## 💬 Communication & Chat

### 1. Get Chat Rooms
**Endpoint:** `GET /api/v1/chat/rooms/`

```javascript
// Request Headers
Authorization: Bearer jwt_access_token_here

// Response (200 OK)
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "name": "Mobile App Development - Project Chat",
      "room_type": "project",
      "order_id": 1,
      "participants": [
        {
          "id": 1,
          "first_name": "Alice",
          "last_name": "Brown",
          "avatar": "https://example.com/avatar1.jpg",
          "role": "client"
        },
        {
          "id": 2,
          "first_name": "Sarah",
          "last_name": "Connor",
          "avatar": "https://example.com/avatar2.jpg",
          "role": "service_provider"
        }
      ],
      "last_message": {
        "id": 45,
        "message": "The first milestone is ready for review",
        "timestamp": "2024-01-15T14:30:00Z",
        "sender": {
          "first_name": "Sarah",
          "last_name": "Connor"
        }
      },
      "unread_count": 2,
      "created_at": "2024-01-03T16:45:00Z"
    }
  ]
}
```

### 2. Get Chat Messages  
**Endpoint:** `GET /api/v1/chat/messages/?limit=50&room=1`

```javascript
// Request Headers
Authorization: Bearer jwt_access_token_here

// Response (200 OK)
{
  "count": 23,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 45,
      "message": "The first milestone is ready for review",
      "timestamp": "2024-01-15T14:30:00Z",
      "sender": {
        "id": 2,
        "first_name": "Sarah",
        "last_name": "Connor",
        "avatar": "https://example.com/avatar2.jpg"
      },
      "message_type": "text",
      "attachments": [],
      "is_read": false
    },
    {
      "id": 44,
      "message": "Great! Please share the design mockups when ready.",
      "timestamp": "2024-01-14T09:15:00Z",
      "sender": {
        "id": 1,
        "first_name": "Alice",
        "last_name": "Brown",
        "avatar": "https://example.com/avatar1.jpg"
      },
      "message_type": "text",
      "is_read": true
    }
  ]
}
```

### 3. Send Message
**Endpoint:** `POST /api/v1/chat/messages/create/`

```javascript
// Request Headers
Authorization: Bearer jwt_access_token_here
Content-Type: application/json

// Request Body
{
  "message": "I've uploaded the latest version. Please check and let me know your feedback.",
  "message_type": "text"
}

// Response (201 Created)
{
  "id": 46,
  "message": "I've uploaded the latest version. Please check and let me know your feedback.",
  "timestamp": "2024-01-16T11:20:00Z",
  "sender": {
    "id": 2,
    "first_name": "Sarah",
    "last_name": "Connor"
  },
  "message_type": "text",
  "is_read": false
}
```

---

## 🔔 Notifications

### 1. Get User Notifications
**Endpoint:** `GET /api/v1/notifications/`

```javascript
// Request Headers
Authorization: Bearer jwt_access_token_here

// Response (200 OK)
{
  "count": 15,
  "results": [
    {
      "id": 1,
      "title": "New Bid Received",
      "message": "You received a new bid for your project 'Mobile App Development'",
      "notification_type": "bid_received",
      "is_read": false,
      "created_at": "2024-01-16T10:30:00Z",
      "related_object_id": 1,
      "related_object_type": "bid"
    }
  ]
}
```

### 2. Mark Notification as Read
**Endpoint:** `PATCH /api/v1/notifications/1/`

```javascript
// Request Headers
Authorization: Bearer jwt_access_token_here
Content-Type: application/json

// Request Body
{
  "is_read": true
}

// Response (200 OK)
{
  "id": 1,
  "is_read": true,
  "updated_at": "2024-01-16T11:00:00Z"
}
```

### 3. Get Notification Settings
**Endpoint:** `GET /api/v1/notifications/settings/`

```javascript
// Request Headers
Authorization: Bearer jwt_access_token_here

// Response (200 OK)
{
  "email_notifications": true,
  "push_notifications": true,
  "sms_notifications": false,
  "notification_types": {
    "bid_received": true,
    "bid_accepted": true,
    "message_received": true,
    "order_completed": true
  }
}
```

---

## ⭐ Reviews & Ratings

### 1. List Reviews
**Endpoint:** `GET /api/v1/reviews/`

```javascript
// Request Headers
Authorization: Bearer jwt_access_token_here

// Response (200 OK)
{
  "count": 25,
  "results": [
    {
      "id": 1,
      "rating": 5,
      "comment": "Excellent work and great communication!",
      "order": {
        "id": 1,
        "title": "Mobile App Development"
      },
      "reviewer": {
        "first_name": "John",
        "last_name": "Doe"
      },
      "provider": {
        "business_name": "Tech Solutions Pro"
      },
      "created_at": "2024-01-15T14:30:00Z"
    }
  ]
}
```

### 2. Create Review
**Endpoint:** `POST /api/v1/reviews/`

```javascript
// Request Headers
Authorization: Bearer jwt_access_token_here
Content-Type: application/json

// Request Body
{
  "order": 1,
  "provider": 2,
  "rating": 5,
  "comment": "Outstanding work! Delivered on time and exceeded expectations.",
  "would_recommend": true
}

// Response (201 Created)
{
  "id": 26,
  "rating": 5,
  "comment": "Outstanding work! Delivered on time and exceeded expectations.",
  "would_recommend": true,
  "created_at": "2024-01-16T15:20:00Z"
}
```

### 3. Get Provider Reviews
**Endpoint:** `GET /api/v1/reviews/provider/2/`

```javascript
// Request Headers
Authorization: Bearer jwt_access_token_here

// Response (200 OK)
{
  "provider_id": 2,
  "average_rating": 4.8,
  "total_reviews": 31,
  "rating_distribution": {
    "5": 25,
    "4": 4,
    "3": 2,
    "2": 0,
    "1": 0
  },
  "recent_reviews": [
    {
      "id": 25,
      "rating": 5,
      "comment": "Great developer!",
      "created_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

---

## 💳 Payments & Billing

### 1. List Payment Methods
**Endpoint:** `GET /api/v1/payments/methods/`

```javascript
// Request Headers
Authorization: Bearer jwt_access_token_here

// Response (200 OK)
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "type": "card",
      "last_four": "4242",
      "brand": "visa",
      "is_default": true,
      "expires_at": "2025-12-31",
      "created_at": "2024-01-01T10:00:00Z"
    }
  ]
}
```

### 2. Add Payment Method
**Endpoint:** `POST /api/v1/payments/methods/create/`

```javascript
// Request Headers
Authorization: Bearer jwt_access_token_here
Content-Type: application/json

// Request Body
{
  "type": "card",
  "stripe_payment_method_id": "pm_1234567890",
  "is_default": false
}

// Response (201 Created)
{
  "id": 2,
  "type": "card",
  "last_four": "1234",
  "brand": "mastercard",
  "is_default": false,
  "message": "Payment method added successfully"
}
```

### 3. Create Payment
**Endpoint:** `POST /api/v1/payments/create/`

```javascript
// Request Headers
Authorization: Bearer jwt_access_token_here
Content-Type: application/json

// Request Body
{
  "order": 1,
  "amount": 4500.00,
  "payment_method": 1,
  "description": "Payment for Mobile App Development"
}

// Response (201 Created)
{
  "id": 1,
  "amount": "4500.00",
  "status": "succeeded",
  "stripe_payment_intent_id": "pi_1234567890",
  "created_at": "2024-01-16T16:00:00Z"
}
```

---

## 🚨 Disputes & Support

### 1. List Order Disputes
**Endpoint:** `GET /api/v1/orders/disputes/`

```javascript
// Request Headers
Authorization: Bearer jwt_access_token_here

// Response (200 OK)
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "order": {
        "id": 1,
        "title": "Mobile App Development"
      },
      "dispute_type": "quality_issue",
      "status": "open",
      "description": "The delivered app doesn't match the requirements",
      "created_at": "2024-01-15T09:00:00Z"
    }
  ]
}
```

### 2. Create Dispute
**Endpoint:** `POST /api/v1/orders/1/disputes/`

```javascript
// Request Headers
Authorization: Bearer jwt_access_token_here
Content-Type: application/json

// Request Body
{
  "dispute_type": "quality_issue",
  "description": "The delivered product doesn't meet the agreed specifications. Several features are missing and the code quality is poor.",
  "evidence_files": ["https://example.com/evidence1.pdf"]
}

// Response (201 Created)
{
  "id": 2,
  "dispute_type": "quality_issue",
  "status": "open",
  "description": "The delivered product doesn't meet the agreed specifications...",
  "created_at": "2024-01-16T11:30:00Z"
}
```

---

## 📚 Core Data

### 1. Get Service Categories
**Endpoint:** `GET /api/v1/core/service-categories/`

```javascript
// Request Headers
Authorization: Bearer jwt_access_token_here

// Response (200 OK)
{
  "count": 8,
  "results": [
    {
      "id": 1,
      "name": "Web Development",
      "description": "Build websites and web applications",
      "icon": "web-icon.svg",
      "is_active": true
    }
  ]
}
```

### 2. Get Service Subcategories
**Endpoint:** `GET /api/v1/core/service-subcategories/?category=1`

```javascript
// Request Headers
Authorization: Bearer jwt_access_token_here

// Response (200 OK)
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "name": "Frontend Development",
      "category": 1,
      "description": "User interface development"
    }
  ]
}
```

### 3. Get Languages
**Endpoint:** `GET /api/v1/core/languages/`

```javascript
// Request Headers
Authorization: Bearer jwt_access_token_here

// Response (200 OK)
{
  "count": 20,
  "results": [
    {
      "id": 1,
      "name": "English",
      "code": "en",
      "is_default": true
    }
  ]
}
```

---

## 📱 Mobile App Screens & API Mapping

### Login & Registration Flow
1. **Login Screen** → `POST /api/v1/auth/firebase/`
2. **Profile Check** → `GET /api/v1/users/profile/`
3. **Registration Screen** → `POST /api/v1/users/profile/update/`
4. **Avatar Upload** → `POST /api/v1/profile/` (with photo)
5. **Role Selection** → `POST /api/v1/users/client/update/` or `POST /api/v1/users/provider/update/`

### Main App Screens

#### For Clients:
1. **Dashboard** → `GET /api/v1/analytics/dashboard/`
2. **Search Providers** → `GET /api/v1/search/providers/`
3. **My Orders** → `GET /api/v1/orders/`
4. **Order Details** → `GET /api/v1/orders/{id}/`
5. **Incoming Bids** → `GET /api/v1/orders/bids/?order={id}`
6. **Accept/Reject Bids** → `POST /api/v1/orders/bids/{id}/accept/` or `POST /api/v1/orders/bids/{id}/reject/`
7. **Active Projects** → `GET /api/v1/orders/assignments/`
8. **Chat** → `GET /api/v1/chat/rooms/`

#### For Service Providers:
1. **Dashboard** → `GET /api/v1/analytics/dashboard/`
2. **Browse Jobs** → `GET /api/v1/search/orders/`
3. **Job Details** → `GET /api/v1/orders/{id}/`
4. **Apply for Job** → `POST /api/v1/orders/{id}/bids/`
5. **My Applications** → `GET /api/v1/orders/bids/`
6. **Withdraw Application** → `POST /api/v1/orders/bids/{id}/withdraw/`
7. **Active Projects** → `GET /api/v1/orders/assignments/`
8. **Update Progress** → `PATCH /api/v1/orders/assignments/{id}/`
9. **Chat** → `GET /api/v1/chat/rooms/`

---

## 🚀 Implementation Tips

### Error Handling
```javascript
// Standard Error Response Format
{
  "error": "Validation failed",
  "details": {
    "amount": ["This field is required"],
    "proposal": ["Proposal must be at least 50 characters"]
  },
  "status_code": 400
}
```

### Pagination
```javascript
// All list endpoints support pagination
GET /orders/?page=2&page_size=20

// Response includes pagination info
{
  "count": 150,
  "next": "http://api/orders/?page=3",
  "previous": "http://api/orders/?page=1",
  "results": [...]
}
```

### Real-time Updates
- Use WebSocket connections for chat: `ws://your-domain.com/ws/chat/{room_id}/`
- Implement push notifications for bid updates, messages, and order status changes
- Poll dashboard endpoint every 30 seconds for activity updates

### Mobile-Specific Considerations
- Cache user profile data locally
- Implement offline mode for viewing saved jobs/applications
- Use image compression for avatar/portfolio uploads
- Implement pull-to-refresh for all list screens
- Add infinite scroll for search results

---

## 📋 Complete User Journey Checklist

### New User Registration ✅
- [ ] Firebase authentication
- [ ] Basic profile creation
- [ ] Avatar upload
- [ ] Role-specific profile setup
- [ ] Verification process

### Service Provider Journey ✅
- [ ] Browse available jobs
- [ ] Filter and search jobs
- [ ] View job details and requirements
- [ ] Submit applications with proposals
- [ ] Track application status
- [ ] Manage active projects
- [ ] Communicate with clients
- [ ] Update project progress

### Client Journey ✅
- [ ] Create job postings
- [ ] Search for service providers
- [ ] Review incoming applications
- [ ] Accept/reject applications
- [ ] Manage active orders
- [ ] Communicate with providers
- [ ] Track project progress
- [ ] Complete orders and leave reviews

This guide provides everything needed to build a complete mobile job portal app with proper API integration! 🎉
