class RoleAwareBaseTemplateMixin:
    customer_base_template = "base_user.html"
    staff_base_template = "base_admin.html"

    def get_base_template(self):
        user = getattr(self.request, "user", None)
        if user and user.is_authenticated and user.is_staff:
            return self.staff_base_template
        return self.customer_base_template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("base_template", self.get_base_template())
        return context