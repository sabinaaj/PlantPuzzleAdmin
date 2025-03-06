from django.views.generic import View
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import Avg, Exists, OuterRef
from django.utils.timezone import now, timedelta
from django.conf import settings

import os
import pdfkit

from areas.models import Area
from visitors.models import SuccessRate, VisitorResponse
from worksheets.models import Worksheet


class StatsExportView(View):

    def get(self, request):

        # Get the selected time range from the request parameters, defaulting to 'all'
        time_range = request.GET.get('range', 'all')

        # Determine the start date based on the selected time range
        if time_range == 'today':
            start_date = now().replace(hour=0, minute=0, second=0)
            time = f"{start_date.strftime('%d. %m.')}"
        elif time_range == 'week':
            start_date = now() - timedelta(days=7)
            time = f"posledních 7 dní ({start_date.strftime('%d. %m.')} – {now().strftime('%d. %m.')})"
        elif time_range == 'month':
            start_date = now() - timedelta(days=30)
            time = f"posledních 30 dní ({start_date.strftime('%d. %m.')} – {now().strftime('%d. %m.')})"
        else:
            start_date = None
            time = "celé období"

        # Fetch relevant data efficiently
        success_rates = SuccessRate.objects.all()
        responses = VisitorResponse.objects.all()
        if start_date:
            success_rates = success_rates.filter(created_at__gte=start_date)
            responses = responses.filter(created_at__gte=start_date)

        # Precompute aggregated values
        aggregated_success_rates = success_rates.aggregate(avg_rate=Avg('rate'))
        avg_rate = int(aggregated_success_rates['avg_rate'] or 0)

        # Retrieve areas linked to worksheets with success rate data
        areas = Area.objects.filter(
            Exists(Worksheet.objects.filter(area=OuterRef('pk'), successrate__in=success_rates))
        ).prefetch_related('worksheet_set', 'worksheet_set__task_set', 'worksheet_set__successrate_set')

        # Construct context for rendering the template
        context = {
            'time': time,
            'static_root': settings.STATIC_ROOT,
            'visitors_cnt': success_rates.values('visitor').distinct().count(),
            'done_cnt': success_rates.count(),
            'avg_rate': avg_rate,
            'areas': []
        }

        for area in areas:
            worksheets = []
            for worksheet in area.worksheet_set.all():
                done_cnt = success_rates.filter(worksheet=worksheet).count()
                if done_cnt == 0:
                    continue

                avg_rate = int(success_rates.filter(worksheet=worksheet).aggregate(rate=Avg('rate'))['rate'] or 0)

                tasks = [
                    {
                        'text': task.text,
                        'done_percent': int(
                            responses.filter(question__in=task.question_set.all(), is_correct=True).count()
                            / responses.filter(question__in=task.question_set.all()).count() * 100
                            if responses.filter(question__in=task.question_set.all()).count() > 0 else 0
                        ),
                    }
                    for task in worksheet.task_set.all()
                ]

                worksheets.append({
                    'title': worksheet.title,
                    'done_cnt': done_cnt,
                    'avg_rate': avg_rate,
                    'tasks': tasks,
                })

            context['areas'].append({
                'title': area.title,
                'icon': area.icon.path if area.icon else None,
                'done_cnt': success_rates.filter(worksheet__area=area).count(),
                'avg_rate': int(
                    success_rates.filter(worksheet__area=area).aggregate(rate=Avg('rate'))['rate'] or 0),
                'worksheets': worksheets,
            })

        # PDF generation options
        options = {
            'enable-local-file-access': True,
            'margin-top': '10mm',
            'margin-left': '10mm',
            'margin-right': '10mm',
            'margin-bottom': '10mm',
        }

        # Render the HTML template with the given context
        html_content = render_to_string('stats_export.html', context)

        # Create the HTTP response as a PDF file
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=report.pdf'

        try:
            # Convert the HTML to a PDF and write it to the response
            pdf = pdfkit.from_string(html_content, False, options=options)
            response.write(pdf)
        except Exception as e:
            response = HttpResponse(f"Error generating PDF: {str(e)}", status=500)

        return response
