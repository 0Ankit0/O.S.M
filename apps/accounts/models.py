from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models


postal_code_validator = RegexValidator(
    regex=r"^[A-Za-z0-9\- ]{3,12}$",
    message="Enter a valid postal code.",
)


class AccountAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="account_addresses")
    label = models.CharField(max_length=32, blank=True, default="")
    line1 = models.CharField(max_length=128)
    line2 = models.CharField(max_length=128, blank=True, default="")
    city = models.CharField(max_length=64)
    state = models.CharField(max_length=64, blank=True, default="")
    postal_code = models.CharField(max_length=12, validators=[postal_code_validator])
    country = models.CharField(max_length=2, default="US")
    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.line1}, {self.city}"
