"""
Pulsar Web Server Python Wrapper using ctypes
"""
import sys
import ctypes
import enum
from typing import Any, Callable, Optional, Union
from pathlib import Path

# Get package directory
PACKAGE_DIR = Path(__file__).parent.resolve()

def _load_library():
    lib_dir = Path(__file__).parent / "lib"
    
    # Platform-specific filenames
    libnames = {
        'linux': 'libpulsar.so',
        'darwin': 'libpulsar.dylib',
        'win32': 'pulsar.dll'
    }
    
    libname = libnames.get(sys.platform)
    if not libname:
        raise OSError(f"Unsupported platform: {sys.platform}")
    
    libpath = lib_dir / libname
    if not libpath.exists():
        raise FileNotFoundError(f"Library not found at {libpath}")
    
    return ctypes.CDLL(str(libpath))

lib = _load_library()

# Type definitions
class HttpMethod(enum.IntEnum):
    INVALID = -1
    OPTIONS = 0
    GET = 1
    POST = 2
    PUT = 3
    PATCH = 4
    DELETE = 5

class HttpStatus(enum.IntEnum):
    # Informational
    CONTINUE = 100
    SWITCHING_PROTOCOLS = 101
    PROCESSING = 102
    EARLY_HINTS = 103

    # Success
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NON_AUTHORITATIVE_INFORMATION = 203
    NO_CONTENT = 204
    RESET_CONTENT = 205
    PARTIAL_CONTENT = 206
    MULTI_STATUS = 207
    ALREADY_REPORTED = 208
    IM_USED = 226

    # Redirection
    MULTIPLE_CHOICES = 300
    MOVED_PERMANENTLY = 301
    FOUND = 302
    SEE_OTHER = 303
    NOT_MODIFIED = 304
    USE_PROXY = 305
    TEMPORARY_REDIRECT = 307
    PERMANENT_REDIRECT = 308

    # Client Errors
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    PAYMENT_REQUIRED = 402
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    NOT_ACCEPTABLE = 406
    PROXY_AUTHENTICATION_REQUIRED = 407
    REQUEST_TIMEOUT = 408
    CONFLICT = 409
    GONE = 410
    LENGTH_REQUIRED = 411
    PRECONDITION_FAILED = 412
    PAYLOAD_TOO_LARGE = 413
    URI_TOO_LONG = 414
    UNSUPPORTED_MEDIA_TYPE = 415
    RANGE_NOT_SATISFIABLE = 416
    EXPECTATION_FAILED = 417
    IM_A_TEAPOT = 418
    MISDIRECTED_REQUEST = 421
    UNPROCESSABLE_ENTITY = 422
    LOCKED = 423
    FAILED_DEPENDENCY = 424
    TOO_EARLY = 425
    UPGRADE_REQUIRED = 426
    PRECONDITION_REQUIRED = 428
    TOO_MANY_REQUESTS = 429
    REQUEST_HEADER_FIELDS_TOO_LARGE = 431
    UNAVAILABLE_FOR_LEGAL_REASONS = 451

    # Server Errors
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504
    HTTP_VERSION_NOT_SUPPORTED = 505
    VARIANT_ALSO_NEGOTIATES = 506
    INSUFFICIENT_STORAGE = 507
    LOOP_DETECTED = 508
    NOT_EXTENDED = 510
    NETWORK_AUTHENTICATION_REQUIRED = 511

# ctypes setup
lib.pulsar_run.argtypes = [ctypes.c_int]
lib.pulsar_run.restype = ctypes.c_int

# Connection and request/response objects are opaque pointers
Connection = ctypes.c_void_p
Route = ctypes.c_void_p

# Handler type (returns bool, takes Connection)
HandlerFunc = ctypes.CFUNCTYPE(ctypes.c_bool, Connection)

# Middleware type (same as handler)
MiddlewareFunc = HandlerFunc

def _setup_function(name: str, argtypes: list, restype: Any) -> None: # type: ignore
    """Helper to setup ctypes function signatures"""
    func = getattr(lib, name)
    func.argtypes = argtypes
    func.restype = restype

# Setup all function signatures
_setup_function("route_register", 
    [ctypes.c_char_p, ctypes.c_int, HandlerFunc], Route)
_setup_function("register_static_route", 
    [ctypes.c_char_p, ctypes.c_char_p], Route)
_setup_function("use_global_middleware", 
    [ctypes.c_size_t, ctypes.c_void_p], None)
_setup_function("use_route_middleware", 
    [Route, ctypes.c_size_t, ctypes.c_void_p], None)

