from NEMO.utilities import format_datetime
from django.core.exceptions import ValidationError
from django.db import models
from django.forms import model_to_dict

from NEMO_sensors.models import Sensor
from NEMO.models import BaseModel


class FloorPlan(BaseModel):
    name = models.CharField(max_length=100, blank=False, null=False, help_text="The name of the floor plan")
    image = models.ImageField(
        upload_to="floor_plans/", blank=False, null=False, help_text="The image of the floor plan"
    )
    is_default = models.BooleanField(default=False, help_text="Whether this floor plan is the default one")

    def serialize(self):
        data = model_to_dict(self)
        if self.image:
            data["image"] = self.image.url
        return data

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.pk:
            old_instance = FloorPlan.objects.get(pk=self.pk)

            # delete existing image if it is updated
            if old_instance.image and self.image != old_instance.image:
                old_instance.image.delete(save=False)

            # make sure only one floor plan is default
            if self.is_default and not old_instance.is_default:
                FloorPlan.objects.exclude(pk=self.pk).update(is_default=False)

        super().save(*args, **kwargs)


class FloorPlanIcon(BaseModel):
    name = models.CharField(max_length=100, blank=False, null=False, help_text="The name of the icon")
    image = models.ImageField(upload_to="floor_plan_icons/", blank=False, null=False, help_text="The image of the icon")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # delete existing image if it is updated
        if self.pk:
            old_instance = FloorPlanIcon.objects.get(pk=self.pk)
            if old_instance.image and self.image != old_instance.image:
                old_instance.image.delete(save=False)

        super().save(*args, **kwargs)


class FloorPlanNode(BaseModel):
    class NodeType(object):
        PORTAL = 0
        SENSOR = 1
        Choices = ((PORTAL, "Portal"), (SENSOR, "Sensor"))

    class SensorTextPositionType(object):
        TOP = 0
        RIGHT = 1
        BOTTOM = 2
        LEFT = 3
        Choices = ((TOP, "Top"), (RIGHT, "Right"), (BOTTOM, "Bottom"), (LEFT, "Left"))

    floor_plan = models.ForeignKey(FloorPlan, on_delete=models.CASCADE, related_name="nodes")
    type = models.IntegerField(choices=NodeType.Choices, blank=False, null=False, default=NodeType.SENSOR)
    icon = models.ForeignKey(FloorPlanIcon, on_delete=models.SET_NULL, blank=True, null=True)
    icon_scale = models.FloatField(default=1.0)
    x = models.IntegerField(blank=False, null=False, help_text="The x coordinate of the node")
    y = models.IntegerField(blank=False, null=False, help_text="The y coordinate of the node")
    font_size = models.FloatField(default=25, blank=True, null=True, help_text="The font size of the node label")
    sensor_text_position = models.IntegerField(
        choices=SensorTextPositionType.Choices,
        blank=True,
        null=True,
        help_text="The position of the sensor text",
    )
    sensor = models.ForeignKey(Sensor, on_delete=models.SET_NULL, blank=True, null=True)
    portal_to = models.ForeignKey(FloorPlan, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"Node ({self.id}) of type {self.type.__str__()} on {self.floor_plan.name}"

    def serialize(self, include_sensor_data=True):
        node_value = {}
        if self.type == FloorPlanNode.NodeType.SENSOR and self.sensor:
            if include_sensor_data:
                node_value["sensor_value"] = self.sensor.last_value_display() if self.sensor.last_value else None
                node_value["sensor_datetime"] = (
                    format_datetime(self.sensor.last_read, "SHORT_DATETIME_FORMAT") if self.sensor.last_read else None
                )
                node_value["sensor_alert"] = self.sensor.alert_triggered()

            node_value["sensor_id"] = self.sensor.id
            node_value["sensor_name"] = self.sensor.name
        if self.type == FloorPlanNode.NodeType.PORTAL and self.portal_to:
            node_value["portal_name"] = self.portal_to.name
            node_value["portal_id"] = self.portal_to.id
            node_value["portal_img"] = self.portal_to.image.url

        return {
            "id": self.id,
            "type": self.get_type_display(),
            "type_id": self.type,
            "icon": self.icon.image.url if self.icon else None,
            "icon_id": self.icon.id if self.icon else None,
            "icon_scale": self.icon_scale,
            "font_size": self.font_size,
            "sensor_text_position": self.sensor_text_position,
            "x": self.x,
            "y": self.y,
            **node_value,
        }

    def clean(self):
        if self.type == self.NodeType.SENSOR:
            if not self.sensor:
                raise ValidationError({"sensor": "Sensor is required."})
            if self.portal_to:
                raise ValidationError({"portal_to": "Sensor node cannot have portal."})
            if self.sensor_text_position is None:
                raise ValidationError({"sensor_text_position": "Sensor text position is required."})
            if not self.font_size:
                raise ValidationError({"font_size": "Font size is required."})

        if self.type == self.NodeType.PORTAL:
            if not self.portal_to:
                raise ValidationError({"portal_to": "Portal is required."})
            if self.sensor:
                raise ValidationError({"type": "Portal node cannot have sensor."})
            if self.floor_plan == self.portal_to:
                raise ValidationError({"portal_to": "Portal cannot be the same as the current floor plan."})
