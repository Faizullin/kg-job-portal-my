# Documentation

This folder contains comprehensive documentation for the kg-job-portal-my project, consolidated into two essential files.

## 📚 **Available Documentation**

### [Complete Database Schema](./DATABASE_COMPLETE.md)
Comprehensive database schema documentation including all models, relationships, soft delete functionality, and database design principles.

**Topics covered:**
- Complete app structure and architecture
- Detailed model documentation with soft delete information
- Key relationships and data flows
- Soft delete system implementation and usage
- Database indexes and performance optimization
- Security, compliance, and scalability considerations
- Migration strategy and best practices

### [Complete API Routing Schema](./API_ROUTING_SCHEMA.md)
Complete API routing information for all endpoints, organized by app and functionality.

**Topics covered:**
- All API endpoints with methods and authentication requirements
- Request/response formats and examples
- Authentication and authorization details
- Rate limiting and performance metrics
- WebSocket endpoints for real-time communication
- Testing and development tools
- API versioning strategy

## 🏗️ **Project Structure**

```
kg-job-portal-my/
├── docs/                          # Documentation files
│   ├── README.md                  # This index file
│   ├── DATABASE_COMPLETE.md      # Complete database schema + soft delete
│   └── API_ROUTING_SCHEMA.md     # Complete API routing schema
├── backend/                       # Django backend application
│   ├── accounts/                  # User management
│   ├── api_users/                 # API user functionality
│   ├── job_portal/                # Job portal models and views
│   │   └── apps/                  # Modular app structure
│   │       ├── core/              # Core services & categories
│   │       ├── users/             # User profiles & verification
│   │       ├── orders/            # Order management & bidding
│   │       ├── chat/              # Communication system
│   │       ├── payments/          # Payment processing
│   │       ├── notifications/     # Notification system
│   │       └── analytics/         # Business intelligence
│   ├── lms/                       # Learning management system
│   └── utils/                     # Utility modules and abstract models
├── nginx/                         # Nginx configuration
└── README.md                      # Project overview (root level)
```

## 🚀 **Getting Started**

1. **Database Understanding**: Start with [DATABASE_COMPLETE.md](./DATABASE_COMPLETE.md) to understand the data model and soft delete system
2. **API Integration**: Use [API_ROUTING_SCHEMA.md](./API_ROUTING_SCHEMA.md) for all API endpoint information
3. **Backend Setup**: Follow the Django setup instructions in the backend folder
4. **API Documentation**: Use the OpenAPI schema generation command: `python3 manage.py generateschema --file openapi-schema.yml`

## 🔄 **Soft Delete System**

The application implements a comprehensive soft delete system that:
- Automatically filters soft-deleted objects in queries
- Provides cascading soft delete for related objects
- Maintains data integrity and history
- Is fully documented in the database schema file

## 📱 **Key Features**

- **Modular Architecture**: Clean separation of concerns across Django apps
- **Soft Delete**: Comprehensive soft delete system for data preservation
- **Real-time Communication**: WebSocket-based chat system
- **Payment Integration**: Stripe payment processing with webhooks
- **Multi-language Support**: Internationalization ready
- **Role-based Access**: Secure authentication and authorization
- **Analytics**: Business intelligence and reporting capabilities

## 🔧 **Development Tools**

- **Django Debug Toolbar**: Available in development mode
- **API Testing**: Comprehensive endpoint documentation
- **Database Migrations**: Up-to-date migration files
- **Docker Support**: Development and production containers

## 📖 **Documentation Standards**

- **Comprehensive Coverage**: All aspects documented in detail
- **Code Examples**: Practical usage examples provided
- **Best Practices**: Implementation guidelines included
- **Troubleshooting**: Common issues and solutions documented

---

This consolidated documentation provides everything needed to understand and work with the kg-job-portal-my application, focusing on the two most important aspects: database structure (including soft delete) and API routing schema.
