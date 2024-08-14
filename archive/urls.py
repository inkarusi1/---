from django.urls import path

from . import views

app_name = "archive"
urlpatterns = [
    # ex: /archive/
    path("", views.index, name="index"),
    # path("", views.IndexView.as_view(), name="index"),
    path("<int:block_id>/", views.detail, name="detail"),
    # path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:block_id>/modify/", views.modify_block, name="modify_block"),
    path("<int:block_id>/results/", views.results, name="results"),
    # path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    path("add-block-view/", views.add_block_view, name="add_block_view"),
    path("add-block/", views.add_block, name="add_block"),
    path("<int:block_id>/delete-block/", views.delete_block, name="delete_block"),
    path("add-blocks-from-excel/", views.add_blocks_from_excel, name="add_blocks_from_excel"),
]
