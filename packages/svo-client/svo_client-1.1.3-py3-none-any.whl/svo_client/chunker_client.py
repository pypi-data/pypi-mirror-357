"""Async client for SVO semantic chunker microservice."""

__version__ = "1.1.3"

import aiohttp
from typing import List, Optional, Any, Dict
from pydantic import BaseModel
import json
import asyncio

class SVOServerError(Exception):
    """Raised when the SVO server returns an error in the chunk response."""
    def __init__(self, code: str, message: str, chunk_error: dict = None):
        self.code = code
        self.message = message
        self.chunk_error = chunk_error or {}
        super().__init__(f"SVO server error [{code}]: {message}")

class SVOJSONRPCError(Exception):
    """Raised when the SVO server returns a JSON-RPC error response."""
    def __init__(self, code: int, message: str, data: dict = None):
        self.code = code
        self.message = message
        self.data = data or {}
        super().__init__(f"JSON-RPC error [{code}]: {message}")

class SVOHTTPError(Exception):
    """Raised when the SVO server returns an HTTP error or invalid response."""
    def __init__(self, status_code: int, message: str, response_text: str = ""):
        self.status_code = status_code
        self.message = message
        self.response_text = response_text
        super().__init__(f"HTTP error [{status_code}]: {message}")

class SVOConnectionError(Exception):
    """Raised when there are network/connection issues with the SVO server."""
    def __init__(self, message: str, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(message)

class SVOTimeoutError(Exception):
    """Raised when request to SVO server times out."""
    def __init__(self, message: str, timeout_value: float = None):
        self.message = message
        self.timeout_value = timeout_value
        super().__init__(f"Timeout error: {message}")

class ChunkerClient:
    def __init__(self, url: str = "http://localhost", port: int = 8009, timeout: float = 60.0):
        """
        :param url: Base URL of the SVO chunker service
        :param port: Port of the service
        :param timeout: HTTP request timeout in seconds (default: 60.0)
        """
        self.base_url = f"{url.rstrip('/')}: {port}"
        self.base_url = f"{url.rstrip('/')}: {port}".replace(': ', ':')
        self.session: Optional[aiohttp.ClientSession] = None
        self.timeout = timeout

    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.session:
            await self.session.close()

    def _check_jsonrpc_response(self, data: dict) -> Any:
        """
        Check JSON-RPC response for errors and return result.
        
        :param data: JSON-RPC response data
        :return: Result data if successful
        :raises SVOJSONRPCError: If JSON-RPC error is present
        """
        if "error" in data:
            error = data["error"]
            raise SVOJSONRPCError(
                code=error.get("code", -1),
                message=error.get("message", "Unknown JSON-RPC error"),
                data=error.get("data", {})
            )
        return data.get("result")

    async def _handle_response(self, response: aiohttp.ClientResponse) -> dict:
        """
        Handle HTTP response and parse JSON with error handling.
        
        :param response: aiohttp response object
        :return: Parsed JSON data
        :raises SVOHTTPError: If HTTP error or JSON parsing error occurs
        """
        try:
            response.raise_for_status()
        except aiohttp.ClientResponseError as e:
            response_text = ""
            try:
                response_text = await response.text()
            except:
                pass
            raise SVOHTTPError(
                status_code=e.status,
                message=f"HTTP {e.status}: {e.message}",
                response_text=response_text
            )
        
        try:
            return await response.json()
        except (json.JSONDecodeError, aiohttp.ContentTypeError) as e:
            response_text = ""
            try:
                response_text = await response.text()
            except:
                pass
            raise SVOHTTPError(
                status_code=response.status,
                message=f"Invalid JSON response: {str(e)}",
                response_text=response_text
            )

    async def _make_request(self, method: str, url: str, timeout: Optional[float] = None, **kwargs):
        """
        Make HTTP request with comprehensive error handling.
        
        :param method: HTTP method ('GET' or 'POST')
        :param url: Request URL
        :param timeout: Request timeout
        :param kwargs: Additional request parameters
        :return: Parsed JSON response
        :raises SVOTimeoutError: If request times out
        :raises SVOConnectionError: If connection fails
        :raises SVOHTTPError: If HTTP error occurs
        """
        req_timeout = aiohttp.ClientTimeout(total=timeout if timeout is not None else self.timeout)
        
        try:
            if method.upper() == 'GET':
                async with self.session.get(url, timeout=req_timeout, **kwargs) as resp:
                    return await self._handle_response(resp)
            elif method.upper() == 'POST':
                async with self.session.post(url, timeout=req_timeout, **kwargs) as resp:
                    return await self._handle_response(resp)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
        except asyncio.TimeoutError as e:
            raise SVOTimeoutError(
                f"Request timed out after {req_timeout.total}s",
                timeout_value=req_timeout.total
            )
        except aiohttp.ClientConnectorError as e:
            raise SVOConnectionError(
                f"Failed to connect to server at {url}: {str(e)}",
                original_error=e
            )
        except aiohttp.ClientConnectionError as e:
            raise SVOConnectionError(
                f"Connection error: {str(e)}",
                original_error=e
            )
        except aiohttp.ClientOSError as e:
            raise SVOConnectionError(
                f"Network error: {str(e)}",
                original_error=e
            )
        except aiohttp.ServerDisconnectedError as e:
            raise SVOConnectionError(
                f"Server disconnected: {str(e)}",
                original_error=e
            )
        except Exception as e:
            # Catch any other unexpected errors
            if isinstance(e, (SVOHTTPError, SVOJSONRPCError, SVOServerError, SVOTimeoutError, SVOConnectionError)):
                # Re-raise our custom exceptions
                raise
            else:
                # Wrap unexpected exceptions
                raise SVOConnectionError(
                    f"Unexpected error during request: {str(e)}",
                    original_error=e
                )

    async def get_openapi_schema(self, timeout: Optional[float] = None) -> Any:
        url = f"{self.base_url}/openapi.json"
        return await self._make_request('GET', url, timeout=timeout)

    def parse_chunk(self, chunk) -> 'SemanticChunk':
        from chunk_metadata_adapter import SemanticChunk
        if isinstance(chunk, SemanticChunk):
            return chunk
        obj, err = SemanticChunk.validate_and_fill({k: v for k, v in chunk.items() if k in SemanticChunk.model_fields})
        if err:
            error_fields = err.get('fields')
            if error_fields:
                raise ValueError(f"Chunk does not validate against chunk_metadata_adapter.SemanticChunk: {err['error']}\nFields: {error_fields}\nChunk: {chunk}")
            else:
                raise ValueError(f"Chunk does not validate against chunk_metadata_adapter.SemanticChunk: {err}\nChunk: {chunk}")
        return obj

    async def chunk_text(self, text: str, timeout: Optional[float] = None, **params) -> List['SemanticChunk']:
        url = f"{self.base_url}/cmd"
        payload = {
            "jsonrpc": "2.0",
            "method": "chunk",
            "params": {"text": text, **params},
            "id": 1
        }
        
        data = await self._make_request('POST', url, timeout=timeout, json=payload)
        
        # Check for JSON-RPC level errors first
        result = self._check_jsonrpc_response(data)
        
        chunks = result.get("chunks", []) if result else []
        parsed_chunks = []
        for chunk in chunks:
            if isinstance(chunk, dict) and "error" in chunk:
                err = chunk["error"]
                raise SVOServerError(
                    code=err.get("code", "unknown"),
                    message=err.get("message", str(err)),
                    chunk_error=err
                )
            parsed_chunks.append(self.parse_chunk(chunk))
        return parsed_chunks

    async def get_help(self, cmdname: Optional[str] = None, timeout: Optional[float] = None) -> Any:
        url = f"{self.base_url}/cmd"
        payload = {
            "jsonrpc": "2.0",
            "method": "help",
            "id": 1
        }
        if cmdname:
            payload["params"] = {"cmdname": cmdname}
            
        data = await self._make_request('POST', url, timeout=timeout, json=payload)
        
        # Check for JSON-RPC level errors
        result = self._check_jsonrpc_response(data)
        return {"result": result}

    async def health(self, timeout: Optional[float] = None) -> Any:
        url = f"{self.base_url}/cmd"
        payload = {
            "jsonrpc": "2.0",
            "method": "health",
            "id": 1
        }
        
        data = await self._make_request('POST', url, timeout=timeout, json=payload)
        
        # Check for JSON-RPC level errors
        result = self._check_jsonrpc_response(data)
        return {"result": result}

    def reconstruct_text(self, chunks: List['SemanticChunk']) -> str:
        """
        Reconstruct the original text from a list of SemanticChunk objects.
        Склеивает текст из чанков в исходном порядке.
        """
        sorted_chunks = sorted(
            chunks,
            key=lambda c: c.ordinal if getattr(c, 'ordinal', None) is not None else chunks.index(c)
        )
        return ''.join(chunk.text for chunk in sorted_chunks if getattr(chunk, 'text', None)) 