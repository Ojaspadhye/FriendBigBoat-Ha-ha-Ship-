import redis

r = redis.Redis(
    host='your-redis-host',
    port=13769,
    password='your-password'
)

# Test connection
print(r.ping())  # Should print True