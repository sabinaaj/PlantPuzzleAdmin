from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Visitor, SchoolGroup
from .serializers import VisitorSerializer, SchoolGroupSerializer, \
    VisitorResponseSerializer, SuccessRateSerializer


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


class SubmitResponsesView(APIView):

    def post(self, request):
        serializer = VisitorResponseSerializer(data=request.data['responses'], many=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Responses submitted successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubmitSuccessRateView(APIView):

    def post(self, request):
        serializer = SuccessRateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Success rate submitted successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