# Response functions
_setup_function("conn_servefile", [Connection, ctypes.c_char_p], ctypes.c_bool)
_setup_function("conn_write_string", [Connection, ctypes.c_char_p], ctypes.c_int)
_setup_function("serve_404", [Connection], ctypes.c_int)
_setup_function("conn_write", [Connection, ctypes.c_void_p, ctypes.c_size_t], ctypes.c_int)
_setup_function("conn_writef", [Connection, ctypes.c_char_p], ctypes.c_int)

# Request functions
_setup_function("req_method", [Connection], ctypes.c_char_p)
_setup_function("req_path", [Connection], ctypes.c_char_p)
_setup_function("req_body", [Connection], ctypes.c_char_p)
_setup_function("req_content_len", [Connection], ctypes.c_size_t)

# Parameter functions
_setup_function("query_get", [Connection, ctypes.c_char_p], ctypes.c_char_p)
_setup_function("get_path_param", [Connection, ctypes.c_char_p], ctypes.c_char_p)

# Header functions
_setup_function("req_header_get", [Connection, ctypes.c_char_p], ctypes.c_char_p)
_setup_function("res_header_get", [Connection, ctypes.c_char_p], ctypes.c_char_p)

# Status/header setters
_setup_function("conn_set_status", [Connection, ctypes.c_int], None)
_setup_function("conn_set_content_type", [Connection, ctypes.c_char_p], ctypes.c_bool)
_setup_function("conn_writeheader", [Connection, ctypes.c_char_p, ctypes.c_char_p], ctypes.c_bool)

# User data functions
_setup_function("set_userdata", 
    [Connection, ctypes.c_void_p, ctypes.CFUNCTYPE(None, ctypes.c_void_p)], None)
_setup_function("get_userdata", [Connection], ctypes.c_void_p)

# Method conversion
_setup_function("http_method_from_string", [ctypes.c_char_p], ctypes.c_int)
_setup_function("http_method_to_string", [ctypes.c_int], ctypes.c_char_p)

# Global dictionary to maintain callback references
_CALLBACK_STORE = {}

def _create_handler_wrapper(py_handler): # type: ignore
    """Wrapper that keeps Python handler alive and handles exceptions"""
    @HandlerFunc
    def wrapped_handler(conn: Connection): # type: ignore
        try:
            # Store the current connection in thread-local storage if needed
            return py_handler(conn) # type: ignore
        except Exception as e:
            print(f"Handler error: {e}", file=sys.stderr)
            return False
    
    # Store the wrapper to prevent garbage collection
    _CALLBACK_STORE[id(py_handler)] = wrapped_handler # type: ignore
    return wrapped_handler

