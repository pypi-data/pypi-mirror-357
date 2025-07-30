from django.forms import ModelForm

from NEMO_floor_plans.models import FloorPlan, FloorPlanNode


class FloorPlanNodeForm(ModelForm):
    class Meta:
        model = FloorPlanNode
        fields = "__all__"


class FloorPlanForm(ModelForm):
    class Meta:
        model = FloorPlan
        fields = "__all__"
