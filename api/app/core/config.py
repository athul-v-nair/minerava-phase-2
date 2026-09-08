import os

JWT_SECRET = os.getenv("JWT_SECRET", "dev-jwt-secret-change-me-at-least-32-chars-long")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TTL_SECONDS = 15 * 60  # 15m
JWT_REFRESH_TTL_SECONDS = 7 * 24 * 60 * 60  # 7d
