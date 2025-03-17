import datetime
from re import search
from jalali_date_new.utils import to_georgian
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from .forms import VacationRequestForm, ProblemReportForm,\
    VacationRequestBossReviewForm, VacationRequestAlterReviewForm, SearchForm, ProblemSearchForm
from .models import VacationRequest, ProblemReport, Log
from shop.models import ProductBuyOrder, ProductStockroomOrder
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, FileResponse
from django.core.exceptions import PermissionDenied
from common import export


"""
Views for handling vacation requests written below:
Add, View, Update operations

Requires being signed in with @login_required() decorator

Accessibility and permission allowing included for each one by @permission_required() decorator:
add permission -> add_vacationrequest
view and update permission -> view_vacationrequest
"""

# new vacation request
@login_required
@permission_required("organization.add_vacationrequest", raise_exception=True)
def vacation_request(request):
    if request.method == 'POST':
        form = VacationRequestForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            new = form.save(commit=False)
            new.user = request.user
            new.save()

            return redirect('organization:vacation_requests')
    else:
        form = VacationRequestForm(data=request.GET)

        return render(request, "VacationRequest.html",
                      {"title": "درخواست مرخصی",
                       "user": request.user,
                       "form": form
                       })


# admin vacation request review and update
@login_required
@permission_required("organization.view_vacationrequest", raise_exception=True)
def vacation_request_review(request, pk):
    instance = VacationRequest.objects.get(id=pk)
    if request.method == 'POST':
        form = VacationRequestBossReviewForm(data=request.POST, instance=instance)
        if form.has_changed():
            message = f'وضعیت درخواست را از "{instance.status}" به "{form.data['status']}" تغییر داد.'
            Log.objects.create(user=request.user,
                               action=message,
                               content_object=instance)
        if form.is_valid():
            form.save()

            return redirect('organization:vacation_request_logs')
    else:
        form = VacationRequestBossReviewForm(instance=instance)

        return render(request, "VacationDetail.html",
                      {"title": "جزئیات درخواست مرخصی",
                       "user": request.user,
                       "form": form,
                       "instance": instance
                       })


# alter vacation request review and update
@login_required
@permission_required("organization.add_vacationrequest", raise_exception=True)
def alter_request_review(request, pk):
    instance = VacationRequest.objects.get(id=pk)
    if request.method == 'POST':
        form = VacationRequestAlterReviewForm(data=request.POST, instance=instance)
        if form.has_changed():
            message = f'وضعیت درخواست را از "{instance.status}" به "{form.data['status']}" تغییر داد.'
            Log.objects.create(user=request.user,
                               action=message,
                               content_object=instance)
        if form.is_valid():
            form.save()

            return redirect('organization:alternative_requests')
    else:
        form = VacationRequestAlterReviewForm(instance=instance)

        return render(request, "VacationDetail.html",
                      {"title": "جزئیات درخواست مرخصی",
                       "user": request.user,
                       "form": form,
                       "instance": instance
                       })


# all users vacation request logs for admin
@login_required
@permission_required("organization.view_vacationrequest", raise_exception=True)
def vacation_request_logs(request):
    logs = VacationRequest.objects.filter(status__in=["تایید جانشین", "موافقت شده", "رد شده"]).order_by("-created")

    paginator = Paginator(logs, 15)
    page = request.GET.get("page")
    try:
        logs = paginator.page(page)
    except PageNotAnInteger:
        logs = paginator.page(1)
    except EmptyPage:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return HttpResponse('')
        logs = paginator.page(paginator.num_pages)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'VacationLogsActionsAJAX.html',
                      {'logs': logs})

    search_form = SearchForm(data=request.GET)
    return render(request, "VacationLogsActions.html",
                  {"title": "سوابق درخواست مرخصی",
                   "user": request.user,
                   "logs": logs,
                   "action_mode": "boss",
                   "search_form": search_form
                   })


