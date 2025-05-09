import datetime
from account.models import User
from jalali_date_new.utils import to_georgian
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from .forms import VacationRequestForm, ProblemReportForm,\
    VacationRequestBossReviewForm, VacationRequestAlterReviewForm,\
    SearchForm, ProblemSearchForm, TodoListForm, TaskReviewForm
from .models import VacationRequest, ProblemReport, Log, TodoList, TaskAssignment
from shop.models import ProductBuyOrder, ProductStockroomOrder, Note
from shop.forms import NoteForm
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, FileResponse
from django.core.exceptions import PermissionDenied
from common import export
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta


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
    
    # بررسی اگر درخواست از صفحه درخواست‌های جانشینی آمده است و کاربر جانشین است
    if request.GET.get('from_alternative') == 'true' and instance.alternative == request.user:
        # ریدایرکت به صفحه بررسی جانشین
        return redirect('organization:alternative_request_review', pk=pk)
    
    # بررسی وضعیت درخواست - فقط درخواست‌هایی که توسط جانشین بررسی شده‌اند قابل بررسی توسط مدیر هستند
    if instance.status == "بررسی نشده":
        return render(request, "VacationDetail.html",
                  {"title": "جزئیات درخواست مرخصی",
                   "user": request.user,
                   "instance": instance,
                   "message": "این درخواست هنوز توسط جانشین بررسی نشده است. ابتدا باید جانشین آن را تأیید یا رد کند.",
                   "status": "error"
                   })
    
    # اگر جانشین درخواست را رد کرده باشد، مدیر نمی‌تواند آن را تایید یا رد کند
    if instance.status == "رد جانشین":
        return render(request, "VacationDetail.html",
                  {"title": "جزئیات درخواست مرخصی",
                   "user": request.user,
                   "instance": instance,
                   "message": "این درخواست توسط جانشین رد شده است و قابل تایید یا رد توسط مدیر نیست.",
                   "status": "error"
                   })
    
    if request.method == 'POST':
        if request.user.has_perm('organization.change_vacationrequest'):
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
            return PermissionDenied
    else:
        # اگر وضعیت "تایید جانشین"، "موافقت شده" یا "رد شده" باشد، فرم تغییر وضعیت را نمایش می‌دهیم
        if instance.status in ["تایید جانشین", "موافقت شده", "رد شده"]:
            form = VacationRequestBossReviewForm(instance=instance)
            
            # تنظیم گزینه‌های فرم بر اساس وضعیت فعلی
            if instance.status == "تایید جانشین":
                form.fields['status'].choices = [
                    ("تایید جانشین", "تایید جانشین"),
                    ("موافقت شده", "موافقت شده"),
                    ("رد شده", "رد شده")
                ]
            elif instance.status == "موافقت شده":
                form.fields['status'].choices = [
                    ("موافقت شده", "موافقت شده"),
                    ("رد شده", "رد شده"),
                    ("تایید جانشین", "تایید جانشین")
                ]
            elif instance.status == "رد شده":
                form.fields['status'].choices = [
                    ("رد شده", "رد شده"),
                    ("موافقت شده", "موافقت شده"),
                    ("تایید جانشین", "تایید جانشین")
                ]
            
            return render(request, "VacationDetail.html",
                          {"title": "جزئیات درخواست مرخصی",
                           "user": request.user,
                           "form": form,
                           "instance": instance
                           })
        # اگر وضعیت دیگری دارد، فقط نمایش جزئیات
        else:
            return render(request, "VacationDetail.html",
                          {"title": "جزئیات درخواست مرخصی",
                           "user": request.user,
                           "instance": instance,
                           "message": f"وضعیت این درخواست {instance.status} است و قابل تغییر نیست.",
                           "status": "info"
                           })


# alter vacation request review and update
@login_required
def alter_request_review(request, pk):
    instance = VacationRequest.objects.get(id=pk)
    
    # اگر کاربر جانشین درخواست باشد، باید بتواند آن را بررسی کند 
    # حتی اگر مجوز مدیریت داشته باشد
    if instance.alternative == request.user:
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
    else:
        # اگر کاربر جانشین نباشد، اجازه دسترسی ندارد
        raise PermissionDenied


