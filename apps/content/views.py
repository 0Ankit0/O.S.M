from pathlib import Path

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView
from core.mixins import RoleAwareBaseTemplateMixin

from . import forms, models


class DocumentListView(LoginRequiredMixin, RoleAwareBaseTemplateMixin, ListView):
    """List user's documents."""
    template_name = 'content/documents/list.html'
    context_object_name = 'documents'
    login_url = reverse_lazy('iam:login')

    def get_queryset(self):
        return models.Document.objects.filter(
            user=self.request.user
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['upload_form'] = forms.DocumentUploadForm()
        return context


class DocumentUploadView(LoginRequiredMixin, RoleAwareBaseTemplateMixin, FormView):
    """Upload a document."""
    template_name = 'content/documents/upload.html'
    form_class = forms.DocumentUploadForm
    success_url = reverse_lazy('content:documents_list')
    login_url = reverse_lazy('iam:login')

    def form_valid(self, form):
        uploaded_file = form.cleaned_data['file']
        document = models.Document.objects.create(
            user=self.request.user,
            title=form.cleaned_data.get('title') or Path(uploaded_file.name).stem,
            file=uploaded_file,
        )

        messages.success(self.request, 'Document uploaded successfully!')

        if self.request.headers.get('HX-Request'):
            return render(self.request, 'content/documents/partials/document_item.html', {
                'document': document
            })

        return super().form_valid(form)


@login_required
def document_delete(request, pk):
    """Delete a document."""
    document = get_object_or_404(
        models.Document, pk=pk, user=request.user
    )
    document.delete()

    messages.success(request, 'Document deleted.')

    if request.headers.get('HX-Request'):
        return HttpResponse('')

    return redirect('content:documents_list')


class ProductListView(LoginRequiredMixin, RoleAwareBaseTemplateMixin, ListView):
    """List products (CMS items)."""
    template_name = 'content/products/list.html'
    context_object_name = 'products'
    paginate_by = 12
    login_url = reverse_lazy('iam:login')

    def get_queryset(self):
        # Fetch published product items
        return models.ContentItem.objects.filter(
            content_type='product',
            is_published=True
        ).order_by('-created_at')


class ProductCreateView(LoginRequiredMixin, RoleAwareBaseTemplateMixin, FormView):
    """Create a new product."""
    template_name = 'content/products/form.html'
    form_class = forms.ProductCreateForm
    success_url = reverse_lazy('content:products_list')
    login_url = reverse_lazy('iam:login')

    def form_valid(self, form):
        # Create ContentItem for the product
        product_data = {
            'title': form.cleaned_data['title'],
            'price': float(form.cleaned_data['price']),
            'description': form.cleaned_data['description'],
            'image': form.cleaned_data['image'],
        }

        models.ContentItem.objects.create(
            content_type='product',
            external_id=f"product-{models.ContentItem.objects.count() + 1}", # Simple ID generation
            fields=product_data,
            is_published=True
        )

        messages.success(self.request, 'Product created successfully!')
        return super().form_valid(form)

