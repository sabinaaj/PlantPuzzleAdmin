from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from worksheets.models import Worksheet, Question, Option
from .models import Visitor, SchoolGroup, SuccessRate, VisitorResponse
from .serializers import VisitorSerializer, SchoolGroupSerializer


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

        return Response({"message": "Results saved successfully."}, status=status.HTTP_201_CREATED)


