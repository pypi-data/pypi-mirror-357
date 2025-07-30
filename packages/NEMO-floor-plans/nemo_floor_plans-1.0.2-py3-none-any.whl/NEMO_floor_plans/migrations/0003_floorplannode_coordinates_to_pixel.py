from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("NEMO_floor_plans", "0002_floorplannode_sensor_text_position"),
    ]

    def update_coordinates(apps, schema_editor):
        FloorPlanNode = apps.get_model("NEMO_floor_plans", "FloorPlanNode")

        for node in FloorPlanNode.objects.all():
            floor_plan = node.floor_plan
            image_width = floor_plan.image.width
            image_height = floor_plan.image.height
            node.x = int(node.x * image_width)
            node.y = int(node.y * image_height)
            node.save()

    def revert_coordinates(apps, schema_editor):
        FloorPlanNode = apps.get_model("NEMO_floor_plans", "FloorPlanNode")

        for node in FloorPlanNode.objects.all():
            floor_plan = node.floor_plan
            image_width = floor_plan.image.width
            image_height = floor_plan.image.height
            node.x = node.x / image_width
            node.y = node.y / image_height
            node.save()

    operations = [
        migrations.RunPython(update_coordinates, revert_coordinates),
        migrations.AlterField(
            model_name="floorplannode",
            name="x",
            field=models.IntegerField(help_text="The x coordinate of the node"),
        ),
        migrations.AlterField(
            model_name="floorplannode",
            name="y",
            field=models.IntegerField(help_text="The y coordinate of the node"),
        ),
    ]
