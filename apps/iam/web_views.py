from django.contrib import messages
from django.conf import settings
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sessions.models import Session
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, TemplateView
from core.mixins import RoleAwareBaseTemplateMixin

from . import forms

User = get_user_model()


def _social_login_context():
    google_enabled = bool(
        settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
        and settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET
        and "<CHANGE_ME>" not in settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
        and "<CHANGE_ME>" not in settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET
    )
    facebook_enabled = bool(
        settings.SOCIAL_AUTH_FACEBOOK_KEY
        and settings.SOCIAL_AUTH_FACEBOOK_SECRET
        and "<CHANGE_ME>" not in settings.SOCIAL_AUTH_FACEBOOK_KEY
        and "<CHANGE_ME>" not in settings.SOCIAL_AUTH_FACEBOOK_SECRET
    )
    return {
        "social_google_enabled": google_enabled,
        "social_facebook_enabled": facebook_enabled,
        "social_login_enabled": google_enabled or facebook_enabled,
    }


class LoginView(FormView):
    """User login view."""

    template_name = "auth/login.html"
    form_class = forms.LoginForm
    success_url = reverse_lazy("core:dashboard")  # Changed from frontend:dashboard

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("core:dashboard")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(_social_login_context())
        return context

    def form_valid(self, form):
        remember_me = form.cleaned_data.get("remember_me")

        # AuthenticationForm already authenticated the user in its clean() method
        # We can access the authenticated user via form.get_user()
        user = form.get_user()

        # Check if user has OTP enabled
        if getattr(user, "otp_enabled", False):
            self.request.session["otp_user_id"] = user.id
            return redirect("iam:otp_verify")

        # Log the user in
        login(self.request, user)

        if not remember_me:
            self.request.session.set_expiry(0)

        messages.success(self.request, "Welcome back!")
        return super().form_valid(form)

    def form_invalid(self, form):
        # Add a user-friendly error message
        messages.error(self.request, "Invalid email or password.")
        return super().form_invalid(form)


class SignupView(FormView):
    """User registration view."""

    template_name = "auth/signup.html"
    form_class = forms.SignupForm
    success_url = reverse_lazy("iam:login")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("core:dashboard")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(_social_login_context())
        return context

    def form_valid(self, form):
        user = form.save(commit=False)
        user.username = form.cleaned_data["email"]
        user.save()

        # Create or update profile with additional data
        from iam.models import UserProfile

        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.first_name = form.cleaned_data.get("first_name", "")
        profile.last_name = form.cleaned_data.get("last_name", "")
        profile.save()

        messages.success(self.request, "Account created successfully! Please log in.")
        return super().form_valid(form)


class LogoutView(View):
    """User logout view."""

    def get(self, request):
        logout(request)
        messages.info(request, "You have been logged out.")
        return redirect("iam:login")

    def post(self, request):
        return self.get(request)


class OTPVerifyView(FormView):
    """OTP verification view."""

    template_name = "auth/otp_verify.html"
    form_class = forms.OTPVerifyForm
    success_url = reverse_lazy("core:dashboard")

    def dispatch(self, request, *args, **kwargs):
        if "otp_user_id" not in request.session:
            return redirect("iam:login")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user_id = self.request.session.get("otp_user_id")
        if not user_id:
            return redirect("iam:login")

        user = get_object_or_404(User, id=user_id)
        otp_code = form.cleaned_data.get("otp_code")

        try:
            from iam.services import otp  # Changed from apps.iam.services

            otp.validate_otp(user, otp_code)

            login(self.request, user)
            del self.request.session["otp_user_id"]
            messages.success(self.request, "Welcome back!")
            return super().form_valid(form)

        except Exception:
            messages.error(self.request, "Invalid OTP code. Please try again.")
            return self.form_invalid(form)


class PasswordResetView(FormView):
    """Password reset request view."""

    template_name = "auth/password_reset.html"
    form_class = forms.CustomPasswordResetForm
    success_url = reverse_lazy("iam:password_reset_done")

    def form_valid(self, form):
        form.save(request=self.request, email_template_name="auth/password_reset_email.html")
        return super().form_valid(form)


class PasswordResetDoneView(TemplateView):
    """Password reset email sent confirmation."""

    template_name = "auth/password_reset_done.html"


class PasswordResetConfirmView(LoginRequiredMixin, FormView):
    """
    Since we are using standard Django forms for this or need to handle the token link:
    Actually, Django's auth views are best for this complex token validation logic.
    Let's subclass Django's built-in views to keep it simple but use our templates.
    """

    pass


