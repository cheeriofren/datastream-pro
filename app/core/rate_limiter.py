from fastapi import HTTPException, Request
from datetime import datetime, timedelta
from typing import Dict, Optional
import time
import os
from dotenv import load_dotenv
from .database import get_db, APIKey
from sqlalchemy.orm import Session

load_dotenv()

class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, Dict] = {}
        self.rate_limit = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
        self.window_size = 60  # 1 menit dalam detik
    
    def _get_key(self, request: Request, api_key: Optional[str] = None) -> str:
        """
        Mendapatkan kunci unik untuk request
        """
        if api_key:
            return f"api_key:{api_key}"
        return f"ip:{request.client.host}"
    
    def _cleanup_old_requests(self, key: str):
        """
        Membersihkan request yang sudah kadaluarsa
        """
        current_time = time.time()
        if key in self.requests:
            self.requests[key] = {
                timestamp: count
                for timestamp, count in self.requests[key].items()
                if current_time - timestamp < self.window_size
            }
    
    async def check_rate_limit(self, request: Request, api_key: Optional[str] = None) -> bool:
        """
        Memeriksa rate limit untuk request
        """
        key = self._get_key(request, api_key)
        current_time = time.time()
        
        # Bersihkan request lama
        self._cleanup_old_requests(key)
        
        # Hitung total request dalam window
        if key in self.requests:
            total_requests = sum(self.requests[key].values())
        else:
            total_requests = 0
        
        # Cek apakah melebihi limit
        if total_requests >= self.rate_limit:
            return False
        
        # Tambahkan request baru
        if key not in self.requests:
            self.requests[key] = {}
        
        window_start = current_time - (current_time % self.window_size)
        self.requests[key][window_start] = self.requests[key].get(window_start, 0) + 1
        
        return True
    
    def get_remaining_requests(self, key: str) -> int:
        """
        Mendapatkan jumlah request yang tersisa
        """
        self._cleanup_old_requests(key)
        if key in self.requests:
            total_requests = sum(self.requests[key].values())
            return max(0, self.rate_limit - total_requests)
        return self.rate_limit

class RateLimitMiddleware:
    def __init__(self, rate_limiter: RateLimiter):
        self.rate_limiter = rate_limiter
    
    async def __call__(self, request: Request, call_next):
        # Skip rate limiting untuk endpoint tertentu
        if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Cek API key jika ada
        api_key = request.headers.get("X-API-Key")
        
        # Cek rate limit
        if not await self.rate_limiter.check_rate_limit(request, api_key):
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later."
            )
        
        # Tambahkan header rate limit
        response = await call_next(request)
        key = self.rate_limiter._get_key(request, api_key)
        remaining = self.rate_limiter.get_remaining_requests(key)
        
        response.headers["X-RateLimit-Limit"] = str(self.rate_limiter.rate_limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(
            int(time.time() + self.rate_limiter.window_size)
        )
        
        return response

class APIKeyRateLimiter:
    def __init__(self, db: Session):
        self.db = db
        self.rate_limit = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    async def check_api_key_rate_limit(self, api_key: str) -> bool:
        """
        Memeriksa rate limit untuk API key
        """
        db_api_key = self.db.query(APIKey).filter(
            APIKey.key == api_key,
            APIKey.is_active == True
        ).first()
        
        if not db_api_key:
            return False
        
        # Update last_used
        db_api_key.last_used = datetime.utcnow()
        self.db.commit()
        
        return True
    
    def get_api_key_usage(self, api_key: str) -> Dict:
        """
        Mendapatkan informasi penggunaan API key
        """
        db_api_key = self.db.query(APIKey).filter(
            APIKey.key == api_key,
            APIKey.is_active == True
        ).first()
        
        if not db_api_key:
            return {
                "error": "API key not found or inactive"
            }
        
        return {
            "created_at": db_api_key.created_at.isoformat(),
            "last_used": db_api_key.last_used.isoformat() if db_api_key.last_used else None,
            "is_active": db_api_key.is_active
        } 