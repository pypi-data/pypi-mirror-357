from django.contrib import admin
from NEMO.mixins import ModelAdminRedirectMixin
from django.utils.safestring import mark_safe

from NEMO_floor_plans.models import FloorPlan, FloorPlanIcon, FloorPlanNode


@admin.register(FloorPlan)
class FloorPlanAdmin(ModelAdminRedirectMixin, admin.ModelAdmin):
    list_display = ["name", "is_default", "image_thumbnail"]

    @admin.display(ordering="image", description="Image")
    def image_thumbnail(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" height="250px" />')
        return "No image"


@admin.register(FloorPlanNode)
class FloorPlanNodeAdmin(ModelAdminRedirectMixin, admin.ModelAdmin):
    list_display = ["floor_plan", "type", "icon_thumbnail", "sensor", "portal_to"]
    list_filter = ["type", ("icon", admin.RelatedOnlyFieldListFilter)]

    @admin.display(ordering="icon", description="Icon")
    def icon_thumbnail(self, obj: FloorPlanNode):
        if obj.icon:
            return mark_safe(f'<img src="{obj.icon.image.url}" height="50px" />')
        return "No icon"


@admin.register(FloorPlanIcon)
class FloorPlanIconAdmin(ModelAdminRedirectMixin, admin.ModelAdmin):
    list_display = ["name", "image_thumbnail"]

    @admin.display(ordering="image", description="Image")
    def image_thumbnail(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" height="50px" />')
        return "No image"