# Wait, mixing custom FormViews with Django's complex Reset views is tricky.
# The easiest path is to import Django's views directly in urls.py OR subclass them here.
# Let's subclass to set template_name.


class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = "auth/password_reset_confirm.html"
    success_url = reverse_lazy("iam:password_reset_complete")
    form_class = forms.CustomSetPasswordForm


class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = "auth/password_reset_complete.html"


class OTPEnableView(LoginRequiredMixin, FormView):
    """Enable OTP/2FA."""

    template_name = "auth/otp_setup.html"
    form_class = forms.OTPVerifyForm
    success_url = reverse_lazy("iam:settings_security")
    login_url = reverse_lazy("iam:login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Generate OTP secret if not already verifying
        from iam.services import otp

        if not self.request.user.otp_base32:
            otp.generate_otp(self.request.user)

        # Add qr code url to context
        context["otp_auth_url"] = self.request.user.otp_auth_url
        context["secret_key"] = self.request.user.otp_base32
        return context

    def form_valid(self, form):
        otp_code = form.cleaned_data.get("otp_code")
        try:
            from iam.services import otp

            otp.verify_otp(self.request.user, otp_code)
            messages.success(self.request, "Two-factor authentication enabled successfully!")
            return super().form_valid(form)
        except Exception:
            messages.error(self.request, "Invalid code. Please try again.")
            return self.form_invalid(form)


class OTPDisableView(LoginRequiredMixin, View):
    """Disable OTP/2FA."""

    login_url = reverse_lazy("iam:login")

    def post(self, request):
        from iam.services import otp

        otp.disable_otp(request.user)
        messages.info(request, "Two-factor authentication disabled.")
        return redirect("iam:settings_security")


class LogoutOtherSessionsView(LoginRequiredMixin, View):
    """Sign the current user out of all other active sessions."""

    login_url = reverse_lazy("iam:login")

    def post(self, request):
        current_session_key = request.session.session_key
        user_id = str(request.user.pk)
        revoked_session_keys = []

        active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
        if current_session_key:
            active_sessions = active_sessions.exclude(session_key=current_session_key)

        for session in active_sessions:
            if session.get_decoded().get("_auth_user_id") == user_id:
                revoked_session_keys.append(session.session_key)

        if revoked_session_keys:
            Session.objects.filter(session_key__in=revoked_session_keys).delete()
            messages.info(request, f"Signed out {len(revoked_session_keys)} other session(s).")
        else:
            messages.info(request, "No other active sessions were found.")

        return redirect("iam:settings_security")


class SettingsView(LoginRequiredMixin, RoleAwareBaseTemplateMixin, TemplateView):
    """User settings view."""

    template_name = "settings/index.html"
    login_url = reverse_lazy("iam:login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass user explicitly and profile as instance
        profile = getattr(self.request.user, "profile", None)
        if "profile_form" not in context:
            context["profile_form"] = forms.ProfileForm(user=self.request.user, instance=profile)
        if "password_form" not in context:
            context["password_form"] = forms.CustomPasswordChangeForm(user=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        form_type = request.POST.get("form_type")
        user = request.user
        profile = getattr(user, "profile", None)

        # Default forms (unbound)
        profile_form = forms.ProfileForm(user=user, instance=profile)
        password_form = forms.CustomPasswordChangeForm(user=user)

        if form_type == "profile":
            profile_form = forms.ProfileForm(request.POST, request.FILES, user=user, instance=profile)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Profile updated successfully!")
                return redirect("iam:settings")

        elif form_type == "password":
            password_form = forms.CustomPasswordChangeForm(user=user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                # Update session hash to prevent logout
                from django.contrib.auth import update_session_auth_hash

                update_session_auth_hash(request, password_form.user)
                messages.success(request, "Password changed successfully!")
                return redirect("iam:settings")

        # Render with errors
        context = self.get_context_data(**kwargs)
        context["profile_form"] = profile_form
        context["password_form"] = password_form
        return self.render_to_response(context)


class SecuritySettingsView(LoginRequiredMixin, RoleAwareBaseTemplateMixin, TemplateView):
    """Security settings (2FA)."""

    template_name = "settings/security.html"
    login_url = reverse_lazy("iam:login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["otp_enabled"] = getattr(self.request.user, "otp_enabled", False)
        context["otp_form"] = forms.OTPVerifyForm()
        return context