class Pulsar:
    """Python wrapper for Pulsar web server"""
    
    @staticmethod
    def run(port: int) -> int:
        """Start the server on specified port"""
        return lib.pulsar_run(port)
    
    @staticmethod
    def route(
        pattern: str, 
        method: Union[str, HttpMethod], 
        handler: Callable[['Connection'], bool]
    ) -> Route:
        """Register a new route"""
        if isinstance(method, str):
            method = lib.http_method_from_string(method.encode())
            if method == HttpMethod.INVALID:
                raise ValueError(f"Invalid HTTP method: {method}")
        
       # Use our safe wrapper instead of direct HandlerFunc
        wrapped_handler = _create_handler_wrapper(handler)
        
        route = lib.route_register(
            pattern.encode(),
            method,
            wrapped_handler
        )
        if not route:
            raise RuntimeError("Failed to register route")
        return route
    
    @staticmethod
    def static_route(pattern: str, directory: str) -> Route:
        """Register static file route"""
        route = lib.register_static_route(
            pattern.encode(),
            directory.encode()
        )
        if not route:
            raise RuntimeError("Failed to register static route")
        return route
    
    # Request methods
    @staticmethod
    def get_method(conn: Connection) -> str:
        """Get request method"""
        return lib.req_method(conn).decode()
    
    @staticmethod
    def get_path(conn: Connection) -> str:
        """Get request path"""
        return lib.req_path(conn).decode()
    
    @staticmethod
    def get_body(conn: Connection) -> bytes:
        """Get request body"""
        body = lib.req_body(conn)
        return ctypes.string_at(body) if body else b''
    
    @staticmethod
    def get_content_length(conn: Connection) -> int:
        """Get content length"""
        return lib.req_content_len(conn)
    
    # Response methods
    @staticmethod
    def set_status(conn: Connection, status: HttpStatus) -> None:
        """Set response status code"""
        lib.conn_set_status(conn, status)
    
    @staticmethod
    def set_content_type(conn: Connection, content_type: str) -> bool:
        """Set response content type"""
        return lib.conn_set_content_type(conn, content_type.encode())
    
    @staticmethod
    def write_header(conn: Connection, name: str, value: str) -> bool:
        """Set response header"""
        return lib.conn_writeheader(conn, name.encode(), value.encode())
    
    @staticmethod
    def write(conn: Connection, data: bytes) -> int:
        """Write response data"""
        return lib.conn_write(conn, data, len(data))
    
    @staticmethod
    def write_string(conn: Connection, text: str) -> int:
        """Write response text"""
        return lib.conn_write_string(conn, text.encode())
    
    @staticmethod
    def writef(conn: Connection, fmt: str, *args: Any) -> int:
        """Write formatted response with printf-style formatting"""
        formatted = fmt % args # Old printf-style formating.
        return lib.conn_write_string(conn, formatted.encode())
    
    @staticmethod
    def serve_file(conn: Connection, filename: str) -> bool:
        """Serve a file"""
        return lib.conn_servefile(conn, filename.encode())
    
    @staticmethod
    def serve_404(conn: Connection) -> int:
        """Serve 404 response"""
        return lib.serve_404(conn)
    
    # Parameter methods
    @staticmethod
    def get_query_param(conn: Connection, name: str) -> Optional[str]:
        """Get query parameter by name"""
        param = lib.query_get(conn, name.encode())
        return param.decode() if param else None
    
    @staticmethod
    def get_path_param(conn: Connection, name: str) -> Optional[str]:
        """Get path parameter by name"""
        param = lib.get_path_param(conn, name.encode())
        return param.decode() if param else None
    
    # Header methods
    @staticmethod
    def get_req_header(conn: Connection, name: str) -> Optional[str]:
        """Get request header by name"""
        header = lib.req_header_get(conn, name.encode())
        return header.decode() if header else None
    
    @staticmethod
    def get_res_header(conn: Connection, name: str) -> Optional[str]:
        """Get response header by name"""
        header = lib.res_header_get(conn, name.encode())
        return header.decode() if header else None
    
    # User data methods
    @staticmethod
    def set_user_data(
        conn: Connection,
        data: Any,
        free_func: Optional[Callable[[Any], None]] = None
    ) -> None:
        """Set per-connection user data"""
        
        

        if data is None:
            raise TypeError("data must not be None")
        
        if free_func is None:
            raise TypeError("free_func is required")
        
        # Convert Python object to void pointer
        py_obj = ctypes.py_object(data)
        ptr = ctypes.cast(ctypes.pointer(py_obj), ctypes.c_void_p)
        
        lib.set_userdata(conn, ptr, free_func)
    
    @staticmethod
    def get_user_data(conn: Connection) -> Any:
        """Get per-connection user data"""
        ptr = lib.get_userdata(conn)
        if not ptr:
            return None
        
        py_obj = ctypes.cast(ptr, ctypes.POINTER(ctypes.py_object)).contents
        return py_obj.value
    
    # Middleware methods
    @staticmethod
    def use_global_middleware(*middleware: Callable[[Connection], bool]) -> None:
        """Register global middleware"""
        # Convert middleware to C array
        mw_array = (MiddlewareFunc * len(middleware))()
        handlers = []
        
        for i, mw in enumerate(middleware):
            @MiddlewareFunc
            def wrapped(conn: Connection) -> bool:
                return mw(conn)
            
            mw_array[i] = wrapped
            handlers.append(wrapped)  # type: ignore # Keep references
        
        lib.use_global_middleware(len(middleware), mw_array)
    
    @staticmethod
    def use_route_middleware(route: Route, *middleware: Callable[[Connection], bool]) -> None:
        """Register route-specific middleware"""
        # Convert middleware to C array
        mw_array = (MiddlewareFunc * len(middleware))()
        handlers = []
        
        for i, mw in enumerate(middleware):
            @MiddlewareFunc
            def wrapped(conn: Connection) -> bool:
                return mw(conn)
            
            mw_array[i] = wrapped
            handlers.append(wrapped)  # type: ignore # Keep references
        
        lib.use_route_middleware(route, len(middleware), mw_array)

# Example usage
if __name__ == "__main__":
    def hello_handler(conn: Connection) -> bool:
        Pulsar.set_status(conn, HttpStatus.OK)
        Pulsar.set_content_type(conn, "text/plain")
        Pulsar.write_string(conn, "Hello from Python!")
        return True
    
    def auth_middleware(conn: Connection) -> bool:
        token = Pulsar.get_req_header(conn, "Authorization")
        if not token:
            Pulsar.set_status(conn, HttpStatus.UNAUTHORIZED)
            return False
        return True
    
    # Register routes
    route = Pulsar.route("/hello", HttpMethod.GET, hello_handler)
    Pulsar.use_route_middleware(route, auth_middleware)
    
    # Serve static files
    Pulsar.static_route("/static/", "./public")
    
    # Start server
    Pulsar.run(8080)