# export request logs to pdf
@login_required
def export_to_pdf(request, content):
    start_date = request.GET.get("start_date")
    start_date = to_georgian(start_date)
    end_date = request.GET.get("end_date")
    end_date = to_georgian(end_date)
    all_status = ["بررسی نشده", "بررسی بیشتر", "تایید جانشین", "رد جانشین", "موافقت شده", "رد شده", True, False]
    status = all_status if request.GET.get("status") == 'تمام موارد' else [request.GET.get("status")]
    bool_status = [True, False] if request.GET.get("status") == 'تمام موارد' else [request.GET.get("status")]

    match content:
        case('buy_orders'):
            if request.user.has_perm('shop.view_productbuyorder'):
                logs = ProductBuyOrder.objects.filter(created__range=(start_date, end_date), status__in=status).order_by("-created")
                pdf = export.generate_buy_order_pdf(logs)
                f_name = f'buy-orders.pdf'
                return FileResponse(pdf, as_attachment=True, filename=f_name)
            else:
                raise PermissionDenied

        case('stock_orders'):
            if request.user.has_perm('shop.view_productstockroomorder'):
                logs = ProductStockroomOrder.objects.filter(created__range=(start_date, end_date), status__in=status).order_by("-created")
                pdf = export.generate_stock_order_pdf(logs)
                f_name = f'stock-orders.pdf'
                return FileResponse(pdf, as_attachment=True, filename=f_name)
            else:
                raise PermissionDenied

        case('vacation_reqs'):
            if request.user.has_perm('organization.view_vacationrequest'):
                logs = VacationRequest.objects.filter(created__range=(start_date, end_date), status__in=status).order_by("-created")
                pdf = export.generate_vacation_req_pdf(logs)
                f_name = f'vacation-requests.pdf'
                return FileResponse(pdf, as_attachment=True, filename=f_name)
            else:
                raise PermissionDenied

        case ('problem_reps'):
            if request.user.has_perm('organization.view_problemreport'):
                logs = ProblemReport.objects.filter(created__range=(start_date, end_date),
                                                    effective__in=bool_status).order_by("-created")
                pdf = export.generate_problem_reps_pdf(logs)
                f_name = f'problem-reports.pdf'
                return FileResponse(pdf, as_attachment=True, filename=f_name)
            else:
                raise PermissionDenied


# user vacation request logs
@login_required
@permission_required("organization.add_vacationrequest", raise_exception=True)
def vacation_requests(request):
    logs = VacationRequest.objects.filter(user=request.user).order_by("-created")

    paginator = Paginator(logs, 15)
    page = request.GET.get("page")
    try:
        logs = paginator.page(page)
    except PageNotAnInteger:
        logs = paginator.page(1)
    except EmptyPage:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return HttpResponse('')
        logs = paginator.page(paginator.num_pages)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'VacationLogsAJAX.html',
                      {'logs': logs})

    return render(request, "VacationLogs.html",
                  {"title": "وضعیت درخواست مرخصی",
                   "user": request.user,
                   "logs": logs
                   })


# user being alternative requests logs
@login_required
@permission_required("organization.add_vacationrequest", raise_exception=True)
def alternative_request_logs(request):
    logs = request.user.alter_vacation_req.filter(status__in=["تایید جانشین", "رد جانشین", "بررسی نشده"]).order_by("-created")

    paginator = Paginator(logs, 15)
    page = request.GET.get("page")
    try:
        logs = paginator.page(page)
    except PageNotAnInteger:
        logs = paginator.page(1)
    except EmptyPage:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return HttpResponse('')
        logs = paginator.page(paginator.num_pages)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'VacationLogsActionsAJAX.html',
                      {'logs': logs})

    return render(request, "VacationLogsActions.html",
                  {"title": "درخواست های جانشینی",
                   "user": request.user,
                   "logs": logs
                   })


"""
Views for handling problem reports written below:
Add, View operations

Requires being signed in with @login_required() decorator

Accessibility and permission allowing included for each one by @permission_required() decorator
add permission -> add_problemreport
view and update permission -> view_problemreport
"""

# new problem report
@login_required
@permission_required("organization.add_problemreport", raise_exception=True)
def problem_report(request):
    if request.method == 'POST':
        form = ProblemReportForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            new = form.save(commit=False)
            new.user = request.user
            new.save()

            return redirect('organization:problem_reports')
    else:
        form = ProblemReportForm(data=request.GET)

        return render(request, "ProblemReport.html",
                      {"title": "ثبت خطا",
                       "user": request.user,
                       "form": form
                       })


# all users problem report logs
@login_required
@permission_required("organization.view_problemreport", raise_exception=True)
def problem_report_logs(request):
    logs = ProblemReport.objects.all().order_by("-created")

    paginator = Paginator(logs, 15)
    page = request.GET.get("page")
    try:
        logs = paginator.page(page)
    except PageNotAnInteger:
        logs = paginator.page(1)
    except EmptyPage:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return HttpResponse('')
        logs = paginator.page(paginator.num_pages)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'ProblemLogsActionsAJAX.html',
                      {'logs': logs})

    search_form = ProblemSearchForm(data=request.GET)
    return render(request, "ProblemLogsActions.html",
                  {"title": "سوابق ثبت خطا",
                   "user": request.user,
                   "logs": logs,
                   "search_form": search_form
                   })


# user problem reports
@login_required
@permission_required("organization.add_problemreport", raise_exception=True)
def problem_reports(request):
    logs = ProblemReport.objects.filter(user=request.user).order_by("-created")

    return render(request, "ProblemLogs.html",
                  {"title": "وضعیت ثبت خطا",
                   "user": request.user,
                   "logs": logs
                   })