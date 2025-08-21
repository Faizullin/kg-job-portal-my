# Documentation

This folder contains comprehensive documentation for the kg-job-portal-my project.

## Available Documentation

### [Soft Delete System](./SOFT_DELETE_README.md)
Comprehensive guide to the improved soft delete system implemented in Django backend that handles soft delete logic within models rather than views.

**Topics covered:**
- Architecture overview
- Custom managers implementation
- Usage examples
- Best practices
- Migration guide
- Troubleshooting

### [Database Schema](./DATABASE_SCHEMA.md)
Complete database schema documentation for the job portal application, designed based on user flow analysis and business requirements.

**Topics covered:**
- App structure and architecture
- Detailed model documentation
- Key relationships and flows
- Database indexes and performance
- Scalability considerations
- Security and compliance
- Migration strategy

## Project Structure

```
kg-job-portal-my/
├── docs/                          # Documentation files
│   ├── README.md                  # This index file
│   ├── SOFT_DELETE_README.md     # Soft delete system documentation
│   └── DATABASE_SCHEMA.md        # Database schema documentation
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

## Getting Started

1. **Backend Setup**: Follow the Django setup instructions in the backend folder
2. **Soft Delete System**: Read the [Soft Delete System documentation](./SOFT_DELETE_README.md) to understand the improved deletion logic
3. **Database Schema**: Review the [Database Schema documentation](./DATABASE_SCHEMA.md) to understand the data model
4. **API Documentation**: Use the OpenAPI schema generation command: `python3 manage.py generateschema --file openapi-schema.yml`

## Contributing

When adding new documentation:
1. Create markdown files in this `docs/` folder
2. Update this README.md to include links to new documentation
3. Follow the existing documentation style and format

## Documentation Standards

- Use clear, descriptive titles
- Include code examples where appropriate
- Provide step-by-step instructions for complex processes
- Include troubleshooting sections for common issues
- Keep documentation up-to-date with code changes