# all users vacation request logs for admin
@login_required
@permission_required("organization.view_vacationrequest", raise_exception=True)
def vacation_request_logs(request):
    if request.user.has_perm('organization.change_vacationrequest'):
        # نمایش همه درخواست‌ها بدون فیلتر وضعیت
        logs = VacationRequest.objects.all().order_by("-created")
    else:
        # برای کاربران عادی فقط درخواست‌های تایید شده نمایش داده می‌شود
        logs = VacationRequest.objects.filter(status="موافقت شده").order_by("-created")

    # تعیین تعداد آیتم‌ها در هر صفحه از پارامتر page_size درخواست
    page_size = request.GET.get("page_size", 15)
    try:
        page_size = int(page_size)
        if page_size <= 0:
            page_size = 15
    except ValueError:
        page_size = 15

    paginator = Paginator(logs, page_size)
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
                      {'logs': logs,
                       'action_mode': 'boss'})

    search_form = SearchForm(data=request.GET)
    return render(request, "VacationLogsActions.html",
                  {"title": "سوابق درخواست مرخصی",
                   "user": request.user,
                   "logs": logs,
                   "action_mode": "boss",
                   "search_form": search_form,
                   "report_type": "vacation_reqs",
                   "is_paginated": paginator.num_pages > 1,  # فعال کردن صفحه‌بندی اگر بیش از یک صفحه وجود دارد
                   "page_obj": logs  # ارسال آبجکت صفحه برای استفاده در قالب صفحه‌بندی
                   })


# export request logs to pdf
@login_required
def export_to_pdf(request, content):
    print(f"Export PDF requested for content: {content}")
    print(f"Request parameters: {request.GET}")
    
    try:
        # اگر تاریخی در فرم وارد نشده باشد، از دو هفته قبل تا امروز را در نظر می‌گیریم
        start_date_str = request.GET.get("start_date")
        end_date_str = request.GET.get("end_date")
        
        if not start_date_str or not end_date_str:
            # اگر تاریخ‌ها خالی هستند، دو هفته اخیر را انتخاب می‌کنیم
            end_date = datetime.datetime.now()
            start_date = end_date - datetime.timedelta(days=14)
        else:
            # تبدیل تاریخ‌های شمسی به میلادی
            start_date = to_georgian(start_date_str)
            end_date = to_georgian(end_date_str) + datetime.timedelta(days=1)  # افزودن یک روز برای شمول تاریخ پایان
            
        print(f"Date range: {start_date} to {end_date}")
        
        # اگر وضعیت انتخاب نشده باشد، همه وضعیت‌ها را در نظر می‌گیریم
        status_str = request.GET.get("status", 'تمام موارد')
        
        all_status = ["بررسی نشده", "بررسی بیشتر", "تایید جانشین", "رد جانشین", "موافقت شده", "رد شده", True, False]
        status = all_status if status_str == 'تمام موارد' or not status_str else [status_str]
        bool_status = [True, False] if status_str == 'تمام موارد' or not status_str else [True if status_str == 'True' or status_str == 'بله' else False]
        
        print(f"Status filter: {status}")
        print(f"Bool status filter: {bool_status}")

        # فیلتر کردن خروجی بر اساس کاربر
        user_id = request.GET.get("user")
        user = [User.objects.get(id=user_id)] if user_id else User.objects.all()

        print(f"User filter: {user}")

        match content:
            case('buy_orders'):
                if request.user.has_perm('shop.view_productbuyorder'):
                    logs = ProductBuyOrder.objects.filter(created__range=(start_date, end_date), status__in=status, user__in=user).order_by("-created")
                    print(f"Found {logs.count()} buy order logs")
                    pdf = export.generate_buy_order_pdf(logs)
                    f_name = f'buy-orders.pdf'
                    return FileResponse(pdf, as_attachment=True, filename=f_name)
                else:
                    raise PermissionDenied

            case('stock_orders'):
                if request.user.has_perm('shop.view_productstockroomorder'):
                    logs = ProductStockroomOrder.objects.filter(created__range=(start_date, end_date), status__in=status, user__in=user).order_by("-created")
                    print(f"Found {logs.count()} stock order logs")
                    pdf = export.generate_stock_order_pdf(logs)
                    f_name = f'stock-orders.pdf'
                    return FileResponse(pdf, as_attachment=True, filename=f_name)
                else:
                    raise PermissionDenied

            case('vacation_reqs'):
                if request.user.has_perm('organization.view_vacationrequest'):
                    # حالت ادمین - دیدن همه مرخصی‌ها
                    logs = VacationRequest.objects.filter(created__range=(start_date, end_date), status__in=status, user__in=user).order_by("-created")
                    print(f"Found {logs.count()} vacation request logs")
                    pdf = export.generate_vacation_req_pdf(logs)
                    f_name = f'vacation-requests.pdf'
                    return FileResponse(pdf, as_attachment=True, filename=f_name)
                else:
                    # حالت کاربر - فقط مرخصی‌های مربوط به جانشینی
                    logs = VacationRequest.objects.filter(
                        created__range=(start_date, end_date),
                        status__in=status,
                        alternative=request.user
                    ).order_by("-created")
                    print(f"Found {logs.count()} vacation alternative logs for user {request.user.username}")
                    pdf = export.generate_vacation_req_pdf(logs)
                    f_name = f'vacation-alternative-requests.pdf'
                    return FileResponse(pdf, as_attachment=True, filename=f_name)

            case ('problem_reps'):
                if request.user.has_perm('organization.view_problemreport'):
                    logs = ProblemReport.objects.filter(created__range=(start_date, end_date),
                                                        effective__in=bool_status, user__in=user).order_by("-created")
                    print(f"Found {logs.count()} problem report logs")
                    pdf = export.generate_problem_reps_pdf(logs)
                    f_name = f'problem-reports.pdf'
                    return FileResponse(pdf, as_attachment=True, filename=f_name)
                else:
                    raise PermissionDenied
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return HttpResponse(f"خطا در تولید PDF: {e}", status=500)


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


