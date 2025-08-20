from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from utils.abstract_models import AbstractMetaModel


def restore_queryset(modeladmin, request, queryset):
    """Restore soft-deleted objects."""
    if isinstance(queryset, QuerySet):
        for obj in queryset:
            obj.restore(strict=False)
    else:
        queryset.restore()


def soft_delete_queryset(modeladmin, request, queryset):
    """Soft delete objects."""
    if isinstance(queryset, QuerySet):
        for obj in queryset:
            obj.delete()
    else:
        queryset.delete()


def hard_delete_queryset(modeladmin, request, queryset):
    """Hard delete objects permanently."""
    if isinstance(queryset, QuerySet):
        for obj in queryset:
            obj.hard_delete()
    else:
        queryset.hard_delete()


class SoftDeleteFilter(SimpleListFilter):
    """Filter for soft-deleted objects."""
    title = 'is deleted'
    parameter_name = 'is_deleted'

    def lookups(self, request, model_admin):
        return (
            ('true', 'Deleted Softly'),
            ('false', 'Not Deleted'),
            ('all', 'All'),
        )

    def queryset(self, request, queryset):
        value = {
            'true': False,
            'false': True,
            'all': 'ALL',
        }[self.value() or 'false']
        if value == 'ALL':
            return queryset

        return queryset.filter(deleted_at__isnull=value)


