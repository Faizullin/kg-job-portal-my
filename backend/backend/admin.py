from django.contrib import admin


class UniversalAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        list_display = [
            field.name for field in self.model._meta.fields]
        return list_display
