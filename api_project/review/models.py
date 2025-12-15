from django.db import models

class Review(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    sentiment = models.CharField(max_length=10)  
    polarity = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
