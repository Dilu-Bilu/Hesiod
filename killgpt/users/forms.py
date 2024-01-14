from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django.contrib.auth import forms as admin_forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django import forms 

User = get_user_model()


class UserAdminChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):
        model = User


class UserAdminCreationForm(admin_forms.UserCreationForm):
    """
    Form for User Creation in the Admin Area.
    To change user signup, see UserSignupForm and UserSocialSignupForm.
    """

    class Meta(admin_forms.UserCreationForm.Meta):
        model = User

        error_messages = {
            "username": {"unique": _("This username has already been taken.")}
        }




class EmailInputWithStyle(forms.widgets.TextInput):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs.update({
            'style': 'background-color: #231250; font-size: 15px; border-color: magenta;',
            'class': 'form-control py-3 text-white',
            'placeholder': 'Email Address'
        })

class EmailSignupForm(forms.Form):
    email = forms.EmailField(widget=EmailInputWithStyle)
class PasswordInputWithStyle(forms.widgets.PasswordInput):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs.update({
            'style': 'background-color: #231250; font-size: 15px; border-color: magenta;',
            'class': 'form-control py-3 text-white',
            'placeholder': 'Add A Password',
            'label': ''  # Set label to an empty string to remove it
        })

class PasswordSignupForm(forms.Form):
    email = forms.EmailField(widget=EmailInputWithStyle)
    password = forms.CharField(widget=PasswordInputWithStyle)
    
    
class UserSignupForm(SignupForm):
    """
    Form that will be rendered on a user sign up section/screen.
    Default fields will be added automatically.
    Check UserSocialSignupForm for accounts created from social.
    """


class UserSocialSignupForm(SocialSignupForm):
    """
    Renders the form when user has signed up using social accounts.
    Default fields will be added automatically.
    See UserSignupForm otherwise.
    """
