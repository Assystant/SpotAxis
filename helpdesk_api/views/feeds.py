from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.decorators import action

from helpdesk.models import Ticket, FollowUp, Queue
from helpdesk_api.serializers import TicketSerializer, FollowUpSerializer, QueueSerializer

User = get_user_model()

class OpenTicketsByUserViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        username = self.request.query_params.get('username')
        queue_slug = self.request.query_params.get('queue')
        user = get_object_or_404(User, username=username)

        queryset = Ticket.objects.filter(
            assigned_to=user,
            status__in=[Ticket.OPEN_STATUS, Ticket.REOPENED_STATUS]
        )

        if queue_slug:
            queue = get_object_or_404(Queue, slug=queue_slug)
            queryset = queryset.filter(queue=queue)

        return queryset


class UnassignedTicketsViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Ticket.objects.filter(
            assigned_to__isnull=True,
            status__in=[Ticket.OPEN_STATUS, Ticket.REOPENED_STATUS]
        )


class RecentFollowUpsViewSet(viewsets.ModelViewSet):
    serializer_class = FollowUpSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return FollowUp.objects.order_by('-date')[:20]


class OpenTicketsByQueueViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queue_slug = self.request.query_params.get('queue')
        queue = get_object_or_404(Queue, slug=queue_slug)
        return Ticket.objects.filter(
            queue=queue,
            status__in=[Ticket.OPEN_STATUS, Ticket.REOPENED_STATUS]
        )