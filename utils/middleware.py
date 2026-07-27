import time
import hashlib
import threading
from collections import defaultdict, deque
from datetime import datetime, timedelta

from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.apps import apps
import signal
import logging

from utils.exceptions import CustomException, TimeoutError, SuspiciousActivityDetectedError, DDOSProtectionError, log_activity
from django.apps import apps

from utils.auth_utils import decode_jwt

_request_local = threading.local()

logger = logging.getLogger(__name__)

# Global variable to cache the model once loaded
_log_model = None



class CustomExceptionMiddleware(MiddlewareMixin):
	"""
	Middleware that provides:
	1. Request timeout control
	2. Rate limiting per IP/user
	3. Consecutive identical query detection
	4. DDoS protection
	"""

	
	def __init__(self, get_response):
		super().__init__(get_response)
		self.get_response = get_response
		
		# Configuration - can be overridden in settings
		self.timeout_seconds = getattr(settings, 'REQUEST_TIMEOUT_SECONDS', 3)
		self.rate_limit_requests = getattr(settings, 'RATE_LIMIT_REQUESTS_PER_MINUTE', 60)
		self.rate_limit_window = getattr(settings, 'RATE_LIMIT_WINDOW_SECONDS', 60)
		self.consecutive_limit = getattr(settings, 'CONSECUTIVE_IDENTICAL_QUERIES_LIMIT', 5)
		self.consecutive_window = getattr(settings, 'CONSECUTIVE_QUERIES_WINDOW_SECONDS', 60)
		self.ddos_block_duration = getattr(settings, 'DDOS_BLOCK_DURATION_SECONDS', 300)  # 5 minutes
		
		# In-memory storage for request tracking
		self.request_counts = defaultdict(deque)
		self.consecutive_queries = defaultdict(deque)
		self.blocked_ips = {}
		self.lock = threading.RLock()
	
	def get_client_identifier(self, request):
		"""Get unique identifier for the client (IP + User if header available)"""
		ip = self.get_client_ip(request)
		if request.headers.get('jwtauth'):
			try:
				jwt_token = request.headers.get('jwtauth').split(' ')[1]
				user_info = decode_jwt(jwt_token)
				return f"{ip}:{user_info}"
			except (IndexError, Exception) as e:
				logger.warning(f"Failed to decode JWT: {e}")
				return ip
		return ip
	
	def get_client_ip(self, request):
		"""Extract client IP address from request"""
		x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
		if x_forwarded_for:
			ip = x_forwarded_for.split(',')[0].strip()
		else:
			ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
		return ip
	
	def get_query_signature(self, request):
		"""Create a signature for the request to detect identical queries"""
		# Combine method, path, and sorted query parameters
		query_string = request.GET.urlencode() if request.GET else ''
		body = ''
		
		# For POST requests, include body content (be careful with large payloads)
		if request.method == 'POST' and hasattr(request, 'body'):
			try:
				body = request.body.decode('utf-8')[:1000]  # Limit to first 1000 chars
			except Exception:
				body = str(request.body)[:1000]
		
		signature_string = f"{request.method}:{request.path}:{query_string}:{body}"
		return hashlib.md5(signature_string.encode()).hexdigest()
	
	def is_ip_blocked(self, client_id):
		"""Check if IP is currently blocked"""
		with self.lock:
			if client_id in self.blocked_ips:
				block_time = self.blocked_ips[client_id]
				if datetime.now() - block_time < timedelta(seconds=self.ddos_block_duration):
					return True
				else:
					# Block expired, remove it
					del self.blocked_ips[client_id]
		return False
	
	def block_ip(self, client_id, reason="DDoS protection"):
		"""Block an IP address"""
		with self.lock:
			self.blocked_ips[client_id] = datetime.now()
			log_activity(
				data={"blocked_client": client_id, "reason": reason, "timestamp": datetime.now().isoformat()},
				description=f'Client {client_id} has been blocked for {reason}',
				activity_type='SYSTEM_ALERT',
				source='SYSTEM'
			)
	
	def check_rate_limit(self, client_id):
		"""Check if client has exceeded rate limit"""
		now = time.time()
		
		with self.lock:
			# Clean old entries
			while self.request_counts[client_id] and \
					now - self.request_counts[client_id][0] > self.rate_limit_window:
				self.request_counts[client_id].popleft()
			
			# Check if limit exceeded
			if len(self.request_counts[client_id]) >= self.rate_limit_requests:
				log_activity(
					data={
						"client_id": client_id,
						"request_count": len(self.request_counts[client_id]),
						"limit": self.rate_limit_requests,
						"window": self.rate_limit_window
					},
					description=f'Client {client_id} has too many requests within a short time.',
					activity_type='SYSTEM_ALERT',
					source='SYSTEM'
				)
				raise DDOSProtectionError('Rate limit exceeded')
			
			# Add current request
			self.request_counts[client_id].append(now)
			return True
	
	def check_consecutive_queries(self, client_id, query_signature):
		"""Check for consecutive identical queries"""
		now = time.time()
		
		with self.lock:
			# Clean old entries
			while self.consecutive_queries[client_id] and \
					now - self.consecutive_queries[client_id][0][1] > self.consecutive_window:
				self.consecutive_queries[client_id].popleft()
			
			# Count consecutive identical queries
			consecutive_count = 0
			for sig, timestamp in reversed(list(self.consecutive_queries[client_id])):
				if sig == query_signature:
					consecutive_count += 1
				else:
					break
			
			# Add current query
			self.consecutive_queries[client_id].append((query_signature, now))
			
			# Check if limit exceeded
			if consecutive_count >= self.consecutive_limit:
				log_activity(
					data={
						"client_id": client_id,
						"consecutive_count": consecutive_count,
						"limit": self.consecutive_limit,
						"query_signature": query_signature
					},
					description=f'Client {client_id} has too many identical consecutive requests.',
					activity_type='SYSTEM_ALERT',
					source='SYSTEM'
				)
				raise DDOSProtectionError('Too many consecutive identical queries')
			
			return True
	
	def timeout_handler(self, signum, frame):
		"""Handle timeout signal"""
		raise TimeoutError('Request timeout exceeded')
	
	def process_request(self, request):
		_request_local.request = request
		"""Process incoming request for DDoS protection and rate limiting"""
		client_id = self.get_client_identifier(request)
		
		# Check if IP is blocked
		if self.is_ip_blocked(client_id):
			logger.warning(f"Blocked request from {client_id}")
			log_activity(
				data={"client_id": client_id, "blocked_ips_count": len(self.blocked_ips)},
				description=f"Blocked request from {client_id}",
				activity_type='SYSTEM_ALERT',
				source='SYSTEM'
			)
			raise SuspiciousActivityDetectedError('Your IP has been temporarily blocked')
		
		# Check rate limit
		try:
			self.check_rate_limit(client_id)
		except DDOSProtectionError:
			logger.warning(f"Rate limit exceeded for {client_id}")
			self.block_ip(client_id, "Rate limit exceeded")
			raise
		
		# Check consecutive identical queries
		query_signature = self.get_query_signature(request)
		try:
			self.check_consecutive_queries(client_id, query_signature)
		except DDOSProtectionError:
			logger.warning(f"Consecutive identical queries detected for {client_id}")
			self.block_ip(client_id, "Consecutive identical queries")
			raise
		
		# Set up timeout for the request
		request._start_time = time.time()
	
		return None
	
	def process_response(self, request, response):
		"""Process response and clean up timeout"""

		# Check if request took too long (fallback for systems without signals)
		if hasattr(request, '_start_time'):
			duration = time.time() - request._start_time
			if duration > self.timeout_seconds:
				logger.warning(f"Request took {duration:.2f}s, exceeding timeout of {self.timeout_seconds}s")
				log_activity(
					data={
						"duration": duration,
						"timeout_limit": self.timeout_seconds,
						"path": request.path,
						"method": request.method
					},
					description=f"Request took {duration:.2f}s, exceeding timeout of {self.timeout_seconds}s",
					activity_type='SYSTEM_ALERT',
					source='SYSTEM'
				)
		
		return response
	
	def process_exception(self, request, exception):
		"""Handle all exceptions"""
		if not settings.DEBUG:
			if isinstance(exception, CustomException):
				return exception.to_response()
			elif isinstance(exception, Exception):
				logger.exception(exception)
				return CustomException().to_response()
		return None
