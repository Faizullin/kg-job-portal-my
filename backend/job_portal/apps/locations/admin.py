from django.contrib import admin
from .models import Country, City


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_deleted', 'created_at']
    list_filter = ['is_deleted', 'created_at']
    search_fields = ['name', 'code']
    ordering = ['name']
    list_editable = ['is_deleted']
    
    fieldsets = (
        ('Country Information', {
            'fields': ('name', 'code')
        }),
        ('Status', {
            'fields': ('is_deleted',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'country', 'is_deleted', 'created_at']
    list_filter = ['country', 'is_deleted', 'created_at']
    search_fields = ['name', 'code', 'country__name']
    ordering = ['country', 'name']
    list_editable = ['is_deleted']
    raw_id_fields = ['country']
    
    fieldsets = (
        ('City Information', {
            'fields': ('name', 'code', 'country')
        }),
        ('Status', {
            'fields': ('is_deleted',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('country')
