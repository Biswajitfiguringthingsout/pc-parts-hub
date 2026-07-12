from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('<int:id>/', views.product_detail, name='product_detail'),

    path(
        'category/<str:category>/',
        views.products_by_category,
        name='products_by_category'
    ),
    path(
        'build/',
        views.build_page,
        name='build_page'
    ),
    path(
        'build/add/<int:product_id>/',
        views.add_to_build,
        name='add_to_build'
    ),
    path(
        'build/remove/<int:item_id>/',
        views.remove_build_item,
        name='remove_build_item'
    ),
    path(
        "compare-gpus/",
        views.compare_gpus,
        name="compare_gpus",
    ),
    path(
        "compare-cpus/",
        views.compare_cpus,
        name="compare_cpus",
    ),
]