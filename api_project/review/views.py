from rest_framework import viewsets
from .models import Review
from .serializers import ReviewSerializer

class ReviewViewSet(viewsets.ModelViewSet):  # permet GET, POST, etc.
    queryset = Review.objects.all().order_by('-created_at')
    serializer_class = ReviewSerializer
