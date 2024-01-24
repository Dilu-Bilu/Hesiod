from django.db import models
from killgpt.users.models import User
from django.utils import timezone
from django.urls import reverse
import openai
from django.db.models import F, Avg
# Create your models here.
class Assignment(models.Model):
    ASSIGNMENT_TYPES = [
        ('essay', 'Essay'),
        ('presentation', 'Presentation'),
    ]
    SUBJECT_TYPES = [
        ('english', 'English'),
        ('history', 'History'),
    ]


    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    assignment_title = models.CharField(max_length=100, null=True)
    assignment_description = models.TextField(null=True)
    assignment_criteria = models.TextField(null=True)
    total_marks = models.IntegerField(null=True)
    date_created = models.DateTimeField(default=timezone.now)
    subject = models.CharField(max_length=20, choices=SUBJECT_TYPES, null=True)  # Replace with your model
    percent_of_cheating_students = models.IntegerField(null=True, default=0)
    feedback = models.TextField(blank=True)  # New field for storing feedback

        
    def update_user_fields(self):
        user = self.user
        user.total_assignments_created = F('total_assignments_created') + 1
        user.average_assignment_percentage = Assignment.objects.filter(user=user).aggregate(avg_percentage=Avg('percent_of_cheating_students'))['avg_percentage']
        user.save()

    def save(self, *args, **kwargs):
        created = not self.pk  # Check if the assignment is being created (not updated)
        super().save(*args, **kwargs)

        if created:
            # If this is a new assignment, update the related user's fields
            self.update_user_fields()
        ###### The FEATURE FOR ASSIGNMENT FEEDBACK IS DISABLED 
        # if not self.pk:  # Only generate feedback if the assignment is being created
        #     try: 
        #         input_text = f"Assignment: {self.title}\nDescription: {self.assignment_description}\n"  # Add other details
                
        #         openai.api_key = "YOUR_OPENAI_API_KEY"
        #         response = openai.Completion.create(
        #             engine="text-davinci-003",
        #             prompt=input_text,
        #             temperature=0.7,
        #             max_tokens=150,
        #             stop=None
        #         )
                
        #         self.feedback = response.choices[0].text.strip()
        #     except:
        #         self.feedback = 'Here is some feedback as the main OpenAI plugin is not yet created or implemented yet.'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.assignment_title

    def get_absolute_url(self):
        return reverse("assignment-detail", kwargs={"pk": self.pk})

    # def total_likes(self):
    #     return self.likes.count()

    # def total_comments(self):
    #     return self.Comment.count()
    # def comment_number(self):
    #     results = Comment.objects.filter(question=self).count()
    #     print(results)
    #     return results

class Example_Text(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    text = models.TextField(null=True)
    marks = models.IntegerField()
    comments = models.TextField(null=True)

    def __str__(self):
        return self.assignment

