from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from collections import defaultdict
from .models import Post, Comment
import json

def post_list(request):
    posts = Post.objects.prefetch_related('comments').all().order_by("-created_at")
    # Get comment counts for each post (prefetched comments are cached)
    for post in posts:
        post.comment_count = len(post.comments.all())
    return render(request, "blog/post_list.html", {"posts": posts})

def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        author = request.POST.get('author')
        content = request.POST.get('content')
        if author and content:
            Comment.objects.create(post=post, author=author, content=content)
            messages.success(request, 'Comment added successfully!')
    return redirect('post_list')

def analytics(request):
    # Total statistics
    total_posts = Post.objects.count()
    total_comments = Comment.objects.count()
    avg_comments_per_post = total_comments / total_posts if total_posts > 0 else 0
    
    # Posts over time (last 12 months)
    now = timezone.now()
    posts_over_time = []
    labels_over_time = []
    for i in range(11, -1, -1):
        month_start = (now - timedelta(days=30*i)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        count = Post.objects.filter(created_at__gte=month_start, created_at__lte=month_end).count()
        posts_over_time.append(count)
        labels_over_time.append(month_start.strftime('%Y-%m'))
    
    # Comments per post
    posts_with_comments = Post.objects.annotate(comment_count=Count('comments')).order_by('-comment_count')[:10]
    post_titles = [post.title[:20] + '...' if len(post.title) > 20 else post.title for post in posts_with_comments]
    comment_counts = [post.comment_count for post in posts_with_comments]
    
    # Posts by month (all time)
    all_posts = Post.objects.all().order_by('created_at')
    monthly_posts = defaultdict(int)
    for post in all_posts:
        month_key = post.created_at.strftime('%Y-%m')
        monthly_posts[month_key] += 1
    
    sorted_months = sorted(monthly_posts.keys())
    monthly_labels = sorted_months
    monthly_counts = [monthly_posts[month] for month in sorted_months]
    
    # Post content length statistics
    post_lengths = [len(post.content) for post in Post.objects.all()]
    avg_length = sum(post_lengths) / len(post_lengths) if post_lengths else 0
    
    context = {
        'total_posts': total_posts,
        'total_comments': total_comments,
        'avg_comments_per_post': round(avg_comments_per_post, 2),
        'avg_post_length': round(avg_length, 0),
        'posts_over_time': json.dumps(posts_over_time),
        'labels_over_time': json.dumps(labels_over_time),
        'post_titles': json.dumps(post_titles),
        'comment_counts': json.dumps(comment_counts),
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_counts': json.dumps(monthly_counts),
    }
    
    return render(request, "blog/analytics.html", context)
