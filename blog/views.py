from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import BlogPost, BlogCategory, Comment
from .forms import BlogPostForm, CommentForm, BlogCategoryForm
from django.utils import timezone
from django.http import JsonResponse

def blog_list(request):
    query = request.GET.get('q')
    category = request.GET.get('category')
    
    # Base queryset - only show published posts
    posts = BlogPost.objects.filter(status='published').order_by('-published_at')
    
    # If user is authenticated, show their own draft posts
    if request.user.is_authenticated and (request.user.role in ['teacher', 'admin']):
        posts = BlogPost.objects.filter(
            Q(status='published') |
            (Q(status='draft') & Q(author=request.user))
        ).order_by('-published_at')
    
    # Apply search filters
    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(excerpt__icontains=query)
        )
    
    # Apply category filter
    if category:
        posts = posts.filter(categories__slug=category)
    
    # Pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all categories for the sidebar
    categories = BlogCategory.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'selected_category': category,
        'can_create_post': request.user.is_authenticated and request.user.role in ['teacher', 'admin']
    }
    return render(request, 'blog/blog_list.html', context)

def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, status='published')
    comments = post.comments.filter(parent=None, is_approved=True).order_by('-created_at')
    
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.author = request.user
            parent_id = request.POST.get('parent')
            if parent_id:
                parent_comment = Comment.objects.get(id=parent_id)
                new_comment.parent = parent_comment
            new_comment.save()
            messages.success(request, 'Your comment has been posted.')
            return redirect('blog:blog_detail', slug=post.slug)
    else:
        comment_form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'blog/blog_detail.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def post_list(request):
    posts = BlogPost.objects.all().order_by('-created_at')
    return render(request, 'blog/admin/post_list.html', {
        'posts': posts
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def create_post(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Blog post created successfully.')
            return redirect('blog:blog_detail', slug=post.slug)
    else:
        form = BlogPostForm()
    return render(request, 'blog/admin/create_post.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def edit_post(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Blog post updated successfully.')
            return redirect('blog:blog_detail', slug=post.slug)
    else:
        form = BlogPostForm(instance=post)
    return render(request, 'blog/admin/edit_post.html', {
        'form': form,
        'post': post
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_post(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Blog post deleted successfully.')
        return redirect('blog:post_list')
    return render(request, 'blog/admin/delete_post.html', {'post': post})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def category_list(request):
    categories = BlogCategory.objects.all()
    return render(request, 'blog/admin/category_list.html', {
        'categories': categories
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def create_category(request):
    if request.method == 'POST':
        form = BlogCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully.')
            return redirect('blog:category_list')
    else:
        form = BlogCategoryForm()
    return render(request, 'blog/admin/create_category.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def edit_category(request, slug):
    category = get_object_or_404(BlogCategory, slug=slug)
    if request.method == 'POST':
        form = BlogCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('blog:category_list')
    else:
        form = BlogCategoryForm(instance=category)
    return render(request, 'blog/admin/edit_category.html', {
        'form': form,
        'category': category
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_category(request, slug):
    category = get_object_or_404(BlogCategory, slug=slug)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully.')
        return redirect('blog:category_list')
    return render(request, 'blog/admin/delete_category.html', {'category': category})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def comment_list(request):
    comments = Comment.objects.all().order_by('-created_at')
    return render(request, 'blog/admin/comment_list.html', {
        'comments': comments
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Comment deleted successfully.')
        return redirect('blog:comment_list')
    return render(request, 'blog/admin/delete_comment.html', {'comment': comment})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def approve_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    comment.is_approved = True
    comment.save()
    messages.success(request, 'Comment approved successfully.')
    return redirect('blog:comment_list')
