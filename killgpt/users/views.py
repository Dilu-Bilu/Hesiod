from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView
from .forms import EmailSignupForm, PasswordSignupForm
from django.contrib import messages
from django.http import HttpResponseRedirect
User = get_user_model()

from django.contrib.auth.decorators import login_required
from django.urls import reverse

from djstripe.settings import djstripe_settings
from djstripe.models import Subscription

import stripe

def profile_view(request):
    return render(request, 'steps/profile.html',)


@login_required
def subscription_confirm(request):
    # set our stripe keys up
    stripe.api_key = djstripe_settings.STRIPE_SECRET_KEY

    # get the session id from the URL and retrieve the session object from Stripe
    session_id = request.GET.get("session_id")
    session = stripe.checkout.Session.retrieve(session_id)

    # get the subscribing user from the client_reference_id we passed in above
    client_reference_id = int(session.client_reference_id)
    subscription_holder = get_user_model().objects.get(id=client_reference_id)
    # sanity check that the logged in user is the one being updated
    assert subscription_holder == request.user

    # get the subscription object form Stripe and sync to djstripe
    subscription = stripe.Subscription.retrieve(session.subscription)
    djstripe_subscription = Subscription.sync_from_stripe_data(subscription)

    # set the subscription and customer on our user
    subscription_holder.subscription = djstripe_subscription
    subscription_holder.customer = djstripe_subscription.customer
    subscription_holder.save()

    # show a message to the user and redirect
    messages.success(request, f"You've successfully signed up. Thanks for the support!")
    return HttpResponseRedirect(reverse("assignment-list"))

from django.shortcuts import render, redirect
from .forms import UserSignupForm  # Import your forms

def step_one_signup_teacher(request):
    if request.method == 'POST':
        form = EmailSignupForm(request.POST)
        if form.is_valid():
            # Save email in session or temporary storage
            request.session['signup_email'] = form.cleaned_data['email']
            return redirect('step-1')  # Redirect to the password step
            
    else:
        form = EmailSignupForm(request.POST)
    
    return render(request, 'pages/teacher.html', {'form': form})

def step_one_signup_student(request):
    if request.method == 'POST':
        form = EmailSignupForm(request.POST)
        if form.is_valid():
            # Save email in session or temporary storage
            request.session['signup_email'] = form.cleaned_data['email']
            return redirect('step-1')  # Redirect to the password step
            
    else:
        form = EmailSignupForm(request.POST)
    
    return render(request, 'pages/student.html', {'form': form})


from django.contrib.auth import authenticate, login

def step_two_signup(request):
    if 'signup_email' not in request.session:
        return redirect('signup_email')  # Redirect to email step if email is not available

    if request.method == 'POST':
        form = PasswordSignupForm(request.POST)
        if form.is_valid():
            email = request.session.get('signup_email')
            password = form.cleaned_data['password']
            
            # Create the user with the collected email and password
            user = User.objects.create_user(email=email, password=password, username=email)
            
            # Authenticate the user
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                # Log in the user
                login(request, user)
                return redirect('step-2')  # Redirect to success page or any desired page
            else:
                # Handle the case where authentication fails
                # You might want to add an error message or redirect to a login page
                return render(request, 'login_error.html')
    else:
        try:
            email = request.session.get('signup_email')
        except:
            email = ""

        form = PasswordSignupForm(initial={'email': email})
        

    return render(request, 'steps/one.html', {'form': form, 'email': email})
class UserDetailView(LoginRequiredMixin, DetailView):

    model = User
    slug_field = "email"
    slug_url_kwarg = "email"


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):

    model = User
    fields = ["name"]
    success_message = _("Information successfully updated")

    def get_success_url(self):
        assert (
            self.request.user.is_authenticated
        )  # for mypy to know that the user is authenticated
        return self.request.user.get_absolute_url()

    def get_object(self):
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):

    permanent = False

    def get_redirect_url(self):
        return reverse("home")


user_redirect_view = UserRedirectView.as_view()
