from django.shortcuts import render
import os
import requests
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import models
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from killgpt.users.models import User
from .models import Assignment
from django.core.mail import send_mail
from django.db.models import Avg, F
from django.db import models
from djstripe.models import Product

def PriceView(request):
    return render(request, 'steps/three.html', {
        'products': Product.objects.all()
    })
class AssignmentListView(ListView):
    model = Assignment
    context_object_name = "Assignments"
    template_name = "assignment/assignment_list.html"
    ordering = ["-date_created"]
    paginate_by = 8
    
    def get_queryset(self):
        # Get the currently signed-in user
        user = self.request.user

        # Filter assignments by the currently signed-in user
        return Assignment.objects.filter(user=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the currently signed-in user
        user = self.request.user

        # Update the context with the monthly detector and assignment usage
        context['monthly_detector_usage'] = user.monthly_detector_usage
        context['monthly_assignment_usage'] = user.monthly_assignment_usage
        context['total_assignments_created'] = user.total_assignments_created
        context['average_assignment_percentage'] = round(user.average_assignment_percentage)
   
        return context
class AssignmentDetailView(DetailView):
    model = Assignment
    template_name = 'assignment/assignment_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import CustomAssignmentForm

from django.core.exceptions import PermissionDenied
from datetime import datetime
from openai import OpenAI
import re
from config.settings.base import OPEN_AI_KEY
def get_assignment_feedback():
    
    client = OpenAI(api_key=OPEN_AI_KEY)
    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
    {"role": "system", "content": """You are a teaching assistant, skilled in editing assignments in order to make them more engaging, thought provoking, easy to mark, and less prone to students cheating through creating the whole assignment by using ChatGPT. The last part is the top most priority as teachers don't want students to completely plagiarize their assignments
     ."""},
    {"role": "user", "content": f"""You are an AI assistant helping an English teacher modernize a current assignment for their high school class. The teacher wants to incorporate ChatGPT (like me) into the assignment to enhance students' learning and writing processes. The assignment revolves around analyzing a chosen piece of literature for themes and character development. The teacher wishes to modernize this assignment by leveraging ChatGPT's capabilities in a way that encourages critical thinking and deeper analysis. Generate an innovative assignment idea that integrates ChatGPT effectively, providing students with a unique and insightful approach to analyzing literature while emphasizing the ethical use of AI in education
        """}
        ]
        )
    response = completion.choices[0].message
    txt = response.content

    return txt
class AssignmentCreateView(LoginRequiredMixin, CreateView):
    model = Assignment
    form_class = CustomAssignmentForm
    context_object_name = "Assignment"

    def form_valid(self, form):
        # Get the user
        user = self.request.user

        # Check the monthly usage limit (e.g., 10 assignments per month)
        now = datetime.now()
        current_month = now.month

        # Calculate the user's monthly usage for assignments
        user_monthly_usage = user.monthly_assignment_usage
        if user.last_assignment_usage_update:
            if user.last_assignment_usage_update.month != current_month:
                user_monthly_usage = 1
            else:
                user_monthly_usage += 1

        # Define the monthly usage limit
        monthly_limit = 10

        if user_monthly_usage > monthly_limit:
            # If the usage limit is exceeded, raise a PermissionDenied exception
            raise PermissionDenied("Monthly assignment usage limit exceeded")

        form.instance.user = user
        result = super().form_valid(form)

        # Call the update_user_fields method to update user-related fields
        self.object.update_user_fields()
        criteria_text = form.cleaned_data.get('assignment_criteria', None)

        # if criteria_text:
        #     # If 'criteria' field has a value, do something with it
        #     # For example, you can assign it to the 'feedback' field
        #     self.object.feedback = get_assignment_feedback()  # Modify as needed
        #     self.object.save()
        return result

    def get_success_url(self):
        return reverse('assignment-detail', kwargs={'pk': self.object.pk})


class AssignmentUpdateView(UserPassesTestMixin, LoginRequiredMixin, UpdateView):
    model = Assignment
    fields = ["title", "content"]

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def test_func(self):
        Assignments = self.get_object()
        if self.request.user == Assignments.user:
            return True
        return False


class AssignmentDeleteView(UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    model = Assignment
    context_object_name = "Assignment"
    success_url = "/"

    def test_func(self):
        Assignments = self.get_object()
        if self.request.user == Assignments.user:
            return True
        return False