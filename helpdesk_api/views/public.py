from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny


from helpdesk.models import Ticket, Queue
from helpdesk_api.serializers import PublicTicketSerializer
from helpdesk.lib import text_is_spam
from helpdesk.views.staff import update_ticket as staff_update_ticket

class PublicTicketViewSet(viewsets.ViewSet):
    """
    ViewSet for public ticket submission and view access.
    """
    permission_classes = [AllowAny]

    def create(self, request):
        # Handles public ticket submission
        serializer = PublicTicketSerializer(data=request.data)
        if serializer.is_valid():
            if text_is_spam(serializer.validated_data.get('body', ''), request):
                return Response({"error": "Submission flagged as spam."}, status=status.HTTP_400_BAD_REQUEST)
            ticket = serializer.save()
            return Response({
                "message": "Ticket submitted successfully.",
                "ticket": ticket.ticket_for_url,
                "email": ticket.submitter_email
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='view')
    def view_ticket(self, request):
        # Access ticket by public email and ticket ID
        ticket_req = request.GET.get('ticket', '')
        email = request.GET.get('email', '')
        if not (ticket_req and email):
            return Response({'error': 'Missing ticket or email'}, status=status.HTTP_400_BAD_REQUEST)

        queue, ticket_id = Ticket.queue_and_id_from_query(ticket_req)
        try:
            ticket = Ticket.objects.get(id=ticket_id, submitter_email__iexact=email)
        except Ticket.DoesNotExist:
            return Response({'error': 'Invalid ticket ID or email'}, status=status.HTTP_404_NOT_FOUND)

        data = PublicTicketSerializer(ticket).data
        return Response(data)

    @action(detail=False, methods=['post'], url_path='close')
    def close_ticket(self, request):
        ticket_req = request.data.get('ticket')
        email = request.data.get('email')
        if not (ticket_req and email):
            return Response({'error': 'Missing ticket or email'}, status=400)

        queue, ticket_id = Ticket.queue_and_id_from_query(ticket_req)
        try:
            ticket = Ticket.objects.get(id=ticket_id, submitter_email__iexact=email)
        except Ticket.DoesNotExist:
            return Response({'error': 'Invalid ticket or email'}, status=404)

        if ticket.status != Ticket.RESOLVED_STATUS:
            return Response({'error': 'Ticket is not resolved yet'}, status=400)

        request._full_data = request.data
        request.POST = {
            'new_status': Ticket.CLOSED_STATUS,
            'public': 1,
            'title': ticket.title,
            'comment': 'Submitter accepted resolution and closed ticket',
        }
        if ticket.assigned_to:
            request.POST['owner'] = ticket.assigned_to.id
        request.GET = {}

        return staff_update_ticket(request, ticket_id, public=True)