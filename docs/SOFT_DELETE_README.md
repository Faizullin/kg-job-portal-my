# Soft Delete System Documentation

This document explains the improved soft delete system implemented in the Django backend that handles soft delete logic within models rather than views.

## Overview

The new soft delete system provides:
- **Automatic filtering** of soft-deleted objects in queries
- **Custom managers** that handle soft delete operations
- **Cascading soft delete** for related objects
- **Clean separation** of concerns (models handle deletion, views handle presentation)

## Architecture

### 1. Abstract Models

#### `AbstractSoftDeleteModel`
Basic soft delete functionality with fields:
- `is_deleted`: Boolean flag indicating deletion status
- `deleted_at`: Timestamp when object was soft deleted
- `restored_at`: Timestamp when object was restored

#### `AbstractCascadingSoftDeleteModel`
Advanced soft delete with automatic cascading to related objects.

### 2. Custom Managers

#### `SoftDeleteManager`
- Automatically filters out soft-deleted objects in queries
- Provides methods for working with deleted objects
- Handles bulk operations

#### `CascadingSoftDeleteManager`
- Extends `SoftDeleteManager`
- Automatically soft deletes related objects
- Handles cascading restore operations

#### `UserManager`
- Specialized manager for UserModel
- Combines soft delete with Django's user creation methods
- Provides user-specific query methods

## Usage Examples

### Basic Soft Delete

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

### Cascading Soft Delete

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

### User Model with Soft Delete

```python
from accounts.models import UserModel

# Create user (automatically uses SoftDeleteManager)
user = UserModel.objects.create_user(
    email='user@example.com',
    password='password123',
    name='John Doe'
)

# Soft delete user
user.delete()

# User is no longer visible in normal queries
assert UserModel.objects.count() == 0

# But still exists in database
deleted_user = UserModel.objects.all_with_deleted().get(email='user@example.com')
assert deleted_user.is_deleted == True

# Restore user
deleted_user.restore()
assert UserModel.objects.count() == 1
```

## Manager Methods

### SoftDeleteManager Methods

```python
# Basic queries
Model.objects.all()                    # Only active objects
Model.objects.all_with_deleted()       # All objects including deleted
Model.objects.deleted_only()           # Only deleted objects

# Counts
Model.objects.get_active_count()       # Count of active objects
Model.objects.get_deleted_count()      # Count of deleted objects

# Bulk operations
Model.objects.bulk_soft_delete([1, 2, 3])     # Soft delete multiple objects
Model.objects.bulk_restore([1, 2, 3])         # Restore multiple objects

# Individual operations
Model.objects.restore(5)               # Restore object with pk=5
```

### UserManager Methods

```python
# User creation
UserModel.objects.create_user(email='user@example.com', password='password')
UserModel.objects.create_superuser(email='admin@example.com', password='password')

# User queries
UserModel.objects.filter_by_user_type('paid')     # Filter by user type
UserModel.objects.get_blocked_users()             # Get blocked users
UserModel.objects.get_active_users()              # Get active users
```

## Migration from Old System

### Before (View-based soft delete)
```python
class AbstractSoftDeleteViewSet(AbstractBaseApiViewSet):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()  # This would call soft delete
        return Response(status=status.HTTP_204_NO_CONTENT)
```

### After (Model-based soft delete)
```python
class MyModel(AbstractSoftDeleteModel):
    # Soft delete is handled automatically by the manager
    pass

class MyViewSet(AbstractBaseApiViewSet):
    # No need to override get_queryset or destroy
    # Soft delete is handled automatically
    pass
```

## Best Practices

### 1. Choose the Right Abstract Model
- Use `AbstractSoftDeleteModel` for simple soft delete needs
- Use `AbstractCascadingSoftDeleteModel` when you need cascading behavior

### 2. Define Cascade Fields Carefully
```python
def get_cascade_fields(self):
    """Only include fields that should be soft deleted together."""
    return ['jobs', 'employees']  # Don't include fields that should remain
```

### 3. Handle Related Objects Appropriately
```python
def delete(self, using=None, keep_parents=False):
    """Custom delete logic if needed."""
    # Do any cleanup before soft delete
    self.cleanup_before_delete()
    
    # Call the standard soft delete
    super().delete(using, keep_parents)
```

### 4. Use Manager Methods for Bulk Operations
```python
# Good - uses manager method
UserModel.objects.bulk_soft_delete(user_ids)

# Avoid - individual calls in loop
for user_id in user_ids:
    user = UserModel.objects.get(pk=user_id)
    user.delete()
```

## Testing

Run the demonstration command to see the system in action:

```bash
python manage.py demo_soft_delete
```

This will create test data and demonstrate:
- Basic soft delete functionality
- Manager methods
- Cascading soft delete
- Restore functionality

## Benefits

1. **Automatic**: No need to remember to filter out deleted objects
2. **Consistent**: All models behave the same way
3. **Efficient**: Bulk operations and optimized queries
4. **Maintainable**: Logic is centralized in models, not scattered in views
5. **Flexible**: Easy to override behavior when needed
6. **Cascading**: Automatic handling of related object deletion

## Troubleshooting

### Common Issues

1. **Objects still visible after delete**
   - Check if the model inherits from the correct abstract class
   - Verify the manager is properly set

2. **Cascading not working**
   - Ensure `get_cascade_fields()` returns the correct field names
   - Check that related objects also inherit from soft delete models

3. **Performance issues**
   - Use `bulk_soft_delete()` and `bulk_restore()` for multiple objects
   - Consider adding database indexes on `is_deleted` field

### Debug Queries

```python
# See what queries are being executed
from django.db import connection
from django.db import reset_queries
import time

reset_queries()
start = time.time()

# Your query here
users = UserModel.objects.all()

end = time.time()
print(f"Query took {end - start} seconds")
print(f"Number of queries: {len(connection.queries)}")
for query in connection.queries:
    print(query['sql'])
```