# نمایش کارتی درخواست‌های مرخصی کاربر
@login_required
@permission_required("organization.add_vacationrequest", raise_exception=True)
def vacation_request_logs_card(request):
    logs = VacationRequest.objects.filter(user=request.user).order_by("-created")
    
    paginator = Paginator(logs, 15)
    page = request.GET.get("page")
    try:
        logs = paginator.page(page)
    except PageNotAnInteger:
        logs = paginator.page(1)
    except EmptyPage:
        return HttpResponse('')
    
    return render(request, 'VacationCardAJAX.html', {'logs': logs})


# user being alternative requests logs
@login_required
def alternative_request_logs(request):
    # بیایید همه رکوردها را بدون فیلتر بگیریم و ببینیم چند تا هستند
    all_logs = request.user.alter_vacation_req.all().order_by("-created")
    logs_count = all_logs.count()
    print(f"Total alternative logs for user {request.user.username}: {logs_count}")
    
    # اعمال فیلتر برای وضعیت
    logs = request.user.alter_vacation_req.filter(status__in=["تایید جانشین", "رد جانشین", "بررسی نشده"]).order_by("-created")
    filtered_count = logs.count()
    print(f"Filtered alternative logs for user {request.user.username}: {filtered_count}")
    print(f"Available statuses: {[log.status for log in all_logs[:10]]}")
    
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
                      {'logs': logs, 'action_mode': 'alter'})

    return render(request, "VacationLogsActions.html",
                  {"title": "درخواست های جانشینی",
                   "user": request.user,
                   "logs": logs,
                   "action_mode": "alter",
                   "report_type": "vacation_reqs"
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
def problem_report(request, problem_id=None):
    # بررسی دسترسی های لازم
    if not (request.user.has_perm("organization.view_problemreport") or
            request.user.has_perm("organization.add_problemreport") or
            request.user.has_perm("organization.change_problemreport")):
        raise PermissionDenied("شما دسترسی لازم برای مشاهده این صفحه را ندارید.")
    
    # بررسی آیا در حال ویرایش/مشاهده یک گزارش موجود هستیم
    instance = None
    if problem_id:
        try:
            instance = ProblemReport.objects.get(id=problem_id)
            # بررسی دسترسی - فقط کاربر ایجاد کننده یا کاربر با مجوز مشاهده می‌تواند آن را ببیند
            if instance.user != request.user and not request.user.has_perm("organization.view_problemreport"):
                messages.error(request, "شما اجازه مشاهده این گزارش را ندارید.")
                return redirect('organization:problem_reports')
        except ProblemReport.DoesNotExist:
            messages.error(request, "گزارش خطای مورد نظر یافت نشد.")
            return redirect('organization:problem_reports')
    
    if request.method == 'POST':
        # بررسی دسترسی برای ایجاد/ویرایش
        if instance and not request.user.has_perm("organization.change_problemreport"):
            messages.error(request, "شما اجازه ویرایش گزارش را ندارید.")
            return redirect('organization:problem_reports')
        elif not instance and not request.user.has_perm("organization.add_problemreport"):
            messages.error(request, "شما اجازه ایجاد گزارش جدید را ندارید.")
            return redirect('organization:problem_reports')
            
        # اگر گزارش موجود در حال ویرایش است
        if instance:
            form = ProblemReportForm(data=request.POST, instance=instance)
        else:
            form = ProblemReportForm(data=request.POST)
            
        if form.is_valid():
            cd = form.cleaned_data
            new = form.save(commit=False)
            if not instance:  # فقط اگر گزارش جدید است، کاربر را تنظیم کن
                new.user = request.user
            new.save()
            
            if instance:
                messages.success(request, "گزارش خطا با موفقیت به‌روزرسانی شد.")
                return redirect('organization:problem_report_logs')
            else:
                messages.success(request, "گزارش خطا با موفقیت ثبت شد.")
                return redirect('organization:problem_reports')
    else:
        # اگر گزارش موجود را مشاهده می‌کنیم
        if instance:
            form = ProblemReportForm(instance=instance)
            title = "مشاهده/ویرایش گزارش خطا"
            # اگر کاربر فقط مجوز مشاهده دارد، فیلدها را غیرفعال کن
            if not request.user.has_perm("organization.change_problemreport"):
                for field in form.fields.values():
                    field.widget.attrs['disabled'] = True
        else:
            # اگر کاربر مجوز ایجاد ندارد، به صفحه لیست هدایت کن
            if not request.user.has_perm("organization.add_problemreport"):
                messages.error(request, "شما اجازه ایجاد گزارش جدید را ندارید.")
                return redirect('organization:problem_reports')
                
            form = ProblemReportForm(data=request.GET)
            title = "ثبت خطا"

        return render(request, "ProblemReport.html",
                     {"title": title,
                      "user": request.user,
                      "form": form,
                      "instance": instance,
                      "can_edit": (instance and request.user.has_perm("organization.change_problemreport")) or 
                                 (not instance and request.user.has_perm("organization.add_problemreport"))
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
                   "search_form": search_form,
                   "report_type": "problem_reps"
                   })


# user problem reports
@login_required
def problem_reports(request):
    # بررسی دسترسی های لازم
    if not (request.user.has_perm("organization.view_problemreport") or
            request.user.has_perm("organization.add_problemreport")):
        raise PermissionDenied("شما دسترسی لازم برای مشاهده این صفحه را ندارید.")
    
    # بررسی آیا پارامتر id در درخواست وجود دارد
    problem_id = request.GET.get("id")
    
    # اگر شناسه مشخص شده باشد، به صفحه جزئیات گزارش هدایت کن
    if problem_id:
        try:
            # بررسی وجود گزارش با شناسه مشخص شده
            problem_report = ProblemReport.objects.get(id=problem_id)
            # هدایت به صفحه ویرایش/مشاهده گزارش خطا
            return redirect('organization:problem_report', problem_id=problem_id)
        except ProblemReport.DoesNotExist:
            # اگر گزارش وجود نداشت، پیام خطا نمایش بده
            messages.error(request, "گزارش خطای مورد نظر یافت نشد.")
    
    # در غیر این صورت، لیست گزارش‌ها را نمایش بده
    # اگر کاربر دسترسی مدیریتی دارد، همه گزارش‌ها را نمایش بده
    if request.user.has_perm('organization.view_problemreport'):
        logs = ProblemReport.objects.all().order_by("-created")
    else:
        # در غیر این صورت، فقط گزارش‌های کاربر را نمایش بده
        logs = ProblemReport.objects.filter(user=request.user).order_by("-created")

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
        return render(request, 'ProblemLogsAJAX.html',
                      {'logs': logs})

    return render(request, "ProblemLogs.html",
                  {"title": "وضعیت ثبت خطا",
                   "user": request.user,
                   "logs": logs,
                   "can_add": request.user.has_perm("organization.add_problemreport")
                   })


# اضافه کردن یک ویوی دیباگ موقت برای بررسی وضعیت دیتابیس
@login_required
def debug_vacation_requests(request):
    # دریافت تمام درخواست‌ها بدون فیلتر وضعیت
    all_requests = VacationRequest.objects.all().order_by("-created")
    
    # درخواست‌های کاربر فعلی
    user_requests = VacationRequest.objects.filter(user=request.user).order_by("-created")
    
    # درخواست‌هایی که کاربر فعلی جانشین است
    alternative_requests = VacationRequest.objects.filter(alternative=request.user).order_by("-created")
    
    return render(request, "debug_vacation_requests.html",
                 {"title": "دیباگ درخواست‌های مرخصی",
                  "user": request.user,
                  "all_requests": all_requests,
                  "user_requests": user_requests,
                  "alternative_requests": alternative_requests
                 })


# اضافه کردن ویو جدید برای مدیریت هوشمند درخواست‌های مرخصی
@login_required
def smart_vacation_review(request, pk):
    """
    این ویو بررسی می‌کند که آیا کاربر جاری جانشین درخواست است یا مدیر سیستم،
    و براساس آن به ویو مناسب ریدایرکت می‌کند.
    """
    instance = VacationRequest.objects.get(id=pk)
    
    # بررسی اگر درخواست از صفحه درخواست‌های جانشینی آمده است
    from_alternative = request.GET.get('from_alternative') == 'true'
    
    # اگر از صفحه درخواست‌های جانشینی آمده و کاربر جانشین است
    if from_alternative and instance.alternative == request.user:
        return redirect('organization:alternative_request_review', pk=pk)
    # اگر کاربر مجوز مدیریت دارد و از صفحه جانشینی نیامده
    elif request.user.has_perm('organization.view_vacationrequest') and not from_alternative:
        return redirect('organization:vacation_request_review', pk=pk)
    # اگر کاربر جانشین درخواست باشد
    elif instance.alternative == request.user:
        return redirect('organization:alternative_request_review', pk=pk)
    # در غیر این صورت، خطای دسترسی نمایش داده می‌شود
    else:
        raise PermissionDenied


"""
ویو های مربوط به تودو لیست و تسک ها
"""

# new TODO list
@login_required
@permission_required("organization.add_todolist", raise_exception=True)
def new_task(request):
    if request.method == 'POST':
        form = TodoListForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()

            for user in form.cleaned_data['assigned_to']:
                TaskAssignment.objects.create(
                    task=task,
                    user=user,
                    is_done=False,
                )

            return redirect('organization:task_logs')
    else:
        form = TodoListForm(data=request.GET)

        return render(request, "TaskCreate.html",
                      {"title": "ایجاد تسک",
                       "user": request.user,
                       "form": form
                       })


# user tasks
@login_required
@permission_required("organization.add_todolist", raise_exception=True)
def task_list_view(request):
    tasks = TodoList.objects.filter(created_by=request.user).order_by("-created_at")

    paginator = Paginator(tasks, 15)
    page = request.GET.get("page")
    try:
        tasks = paginator.page(page)
    except PageNotAnInteger:
        tasks = paginator.page(1)
    except EmptyPage:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return HttpResponse('')
        tasks = paginator.page(paginator.num_pages)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == 'true':
        return render(request, 'TaskLogsActionsAJAX.html',
                      {'tasks': tasks})

    return render(request, "TaskLogsActions.html",
                  {"title": "تسک‌های ایجاد شده",
                   "user": request.user,
                   "tasks": tasks,
                   })


# privileged user task logs
@login_required
@permission_required("organization.view_todolist", raise_exception=True)
def privileged_task_list_view(request):
    tasks = TodoList.objects.all().order_by("-created_at")

    paginator = Paginator(tasks, 15)
    page = request.GET.get("page")
    try:
        tasks = paginator.page(page)
    except PageNotAnInteger:
        tasks = paginator.page(1)
    except EmptyPage:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return HttpResponse('')
        tasks = paginator.page(paginator.num_pages)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == 'true':
        return render(request, 'TaskLogsActionsAJAX.html',
                      {'tasks': tasks})

    return render(request, "TaskLogsActions.html",
                  {"title": "سوابق تسک ها",
                   "user": request.user,
                   "tasks": tasks,
                   })


@login_required
@permission_required("organization.add_todolist", raise_exception=True)
def open_task_list_view(request):
    assignments = TaskAssignment.objects.filter(user=request.user).order_by("task__remind_at")
    reminder_tasks = []

    for assignment in assignments:
        if not assignment.is_done and assignment.task.remind_at.date() <= timezone.now().date():
            reminder_tasks.append(assignment)

    paginator = Paginator(reminder_tasks, 15)
    page = request.GET.get("page")
    try:
        reminder_tasks = paginator.page(page)
    except PageNotAnInteger:
        reminder_tasks = paginator.page(1)
    except EmptyPage:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return HttpResponse('')
        reminder_tasks = paginator.page(paginator.num_pages)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == 'true':
        return render(request, 'TaskActionsAJAX.html',
                      {'tasks': reminder_tasks})

    return render(request, "TaskActions.html",
                  {"title": "تسک های جاری",
                   "user": request.user,
                   "tasks": reminder_tasks,
                   })


# task review and update
@login_required
@permission_required("organization.add_taskassignment", raise_exception=True)
def task_review(request, pk):
    instance = TaskAssignment.objects.get(id=pk)
    if instance.user == request.user:
        if request.method == 'POST':
            form = TaskReviewForm(data=request.POST, instance=instance)
            note_form = NoteForm(data=request.POST)
            if form.has_changed():
                if instance.is_done != bool(form.data.get('is_done')):
                    message = f'وضعیت انجام تسک را از "{"انجام نشده" if instance.is_done == False else "انجام شده"}" به "{"انجام شده" if form.data.get('is_done') else "انجام نشده"}" تغییر داد.'
                    Log.objects.create(user=request.user,
                                       action=message,
                                       content_object=instance.task)
                if instance.status != form.data['status']:
                    message2 = f'وضعیت تسک را از "{instance.status}" به "{form.data['status']}" تغییر داد.'
                    Log.objects.create(user=request.user,
                                       action=message2,
                                       content_object=instance.task)
            if form.is_valid() and note_form.is_valid():
                cd = form.cleaned_data
                new = form.save(commit=False)
                new.save()
                cd_note = note_form.cleaned_data
                if cd_note["text"] != "":
                    new_note = note_form.save(commit=False)
                    new_note.user = request.user
                    new_note.content_object = instance.task
                    new_note.save()

                return redirect('organization:task_review', instance.id)

        else:
            form = TaskReviewForm(instance=instance)

            authors = [instance.task.created_by, request.user]

            note_form = NoteForm(data=request.GET)
            target = ContentType.objects.get_for_model(instance.task)
            notes = Note.objects.filter(content_type=target, object_id=instance.task.id, user__in=authors)

            # اضافه کردن متغیر can_edit برای کنترل دسترسی در قالب
            can_edit = request.user.has_perm("organization.change_taskassignment") or instance.user == request.user

            return render(request, "TaskDetail.html",
                          {"title": "جزئیات تسک",
                           "user": request.user,
                           "form": form,
                           "instance": instance,
                           "note_form": note_form,
                           "notes": notes,
                           "can_edit": can_edit
                           })
    else:
        return PermissionDenied


# task review and update
@login_required
@permission_required("organization.add_todolist", raise_exception=True)
def creator_task_review(request, pk):
    instance = TodoList.objects.get(id=pk)
    if instance.created_by == request.user or request.user.has_perm('organization.view_todolist'):
        if request.method == 'POST':
            note_form = NoteForm(data=request.POST)

            if note_form.is_valid():
                cd_note = note_form.cleaned_data
                if cd_note["text"] != "":
                    new_note = note_form.save(commit=False)
                    new_note.user = request.user
                    new_note.content_object = instance
                    new_note.save()

                return redirect('organization:creator_task_review', instance.id)

        else:
            assignments = TaskAssignment.objects.filter(task=instance)

            note_form = NoteForm(data=request.GET)
            target = ContentType.objects.get_for_model(instance)
            notes = Note.objects.filter(content_type=target, object_id=instance.id)

            # اضافه کردن متغیر can_edit برای کنترل دسترسی در قالب
            can_edit = request.user.has_perm("organization.change_todolist") or instance.created_by == request.user

            return render(request, "CreatorTaskDetail.html",
                          {"title": "جزئیات تسک",
                           "user": request.user,
                           "instance": instance,
                           "assignments": assignments,
                           "note_form": note_form,
                           "notes": notes,
                           "can_edit": can_edit
                           })
    else:
        raise PermissionDenied