from django.urls import path
from . import views


app_name = 'organization'

urlpatterns = [
    path('vacation-request', views.vacation_request, name='vacation_request'),
    path('vacation-requests', views.vacation_requests, name='vacation_requests'),
    path('alternative-requests', views.alternative_request_logs, name='alternative_requests'),
    path('vacation-requests/<int:pk>', views.vacation_request_review, name='vacation_request_review'),
    path('alternative-requests/<int:pk>', views.alter_request_review, name='alternative_request_review'),
    path('vacation-request-logs', views.vacation_request_logs, name='vacation_request_logs'),
    path('problem-report', views.problem_report, name='problem_report'),
    path('problem-reports', views.problem_reports, name='problem_reports'),
    path('problem-report-logs', views.problem_report_logs, name='problem_report_logs'),
    path('export-pdf/<str:content>', views.export_to_pdf, name='export_pdf')
]
