from django.urls import path
from . import views


app_name = "bank_app"

urlpatterns = [
    path('', views.index, name='index'),
    path('admin-dashboard', views.admin_page, name='admin_page'),
    path('customer_dashboard', views.customer_dashboard, name='customer_dashboard'),
    path('customer_dashboard/<int:id>/', views.customer_dashboard, name='customer_dashboard'),
    path('make_loan_request/', views.make_loan_request, name='make_loan_request'),
    path('review_loan_request', views.review_loan_request, name='review_loan_request'),
    path('make_account_request/', views.make_account_request, name='make_account_request'),
    path('make_transfer/', views.make_transfer, name='make_transfer'),
    path('add_customer/', views.add_customer, name='add_customer'),
    path('admin-dashboard/<int:id>/decline', views.decline_loan_request, name='decline_loan_request'),
    path('admin-dashboard/<int:id>/approve', views.approve_loan_request, name='approve_loan_request'),
    path('admin-dashboard/<int:id>/decline-account', views.decline_account_request, name='decline_account_request'),
    path('admin-dashboard/<int:id>/approve-account', views.approve_account_request, name='approve_account_request'),
    path('account-details/<int:id>', views.account_details, name='account_details'),
    path('customer_overview/', views.customer_overview, name='customer_overview'),
    path('search_customers/', views.search_customers, name='search_customers'),
    path('change_rank/<int:id>', views.change_rank, name='change_rank'),
]
