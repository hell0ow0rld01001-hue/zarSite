from django.views.generic import ListView, DetailView, View , FormView
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.urls import reverse_lazy ,reverse  # new
from .models import Articles
from .forms import CommentForm


class ArticleListView(ListView):
    model = Articles
    template_name = "article_list.html"


class CommentGet(DetailView):  # new
    model = Articles
    template_name = "article_detail.html"

    def get_context_data(self, **kwargs):  # new
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm()
        return context


class CommentPost(SingleObjectMixin, FormView):

    model = Articles
    form_class = CommentForm
    template_name = "article_detail.html"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.article = self.object
        comment.author = self.request.user
        comment.save()
        return super().form_valid(form)


    def get_success_url(self):
        article = self.object
        return reverse("article_detail", kwargs={"pk": article.pk})


class ArticleDetailView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        view = CommentGet.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = CommentPost.as_view()
        return view(request, *args, **kwargs)


class ArticleUpdateView(UpdateView):
    model = Articles
    fields = (
        "title",
        "body",
    )

    template_name = "article_edit.html"

    def test_func(self):
        return self.request.user.is_staff


class ArticleDeleteView(DeleteView):  # new
    model = Articles
    template_name = "article_delete.html"
    success_url = reverse_lazy("article_list")

    def test_func(self):
        return self.request.user.is_staff


class ArticleCreateView(CreateView):
    model = Articles
    fields = (
        "title",
        "body",
        "author",
    )
    template_name = "article_create.html"
    success_url = reverse_lazy("article_list")

    def test_func(self):
        return self.request.user.is_staff
