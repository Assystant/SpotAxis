from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from helpdesk.models import KBCategory, KBItem
from rest_framework.permissions import IsAuthenticatedOrReadOnly


from helpdesk_api.serializers import KBCategorySerializer, KBItemSerializer


class KBCategoryViewSet(viewsets.ModelViewSet):
    queryset = KBCategory.objects.all()
    serializer_class = KBCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class KBItemViewSet(viewsets.ModelViewSet):
    queryset = KBItem.objects.all()
    serializer_class = KBItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=["post"])
    def vote(self, request, pk=None):
        item = get_object_or_404(KBItem, pk=pk)
        vote = request.data.get("vote")

        if vote not in ("up", "down"):
            return Response({"error": "Invalid vote. Use 'up' or 'down'."}, status=400)

        item.votes += 1
        if vote == "up":
            item.recommendations += 1
        item.save()

        return Response({
            "message": "Vote recorded.",
            "votes": item.votes,
            "recommendations": item.recommendations
        })
