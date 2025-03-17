from django.db.models import Avg, Exists, OuterRef
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.timezone import now, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from worksheets.models import Worksheet, Question, Option
from areas.models import Area
from .models import Visitor, SchoolGroup, SuccessRate, VisitorResponse
from .serializers import VisitorSerializer, SchoolGroupSerializer


class StatsPageView(LoginRequiredMixin, TemplateView):
    template_name = 'stats_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['areas'] = Area.objects.filter(
            Exists(Worksheet.objects.filter(area=OuterRef('pk'), successrate__isnull=False))
        ).prefetch_related('worksheet_set')

        context['visitors_cnt'] = Visitor.objects.count()
        context['done_cnt'] = SuccessRate.objects.count()
        context['avg_rate'] = int(SuccessRate.objects.all().aggregate(rate=Avg('rate'))['rate'] or 0)
        return context


class FetchStatsAjaxView(View):
    def get(self, request):
        time_range = request.GET.get('range', 'all')

        if time_range == 'today':
            start_date = now().replace(hour=0, minute=0, second=0)
        elif time_range == 'week':
            start_date = now() - timedelta(days=7)
        elif time_range == 'month':
            start_date = now() - timedelta(days=30)
        else:
            start_date = None

        data = {}

        areas = Area.objects.all().prefetch_related('worksheet_set')
        if start_date:
            success_rates = SuccessRate.objects.filter(created_at__gte=start_date)
        else:
            success_rates = SuccessRate.objects.all()


        for area in areas:

            worksheets = area.worksheet_set.all()
            done_cnt = success_rates.filter(worksheet__in=worksheets).count()
            avg_rate = success_rates.filter(worksheet__in=worksheets).aggregate(rate=Avg('rate'))['rate'] or 0

            worksheet_success_rates = []
            worksheet_labels = []
            worksheet_data = {}
            for worksheet in worksheets:

                worksheet_done_cnt = success_rates.filter(worksheet=worksheet).count()
                worksheet_avg_rate = int(success_rates.filter(worksheet=worksheet).aggregate(rate=Avg('rate'))['rate'] or 0)

                tasks = worksheet.task_set.all()

                tasks_success_rates = []
                for task in tasks:
                    questions = task.question_set.all()

                    if start_date:
                        responses = VisitorResponse.objects.filter(
                            created_at__gte=start_date,
                            question__in=questions
                        )
                    else:
                        responses = VisitorResponse.objects.filter(
                            question__in=questions
                        )

                    responses_cnt = responses.count()
                    correct_responses_count = responses.filter(is_correct=True).count()
                    responses_avg_rate = int((correct_responses_count / responses_cnt) * 100 if responses_cnt else 0)

                    tasks_success_rates.append(responses_avg_rate)



                worksheet_success_rates.append(worksheet_avg_rate)
                worksheet_labels.append(worksheet.title)
                worksheet_data[worksheet.pk] = {
                    'done_cnt': worksheet_done_cnt,
                    'avg_rate': worksheet_avg_rate,
                    'tasks_success_rates': tasks_success_rates
                }

            data[area.pk] = {
                'done_cnt': done_cnt,
                'avg_rate': int(avg_rate),
                'worksheet_success_rates': worksheet_success_rates,
                'worksheet_labels': worksheet_labels,
                'worksheet_data': worksheet_data
            }

        return JsonResponse({ 'data': data })


class VisitorView(APIView):

    def get(self, request, visitor_id):
        visitor = Visitor.objects.filter(pk=visitor_id).first()
        if not visitor:
            return Response({'detail': 'No visitor found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = VisitorSerializer(visitor, context={'request': request})
        return Response(serializer.data)


class VisitorCreateView(APIView):

    def post(self, request):
        serializer = VisitorSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            visitor_pk = serializer.instance.pk

            return Response({'visitor_id': visitor_pk}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VisitorUpdateView(APIView):

    def put(self, request, visitor_id):
        visitor = Visitor.objects.filter(pk=visitor_id).first()
        if not visitor:
            return Response({'detail': 'No visitor found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = VisitorSerializer(visitor, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SchoolGroupsView(APIView):

    def get(self, request):
        queryset = SchoolGroup.objects.all()
        serializer = SchoolGroupSerializer(queryset, many=True)
        return Response(serializer.data)


class SubmitResultsView(APIView):

    def post(self, request, visitor_id):
        visitor = get_object_or_404(Visitor, id=visitor_id)
        data = request.data

        if not data:
            return Response({'detail': 'No data provided.'}, status=status.HTTP_400_BAD_REQUEST)

        for result in data:

            success_rate = result['success_rate']
            worksheet = get_object_or_404(Worksheet, id=success_rate['worksheet'])

            # Create SuccessRate
            SuccessRate.objects.create(
                rate=success_rate['rate'],
                worksheet=worksheet,
                visitor=visitor,
                created_at=result['created_at']
            )

            # Create VisitorResponse
            for response_data in result['responses']:
                question = get_object_or_404(Question, id=response_data['question'])

                visitor_response = VisitorResponse.objects.create(
                    visitor=visitor,
                    question=question,
                    is_correct=response_data.get('is_correct', False),
                    created_at=result['created_at']
                )

                options = Option.objects.filter(id__in=response_data['options'])
                visitor_response.options.set(options)
                visitor_response.save()

        # Create Score
        score = 0
        latest_rates = (SuccessRate.objects.filter(visitor=visitor)
                        .order_by('worksheet', 'visitor', '-created_at')
                        .distinct('worksheet', 'visitor'))
        for success_rate in latest_rates:
            score += success_rate.rate

        visitor.score = score
        visitor.save()

        return Response({"message": "Results saved successfully."}, status=status.HTTP_201_CREATED)


class BetterThanView(APIView):

    def get(self, request, visitor_id):
        visitor = Visitor.objects.filter(pk=visitor_id).first()
        if not visitor:
            return Response({'detail': 'No visitor found.'}, status=status.HTTP_404_NOT_FOUND)

        visitors = Visitor.objects.filter(score__gt=0).all()
        if len(visitors) < 5:
            return Response({'detail': 'Not enough visitors.'}, status=status.HTTP_404_NOT_FOUND)

        scores = sorted(visitors.values_list('score', flat=True))
        lower_scores_count = sum(1 for s in scores if s < visitor.score)

        percentile = (lower_scores_count / len(scores)) * 100

        return Response({'better_than': percentile}, status=status.HTTP_200_OK)
