from django.db import models

# Create your models here.


class Feedback(models.Model):
    """Model to store feedback from users"""

    # TODO: remove name field because feedback is anonymous or we can use email id for reference
    name = models.CharField(max_length=20)
    # TODO: make choice field with predefined and other as custom problem field
    problem = models.CharField(max_length=100)
    message = models.TextField(max_length=500)
    # rename this field to created at
    datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.problem
