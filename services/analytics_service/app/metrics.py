from prometheus_client import Counter, Histogram, Gauge
import time

# User metrics
user_registrations = Counter(
    'user_registrations_total',
    'Total number of user registrations'
)

active_users = Gauge(
    'active_users',
    'Number of currently active users'
)

# Post metrics
posts_created = Counter(
    'posts_created_total',
    'Total number of posts created',
    ['post_type']  # image, video, text
)

post_views = Counter(
    'post_views_total',
    'Total number of post views'
)

# Engagement metrics
likes_total = Counter(
    'likes_total',
    'Total number of likes',
    ['content_type']  # post, comment
)

comments_total = Counter(
    'comments_total',
    'Total number of comments'
)

# Performance metrics
request_latency = Histogram(
    'request_latency_seconds',
    'Request latency in seconds',
    ['endpoint', 'method']
)

error_count = Counter(
    'error_count_total',
    'Total number of errors',
    ['service', 'error_type']
)

# System metrics
db_connection_pool = Gauge(
    'db_connection_pool_size',
    'Current size of the database connection pool'
)

class MetricsMiddleware:
    async def __call__(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        
        request_latency.labels(
            endpoint=request.url.path,
            method=request.method
        ).observe(duration)
        
        return response 