import time
import logging
import os
from typing import Any, Callable, Dict, Optional

from distributed_logger.models.log import LogInfo
from distributed_logger.loggers.factory import LoggerFactory, EnvType
from distributed_logger.models.config import ConfigFactory
from distributed_logger.loggers.logger import Logger

logger = logging.getLogger(__name__)

class AuditLogMiddleware:
    """
    Middleware for auditing requests using distributed logging.
    Supports both WSGI and ASGI frameworks.
    """
    
    def __init__(self, get_response: Callable) -> None:
        """
        Initialize the middleware.
        
        Args:
            get_response: The next middleware or view in the chain
        """
        self.get_response = get_response
        self.logger: Optional[Logger] = None
        self._initialize_logger()

    def _initialize_logger(self) -> None:
        """Initialize the logger based on environment configuration"""
        try:
            broker_type = os.environ.get("BROKER_TYPE", "KAFKA").upper()
            env_type = EnvType.KAFKA

            config = ConfigFactory.create_config(
                config_type=broker_type,
                bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS"),
                topic=os.environ.get("KAFKA_TOPIC"),
                client_id=os.environ.get("KAFKA_CLIENT_ID"),
            )
            
            self.logger = LoggerFactory(env_type, config).get_logger()
            logger.info("Successfully initialized %s logger", broker_type)
            
        except Exception as e:
            logger.error("Failed to initialize logger: %s", str(e))
            raise  # Re-raise the exception since we only support Kafka now
            
    def _extract_request_data(self, request: Any) -> Dict[str, Any]:
        """
        Extract relevant data from the request object.
        
        Args:
            request: The request object (framework agnostic)
            
        Returns:
            Dict containing request data
        """
        data = {}
        
        # Handle different HTTP methods
        if hasattr(request, 'method'):
            # Add request method and path
            data['method'] = request.method
            data['path'] = request.path
            
            # Add query parameters if any
            if hasattr(request, 'GET') and request.GET:
                data['query_params'] = dict(request.GET)
            
            # Handle request body data based on method and content type
            if request.method in ['POST', 'PUT', 'PATCH']:
                content_type = request.content_type if hasattr(request, 'content_type') else ''
                
                # Handle form data
                if hasattr(request, 'POST') and request.POST:
                    data['body'] = dict(request.POST)
                
                # Handle JSON data
                elif 'application/json' in content_type:
                    try:
                        if hasattr(request, 'body') and request.body:
                            import json
                            body_data = json.loads(request.body.decode('utf-8'))
                            # Exclude sensitive fields
                            if isinstance(body_data, dict):
                                body_data = {
                                    k: '[REDACTED]' if k.lower() in ['password', 'token', 'secret', 'key', 'authorization']
                                    else v for k, v in body_data.items()
                                }
                            data['body'] = body_data
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        data['body'] = 'Unable to decode JSON body'
                
                # Handle other content types
                elif hasattr(request, 'body') and request.body:
                    try:
                        data['body'] = request.body.decode('utf-8')
                    except UnicodeDecodeError:
                        data['body'] = 'Binary data not shown'
            
            # Add headers (excluding sensitive ones)
            if hasattr(request, 'headers'):
                headers = dict(request.headers)
                # Exclude sensitive headers
                sensitive_headers = ['cookie', 'authorization', 'proxy-authorization']
                headers = {
                    k.lower(): '[REDACTED]' if k.lower() in sensitive_headers
                    else v for k, v in headers.items()
                }
                data['headers'] = headers
            
            # Add content type and length if available
            if hasattr(request, 'content_type'):
                data['content_type'] = request.content_type
            if hasattr(request, 'content_length'):
                data['content_length'] = request.content_length
                
        return data

    def _get_client_ip(self, request: Any) -> str:
        """
        Get the client IP address from request headers.
        Handles X-Forwarded-For and X-Real-IP headers set by proxy servers.
        
        Args:
            request: The request object
            
        Returns:
            str: The client IP address
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Get the first IP in the chain (original client IP)
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            # Try X-Real-IP, then fall back to REMOTE_ADDR
            ip = request.META.get('HTTP_X_REAL_IP') or request.META.get('REMOTE_ADDR', '')
        return ip

    def __call__(self, request: Any) -> Any:
        """
        Process the request and log audit information.
        
        Args:
            request: The request object
            
        Returns:
            The response from the next middleware or view
        """
        start_time = time.time()
        
        # Process the request first
        response = self.get_response(request)
        
        try:
            if not self.logger:
                logger.warning("Logger not initialized, skipping audit logging")
                return response
                
            # Extract user headers
            headers = {
                'user_id': request.META.get('HTTP_USER_ID', ''),
                'username': request.META.get('HTTP_USER_USERNAME', ''),
                'email': request.META.get('HTTP_USER_EMAIL', ''),
                'is_active': request.META.get('HTTP_USER_IS_ACTIVE', ''),
                'is_staff': request.META.get('HTTP_USER_IS_STAFF', ''),
                'is_superuser': request.META.get('HTTP_USER_IS_SUPERUSER', ''),
                'user_type': request.META.get('HTTP_USER_TYPE', ''),
                'phone_number': request.META.get('HTTP_PHONE_NUMBER', ''),
                'full_name': request.META.get('HTTP_USER_FULL_NAME', ''),
                # Add proxy-related headers
                'x_forwarded_for': request.META.get('HTTP_X_FORWARDED_FOR', ''),
                'x_real_ip': request.META.get('HTTP_X_REAL_IP', ''),
                'x_forwarded_proto': request.META.get('HTTP_X_FORWARDED_PROTO', ''),
                'host': request.META.get('HTTP_HOST', '')
            }
                
            # Create log entry
            log_info = LogInfo(
                ip_address=self._get_client_ip(request),
                user_id=str(request.user.id) if hasattr(request, 'user') and request.user.is_authenticated else None,
                username=request.META.get('HTTP_USER_USERNAME', None),
                request_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time)),
                action=request.path,
                request_data=self._extract_request_data(request),
                headers=headers
            )
            
            # Add the HTTP method to request data
            log_info.request_data['method'] = request.method
            
            # Add the request path to request data
            log_info.request_data['path'] = request.path
            
            # Add the request body to request data
            log_info.request_data['request_data'] = self._extract_request_data(request)
            
            # Add the response status code to request data if available
            if hasattr(response, 'status_code'):
                log_info.request_data['status_code'] = response.status_code
            
            # Safely add response data if available
            response_data = None
            if hasattr(response, 'data'):
                # Handle DRF Response objects
                response_data = response.data
            elif hasattr(response, 'rendered_content'):
                # Handle DRF rendered content
                try:
                    response_data = response.rendered_content.decode('utf-8')
                except (UnicodeDecodeError, AttributeError):
                    response_data = 'Unable to decode rendered content'
            elif hasattr(response, 'content'):
                # Handle regular Django HttpResponse
                try:
                    response_data = response.content.decode('utf-8')
                except (UnicodeDecodeError, AttributeError):
                    response_data = 'Unable to decode response content'
            
            # For error responses in DRF, try to get the detail
            if hasattr(response, 'status_code') and response.status_code >= 400:
                if hasattr(response, 'data') and isinstance(response.data, dict):
                    response_data = response.data.get('detail', response_data)
                
            log_info.request_data['response_data'] = response_data
            
            # Calculate and add request duration
            duration = time.time() - start_time
            log_info.request_data['duration_ms'] = int(duration * 1000)
            
            # Publish log
            self.logger.publish(log_info)
            
        except Exception as e:
            logger.error("Error logging request: %s", str(e))
            # Don't re-raise the exception - logging should not break the application
            
        return response
