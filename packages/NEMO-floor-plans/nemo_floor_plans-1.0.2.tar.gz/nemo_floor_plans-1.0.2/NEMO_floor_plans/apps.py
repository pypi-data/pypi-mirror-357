from django.apps import AppConfig


class FloorPlansConfig(AppConfig):
    name = "NEMO_floor_plans"
    verbose_name = "NEMO Floor Plans"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        from NEMO.plugins.utils import check_extra_dependencies

        """
        This code will be run when Django starts.
        """
        check_extra_dependencies(self.name, ["NEMO", "NEMO-CE"])
        check_extra_dependencies(self.name, ["nemo-sensors"])
