from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import CMMReport
import json


def dashboard(request):

    # ============================
    #  HANDLE POST (IN / OUT TIME)
    # ============================
    if request.method == "POST":
        action = request.POST.get("action")  # "in" or "out"

        line = request.POST.get("line")
        machine = request.POST.get("machine")
        part_no = request.POST.get("part_no")
        operation = request.POST.get("operation")
        oe_name = request.POST.get("oe_name")
        shift = request.POST.get("shift")
        remarks = request.POST.get("remarks")
        activity = request.POST.get("activity")

        now = timezone.now()

        # -----------------------
        # IN-TIME LOGIC
        # -----------------------
        if action == "in":
            CMMReport.objects.create(
                line=line,
                machine=machine,
                part_no=part_no,
                operation=operation,
                oe_name=oe_name,
                shift=shift,
                remarks=remarks,
                activity=activity,
                in_time=now,
                uploaded_from=request.META.get("REMOTE_ADDR", "UNKNOWN")
            )

        # -----------------------
        # OUT-TIME LOGIC
        # -----------------------
        elif action == "out":
            record = (
                CMMReport.objects.filter(
                    line=line,
                    machine=machine,
                    part_no=part_no,
                    oe_name=oe_name,
                    shift=shift,
                    out_time__isnull=True,
                )
                .order_by("-in_time")
                .first()
            )

            if record:
                record.out_time = now
                record.remarks = remarks
                record.activity = activity
                record.save()

            else:
                # No matching IN-TIME found → create OUT entry alone
                CMMReport.objects.create(
                    line=line,
                    machine=machine,
                    part_no=part_no,
                    operation=operation,
                    oe_name=oe_name,
                    shift=shift,
                    remarks=remarks,
                    activity=activity,
                    out_time=now,
                    uploaded_from=request.META.get("REMOTE_ADDR", "UNKNOWN")
                )

        # MOST IMPORTANT: PREVENT DUPLICATION ON REFRESH
        return redirect("dashboard")

    # ============================
    #  GET REQUEST — SHOW TABLE
    # ============================

    reports = CMMReport.objects.order_by("-timestamp")[:10]

    # Add duration + row color
    for r in reports:

        if r.in_time and r.out_time:
            duration_hours = (r.out_time - r.in_time).total_seconds() / 3600
            r.duration_hours = duration_hours

            if duration_hours <= 1:
                r.row_class = "row-green"
            elif duration_hours <= 2:
                r.row_class = "row-yellow"
            elif duration_hours <= 3:
                r.row_class = "row-orange"
            else:
                r.row_class = "row-normal"

        else:
            r.duration_hours = None
            r.row_class = "row-normal"

    return render(request, "dashboard.html", {"reports": reports})


@csrf_exempt
def verify_exit(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        username = data.get("username")
        password = data.get("password")

        user = authenticate(username=username, password=password)

        if user is not None:
            return JsonResponse({"status": "ok"})
        else:
            return JsonResponse({"status": "error"})

    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def delete_row(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        row_id = data.get("id")

        try:
            CMMReport.objects.get(id=row_id).delete()
            return JsonResponse({"status": "ok"})
        except:
            return JsonResponse({"status": "error"})

    return JsonResponse({"status": "invalid"})