class AbstractBaseAdmin(admin.ModelAdmin):
    """Base admin class with common functionality for all models."""
    
    has_default_timestamps = False
    has_soft_delete = False
    has_html_meta = False
    lookup_important_dated_key = "important_dates"
    lookup_general_key = "general"
    lookup_html_meta_key = "html_meta"
    lookup_key_list = [lookup_general_key]

    def __init__(self, model, admin_site):
        super(AbstractBaseAdmin, self).__init__(model, admin_site)
        self.has_default_timestamps = self.check_has_default_timestamps()
        self.has_soft_delete = self.check_has_soft_delete()
        self.has_html_meta = self.check_has_html_meta()
        if self.has_default_timestamps:
            self.readonly_fields += ("created_at", "updated_at",)
        if self.has_soft_delete:
            self.readonly_fields += ("deleted_at", "restored_at",)

    def get_ordering(self, request):
        if self.has_default_timestamps and self.ordering is None:
            return ['-updated_at']
        return self.ordering

    def get_readonly_fields(self, request, obj=None):
        default = super().get_readonly_fields(request, obj)
        if self.has_default_timestamps:
            default += ('created_at', 'updated_at',)
        return default

    def check_has_default_timestamps(self):
        field_name_list = [field.name for field in self.model._meta.get_fields()]
        return 'created_at' in field_name_list and 'updated_at' in field_name_list

    def check_has_soft_delete(self):
        field_name_list = [field.name for field in self.model._meta.get_fields()]
        return 'deleted_at' in field_name_list and 'restored_at' in field_name_list

    def check_has_html_meta(self):
        return issubclass(self.model, AbstractMetaModel)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['has_soft_delete'] = self.has_soft_delete
        extra_context['has_default_timestamps'] = self.has_default_timestamps
        return super().changelist_view(request, extra_context=extra_context)

    def get_list_filter(self, request):
        default_list = super().get_list_filter(request)
        if self.has_soft_delete:
            default_list += (SoftDeleteFilter,)
        return default_list

    def get_object(self, request, object_id, from_field=None):
        queryset = self.get_queryset(request, show_all=True)
        model = queryset.model
        field = (
            model._meta.pk if from_field is None else model._meta.get_field(from_field)
        )
        try:
            object_id = field.to_python(object_id)
            return queryset.get(**{field.name: object_id})
        except (model.DoesNotExist, ValidationError, ValueError):
            return None

    def get_queryset(self, request, show_all=False):
        if show_all and self.has_soft_delete:
            qs = self.model.global_objects.all()
        else:
            qs = self.model.objects.all()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def get_actions(self, request):
        default = super().get_actions(request)
        if self.has_soft_delete:
            default.update({
                "restore": (restore_queryset, "restore", "Restore selected items"),
                "hard_delete": (hard_delete_queryset, "hard_delete", "Hard delete selected items"),
            })
        return default

    def delete_queryset(self, request, queryset):
        soft_delete_queryset(_, request, queryset)

    def delete_model(self, request, obj):
        soft_delete_queryset(_, request, obj)

    def get_fieldsets(self, request, obj=None):
        fieldsets_dict = self.get_fieldsets_dict(request, obj)
        fieldsets = []
        for key in self.lookup_key_list:
            item = fieldsets_dict[key]
            fieldsets.append((item['label'], item['value']))
        return fieldsets

    def get_fieldsets_dict(self, request, obj=None):
        default_fieldsets = super().get_fieldsets(request, obj)
        new_fieldsets_dict = dict()
        if not self.lookup_general_key in new_fieldsets_dict:
            new_fieldsets_dict[self.lookup_general_key] = {
                "label": default_fieldsets[0][0],
                "value": default_fieldsets[0][1],
            }
        if not self.lookup_important_dated_key in new_fieldsets_dict:
            new_fieldsets_dict[self.lookup_important_dated_key] = {
                "label": _("Important dates"),
                "value": {
                    "fields": [],
                },
            }
        if self.has_html_meta and (self.lookup_html_meta_key not in new_fieldsets_dict):
            new_fieldsets_dict[self.lookup_html_meta_key] = {
                "label": _("Meta"),
                "value": {
                    "fields": [],
                },
            }

        if self.has_default_timestamps:
            if 'created_at' in new_fieldsets_dict[self.lookup_general_key]["value"]["fields"]:
                new_fieldsets_dict[self.lookup_general_key]["value"]["fields"].remove('created_at')
            if 'updated_at' in new_fieldsets_dict[self.lookup_general_key]["value"]["fields"]:
                new_fieldsets_dict[self.lookup_general_key]["value"]["fields"].remove('updated_at')
            new_fieldsets_dict[self.lookup_important_dated_key]["value"]["fields"].append('created_at')
            new_fieldsets_dict[self.lookup_important_dated_key]["value"]["fields"].append('updated_at')
        if self.has_soft_delete:
            if 'deleted_at' in new_fieldsets_dict[self.lookup_general_key]["value"]["fields"]:
                new_fieldsets_dict[self.lookup_general_key]["value"]["fields"].remove('deleted_at')
            if 'restored_at' in new_fieldsets_dict[self.lookup_general_key]["value"]["fields"]:
                new_fieldsets_dict[self.lookup_general_key]["value"]["fields"].remove('restored_at')
            new_fieldsets_dict[self.lookup_important_dated_key]["value"]["fields"].append('deleted_at')
            new_fieldsets_dict[self.lookup_important_dated_key]["value"]["fields"].append('restored_at')

        if self.has_html_meta:
            for key in ['use_ssr', 'render_url', 'meta_title', 'meta_keywords', 'meta_description']:
                new_fieldsets_dict[self.lookup_html_meta_key]["value"]["fields"].append(key)
                if key in new_fieldsets_dict[self.lookup_general_key]["value"]["fields"]:
                    new_fieldsets_dict[self.lookup_general_key]["value"]["fields"].remove(key)

        if obj is None:
            if self.has_default_timestamps or self.has_soft_delete:
                del new_fieldsets_dict[self.lookup_important_dated_key]
            if self.has_html_meta:
                del new_fieldsets_dict[self.lookup_html_meta_key]
        else:
            self.lookup_key_list = [self.lookup_general_key]
            if self.has_html_meta:
                self.lookup_key_list.append(self.lookup_html_meta_key)
            if self.has_default_timestamps or self.has_soft_delete:
                self.lookup_key_list.append(self.lookup_important_dated_key)

        return new_fieldsets_dict


class AbstractReadOnlyAdmin(AbstractBaseAdmin):
    """Admin class for read-only models."""
    
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class AbstractAuditAdmin(AbstractBaseAdmin):
    """Admin class for models that need audit trail functionality."""
    
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new object
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
