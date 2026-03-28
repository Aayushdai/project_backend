from django.urls import path
from . import views

urlpatterns = [
    path('add/<int:trip_id>/', views.add_expense, name='add-expense'),
    path('', views.ExpenseListView.as_view(), name='expense-list'),
]