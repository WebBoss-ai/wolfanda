from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from blog.forms import CommentForm
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.shortcuts import redirect
from .models import Post, Comment
from django.urls import reverse

def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'blog/home.html', context)

def main_home(request):
    return render(request,'home/index.html')


class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 7


class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    slug_field = "slug"
    count_hit = True
    form = CommentForm
    def post(self, request, *args, **kwargs):
        post = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            return redirect('post-detail', pk=post.pk)
        else:
            return render(request, self.template_name, {'object': post, 'form': form})

    def get_context_data(self, **kwargs):
        post = self.get_object()
        post_comments_count = Comment.objects.filter(post=post).count()
        post_comments = Comment.objects.filter(post=post)
        context = super().get_context_data(**kwargs)
        context.update({
            'form': CommentForm(),
            'post_comments': post_comments,
            'post_comments_count': post_comments_count,
        })

        if self.request.user.is_authenticated:
            context['user_liked'] = post.likes.filter(id=self.request.user.id).exists()

        return context

def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        if request.user.is_authenticated:
            post.likes.add(request.user)
    return redirect('post-detail', pk=pk)

def unlike_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        if request.user.is_authenticated:
            post.likes.remove(request.user)
    return redirect('post-detail', pk=pk)

    # def get_like_data(self, **kwargs):
    #     post_likes_count = Like.objects.all().filter(post=self.object.id).count()
    #     post_likes = Like.objects.all().filter(post=self.object.id)
    #     context = super().get_like_data(**kwargs)
    #     context.update({
    #         'form': self.form,
    #         'post_likes': post_likes,
    #         'post_likes_count': post_likes_count,
    #     })
    #     return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})
