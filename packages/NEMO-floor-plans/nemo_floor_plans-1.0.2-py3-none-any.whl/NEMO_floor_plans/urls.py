from django.urls import path

from NEMO_floor_plans import views

urlpatterns = [
    # Contracts and procurements
    path("floor_plans/", views.floor_plans, name="floor_plans"),
    path("floor_plans/<int:floor_plan_id>/", views.floor_plans, name="floor_plan"),
    path("floor_plans/<int:floor_plan_id>/edit", views.floor_plan_edit, name="floor_plan_edit"),
    path("floor_plans/<int:floor_plan_id>/nodes", views.floor_plan_nodes, name="floor_plan_nodes"),
]
