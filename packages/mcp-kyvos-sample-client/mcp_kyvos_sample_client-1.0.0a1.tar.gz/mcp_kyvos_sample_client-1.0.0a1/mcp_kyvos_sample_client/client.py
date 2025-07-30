import asyncio
import json
import os
import shutil
import signal
import sys
import traceback
from base64 import b64encode
from typing import Any, Dict, Optional

import click
import dotenv
from http.server import BaseHTTPRequestHandler, HTTPServer
from agents.mcp import MCPServerSse, MCPServerStdio, MCPServerSseParams
from mcp_kyvos_sample_client.interaction import run_interaction
from mcp_kyvos_sample_client.config import setup_logger
from agents import trace
from datetime import timedelta
from typing import Optional
import webbrowser
# from mcp.client.auth import OAuthClientProvider, TokenStorage
from mcp.client.sse import sse_client
from mcp.shared.auth import OAuthClientMetadata, OAuthClientInformationFull
from mcp.shared.auth import OAuthToken
from mcp.client.auth import OAuthClientProvider, TokenStorage
from typing import Any
from urllib.parse import parse_qs, urlparse
import threading
from urllib.parse import urlparse, urlunparse
import httpx
import aiohttp
from mcp.shared.exceptions import McpError
import time
import logging

# Setup module logger
logger = logging.getLogger("openai.agents")


class KyvosOAuthSseClient(MCPServerSse):
    """
    An MCPServerSse subclass that adds OAuth authentication
    via an OAuthClientProvider when opening the SSE stream.
    """

    def __init__(
            self,
            params: MCPServerSseParams,
            oauth_provider: OAuthClientProvider,
            cache_tools_list: bool = False,
            name: Optional[str] = None,
            client_session_timeout_seconds: float | None = 600,
    ):
        """
        Args:
            params: Same as MCPServerSseParams – must include url, headers, timeouts.
            oauth_provider: An instance of OAuthClientProvider that will handle
                token acquisition/refresh and inject Authorization headers.
            cache_tools_list: As in MCPServerSse.
            name: Optional human‐readable name.
        """
        try:
            super().__init__(params=params, cache_tools_list=cache_tools_list, name=name,
                             client_session_timeout_seconds=client_session_timeout_seconds)
            self._oauth = oauth_provider
        except Exception as e:
            logger.error(f"Failed to initialize KyvosOAuthSseClient: {e}")
            logger.debug(f"Initialization error details: {traceback.format_exc()}")
            raise

    def create_streams(self):
        """
        Overrides the base method to pass `auth=self._oauth` into sse_client.
        """
        try:
            # pull out the standard params
            url = self.params["url"]
            headers = self.params.get("headers", {})
            timeout = self.params.get("timeout", 300)
            sse_read_timeout = self.params.get("sse_read_timeout", 60 * 300)

            logger.info(f"Creating SSE streams for URL: {url}")

            return sse_client(
                url=url,
                headers=headers,
                timeout=timeout,
                sse_read_timeout=sse_read_timeout,
                auth=self._oauth,
            )
        except Exception as e:
            logger.error(f"Failed to create SSE streams: {e}")
            logger.debug(f"Stream creation error details: {traceback.format_exc()}")
            raise


# 1) Implement TokenStorage (e.g. as in-memory or file-based)
class InMemoryTokenStorage(TokenStorage):
    def __init__(self):
        self._tokens = None
        self._client_info = None
        logger.debug("Initialized InMemoryTokenStorage")

    async def get_tokens(self) -> Optional[OAuthToken]:
        logger.debug(f"Getting tokens: {'available' if self._tokens else 'none'}")
        return self._tokens

    async def set_tokens(self, tokens: OAuthToken) -> None:
        self._tokens = tokens
        logger.info("OAuth tokens stored successfully")

    async def get_client_info(self) -> Optional[OAuthClientInformationFull]:
        logger.debug(f"Getting client info: {'available' if self._client_info else 'none'}")
        return self._client_info

    async def set_client_info(self, client_info: OAuthClientInformationFull) -> None:
        self._client_info = client_info
        logger.info("OAuth client info stored successfully")


class CallbackHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler to capture OAuth callback."""

    def __init__(self, request, client_address, server, callback_data):
        """Initialize with callback data storage."""
        self.callback_data = callback_data
        try:
            super().__init__(request, client_address, server)
        except Exception as e:
            logger.error(f"Failed to initialize CallbackHandler: {e}")
            raise

    def do_GET(self):
        """Handle GET request from OAuth redirect."""
        try:
            logger.info(f"Received OAuth callback request: {self.path}")
            parsed = urlparse(self.path)
            query_params = parse_qs(parsed.query)
            logger.debug(f"Received query params: {query_params}")
            if "code" in query_params:
                self.callback_data["authorization_code"] = query_params["code"][0]
                self.callback_data["state"] = query_params.get("state", [None])[0]
                logger.info("OAuth authorization code received successfully")

                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"""
                <html>
                <body>
                    <h1>Authorization Successful!</h1>
                    <p>You can close this window and return to the terminal.</p>
                    <script>setTimeout(() => window.close(), 2000);</script>
                </body>
                </html>
                """)
            elif "error" in query_params:
                error_msg = query_params["error"][0]
                self.callback_data["error"] = error_msg
                logger.error(f"OAuth authorization error: {error_msg}")

                self.send_response(400)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(
                    f"""
                <html>
                <body>
                    <h1>Authorization Failed</h1>
                    <p>Error: {error_msg}</p>
                    <p>You can close this window and return to the terminal.</p>
                </body>
                </html>
                """.encode()
                )
            else:
                logger.warning(f"OAuth callback received with unexpected parameters: {query_params}")
                self.send_response(404)
                self.end_headers()
        except Exception as e:
            logger.error(f"Error handling OAuth callback: {e}")
            logger.debug(f"Callback handling error details: {traceback.format_exc()}")
            self.send_response(500)
            self.end_headers()

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


class CallbackServer:
    """Simple server to handle OAuth callbacks."""

    def __init__(self, port=3000):
        self.port = port
        self.server = None
        self.thread = None
        self.callback_data = {"authorization_code": None, "state": None, "error": None}
        logger.debug(f"Initialized CallbackServer on port {port}")

    def _create_handler_with_data(self):
        """Create a handler class with access to callback data."""
        callback_data = self.callback_data

        class DataCallbackHandler(CallbackHandler):
            def __init__(self, request, client_address, server):
                super().__init__(request, client_address, server, callback_data)

        return DataCallbackHandler

    def start(self):
        """Start the callback server in a background thread."""
        try:
            handler_class = self._create_handler_with_data()
            self.server = HTTPServer(("localhost", self.port), handler_class)
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            logger.info(f"Started OAuth callback server on http://localhost:{self.port}")
        except Exception as e:
            logger.error(f"Failed to start callback server: {e}")
            logger.debug(f"Server start error details: {traceback.format_exc()}")
            raise

    def stop(self):
        """Stop the callback server."""
        try:
            if self.server:
                logger.debug("Stopping callback server...")
                self.server.shutdown()
                self.server.server_close()
            if self.thread:
                self.thread.join(timeout=1)
            logger.info("Callback server stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping callback server: {e}")

    def wait_for_callback(self, timeout=600):
        """Wait for OAuth callback with timeout."""
        try:
            logger.info(f"Waiting for OAuth callback (timeout: {timeout}s)")
            start_time = time.time()
            while time.time() - start_time < timeout:
                if self.callback_data["authorization_code"]:
                    logger.info("OAuth callback received successfully")
                    return self.callback_data["authorization_code"]
                elif self.callback_data["error"]:
                    error_msg = f"OAuth error: {self.callback_data['error']}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                time.sleep(0.1)

            timeout_msg = "Timeout waiting for OAuth callback"
            logger.error(timeout_msg)
            raise Exception(timeout_msg)
        except Exception as e:
            logger.error(f"Error waiting for OAuth callback: {e}")
            raise

    def get_state(self):
        """Get the received state parameter."""
        return self.callback_data["state"]


def get_welcome_message(username: Optional[str]) -> str:
    if username:
        return f"""
------------------------------------------------------------
Hello {username}! I am your MCP client, ready to answer business questions.
Type '/exit' to quit, or '/clear' to reset the conversation context.
------------------------------------------------------------"""
    return """
------------------------------------------------------------
Hello! I am your MCP client, ready to answer business questions.
Type '/exit' to quit, or '/clear' to reset the conversation context.
------------------------------------------------------------"""


def load_json_file(path: str) -> Dict[str, Any]:
    """Load and validate JSON configuration file."""
    try:
        logger.info(f"Loading configuration from: {path}")
        with open(path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        logger.info("Configuration loaded successfully")
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in configuration file: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading configuration file: {e}")
        raise


def install_signal_handlers(loop: asyncio.AbstractEventLoop):
    """Install signal handlers for graceful shutdown."""

    def _shutdown():
        logger.info("Received termination signal, shutting down gracefully...")
        click.echo("Received termination signal, shutting down gracefully...")
        for task in asyncio.all_tasks(loop):
            task.cancel()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _shutdown)
            logger.debug(f"Installed signal handler for {sig}")
        except NotImplementedError:
            signal.signal(sig, lambda *_: _shutdown())
            logger.debug(f"Installed fallback signal handler for {sig}")


async def handle_sse_basic_auth(conf: Dict[str, Any], name: str) -> None:
    """Handle SSE connection with basic authentication."""
    try:
        url = conf['url']
        logger.info(f"Setting up SSE connection with basic auth to: {url}")

        headers = {'Accept': 'text/event-stream', 'Auth_Type': 'basic'}
        if 'username' in conf and 'password' in conf:
            token = b64encode(f"{conf['username']}:{conf['password']}".encode()).decode()
            headers['Authorization'] = f"Basic {token}"
            logger.debug("Basic auth credentials added to headers")

        # Preflight check
        async with httpx.AsyncClient() as client:
            logger.debug("Performing preflight OPTIONS request")
            pre = await client.options(url, headers=headers)
            if pre.status_code not in (200, 204):
                error_msg = f"Preflight failed: {pre.status_code} {pre.url!r}"
                logger.error(error_msg)
                logger.error(f"Server response: {pre.text.strip()}")
                print(f"Preflight failed: {pre.status_code} {pre.url!r}")
                print("An error occurred on the server. Details:", pre.text.strip())
                sys.exit(1)
            logger.info("Preflight check successful")

        # Connect to server
        async with MCPServerSse(cache_tools_list=True, client_session_timeout_seconds=600,
                                params={'url': url, 'headers': headers}) as server:
            logger.info(f"Connected to MCP server: {name}")
            with trace(workflow_name=f"MCP {name} SSE"):
                await run_interaction(server)

    except Exception as e:
        logger.error(f"Error in SSE basic auth connection: {e}")
        logger.debug(f"SSE basic auth error details: {traceback.format_exc()}")
        print("Main exception:", repr(e))

        if hasattr(e, 'exceptions'):
            for sub in e.exceptions:
                logger.error(f"Sub-exception: {repr(sub)}")
                if isinstance(sub, httpx.HTTPStatusError):
                    resp = sub.response
                    logger.error(f"HTTP error: {resp.status_code} {resp.url}")
                    logger.error(f"Response: {resp.text.strip()}")
                    print(f"Error : {resp.status_code} {resp.url}")
                    print(f"Error : {resp.text.strip()} ")
                    try:
                        # Ensure the response content is read
                        content = await resp.aread()
                        logger.debug(f"Response content: {content.decode()}")
                        print("Response content:", content.decode())
                    except Exception as read_e:
                        logger.error(f"Failed to read response content: {read_e}")
                        print("Failed to read response content:", read_e)
                else:
                    print("-- sub-exception:", repr(sub))
        raise


async def handle_sse_oauth(conf: Dict[str, Any], name: str) -> None:
    """Handle SSE connection with OAuth authentication."""
    try:
        url = conf['url']
        logger.info(f"Setting up SSE connection with OAuth to: {url}")

        parsed = urlparse(url)
        new_path = parsed.path.rstrip('/sse') if parsed.path.endswith('/sse') else parsed.path
        server_base_url = urlunparse(parsed._replace(path=new_path))
        logger.debug(f"Server base URL: {server_base_url}")

        client_port = int(os.getenv("CLIENT_PORT", "3000"))
        callback_server = CallbackServer(port=client_port)
        callback_server.start()

        async def _default_redirect_handler(authorization_url: str) -> None:
            """Default redirect handler that opens the URL in a browser."""
            logger.info(f"Opening browser for authorization: {authorization_url}")
            webbrowser.open(authorization_url)

        async def callback_handler() -> tuple[str, str | None]:
            """Wait for OAuth callback and return auth code and state."""
            try:
                auth_code = callback_server.wait_for_callback(timeout=300)
                return auth_code, callback_server.get_state()
            except Exception as e:
                logger.error(f"Error in OAuth callback handler: {e}")
                raise
            finally:
                callback_server.stop()

        # Setup OAuth client
        client_metadata = OAuthClientMetadata.model_validate({
            "client_name": "Kyvos SSE Client",
            "redirect_uris": [f"http://localhost:{client_port}/callback"],
            "grant_types": ["authorization_code", "refresh_token"],
            "response_types": ["code"],
            "token_endpoint_auth_method": "client_secret_post",
        })

        oauth_provider = OAuthClientProvider(
            server_url=server_base_url,  # Base URL, without /mcp or /sse
            client_metadata=client_metadata,
            storage=InMemoryTokenStorage(),
            redirect_handler=_default_redirect_handler,  # e.g. opens browser
            callback_handler=callback_handler,  # e.g. waits on a local HTTP server
        )
        logger.info("OAuth provider configured successfully")

        # Preflight check
        headers = {'Accept': 'text/event-stream', 'Auth_Type': 'oauth'}
        params = {'url': url, 'headers': headers}

        async with httpx.AsyncClient() as client:
            logger.debug("Performing OAuth preflight OPTIONS request")
            pre = await client.options(url, headers=headers)
            if pre.status_code not in (200, 204):
                error_msg = f"Preflight failed: {pre.status_code} {pre.url!r}"
                logger.error(error_msg)
                logger.error(f"Server response: {pre.text.strip()}")
                print(f"Preflight failed: {pre.status_code} {pre.url!r}")
                print("Server error:", pre.text.strip())
                sys.exit(1)
            logger.info("OAuth preflight check successful")

        # Connect with OAuth
        kyvos = KyvosOAuthSseClient(
            params=params,
            oauth_provider=oauth_provider,
            cache_tools_list=True,
            name="kyvos-oauth-sse",
        )

        click.echo(f"[{name}] Connected to SSE at {url}...")
        async with kyvos as server:
            logger.info(f"OAuth SSE connection established for: {name}")
            with trace(workflow_name=f"MCP {name} SSE"):
                await run_interaction(server)

    except Exception as e:
        logger.error(f"Error in SSE OAuth connection: {e}")
        logger.debug(f"SSE OAuth error details: {traceback.format_exc()}")
        print("Main exception:", repr(e))

        if hasattr(e, 'exceptions'):
            for sub in e.exceptions:
                logger.error(f"Sub-exception: {repr(sub)}")
                if isinstance(sub, httpx.HTTPStatusError):
                    resp = sub.response
                    logger.error(f"HTTP error: {resp.status_code} {resp.url}")
                    logger.error(f"Response: {resp.text.strip()}")
                    print(f"Error : {resp.status_code} {resp.url}")
                    print(f"Error : {resp.text.strip()} ")
                    try:
                        # Ensure the response content is read
                        content = await resp.aread()
                        logger.debug(f"Response content: {content.decode()}")
                        print("Response content:", content.decode())
                    except Exception as read_e:
                        logger.error(f"Failed to read response content: {read_e}")
                        print("Failed to read response content:", read_e)
                else:
                    print("-- sub-exception:", repr(sub))
        raise


async def handle_stdio_connection(conf: Dict[str, Any], name: str) -> None:
    """Handle STDIO connection to MCP server."""
    try:
        command = conf['command']
        args_list = conf.get('args', [])
        env = conf.get('env', {})

        logger.info(f"Setting up STDIO connection: {command} {' '.join(args_list)}")
        logger.debug(f"Environment variables: {env}")

        click.echo(f"[{name}] Connected to STDIO with {command}...")
        async with MCPServerStdio(
                cache_tools_list=True,
                client_session_timeout_seconds=600,
                name=name,
                params={'command': command, 'args': args_list, 'env': env}
        ) as server:
            logger.info(f"STDIO connection established for: {name}")
            with trace(workflow_name=f"MCP {name} STDIO"):
                await run_interaction(server)

    except Exception as e:
        logger.error(f"Error in STDIO connection: {e}")
        logger.debug(f"STDIO error details: {traceback.format_exc()}")
        raise


@click.command()
@click.option(
    '--config', 'config_path', type=click.Path(exists=True), required=True,
    help='Path to JSON config file defining clientConfiguration and mcpServers.'
)
def main(config_path: str) -> None:
    """
    MCP client launcher: auto-start the single server defined in JSON under 'mcpServers'.
    Uses shared client credentials (OpenAI key, log settings), injects into the server process,
    supports graceful shutdown and file-only logging.
    """
    try:
        # Load base .env
        dotenv.load_dotenv()
        logger.debug("Environment variables loaded from .env file")

        # Load config
        config_data = load_json_file(config_path)

        # Extract and set shared client credentials
        client_creds = config_data.get('clientConfiguration', {})
        if isinstance(client_creds, dict) and client_creds:
            logger.info("Applying client configuration settings")
            for key, val in client_creds.items():
                if isinstance(key, str):
                    os.environ[key.upper()] = str(val)
                    logger.debug(f"Set environment variable: {key.upper()}")

        # Load MCP servers config (expect exactly one)
        mcp_servers = config_data.get('mcpServers')
        if not mcp_servers or len(mcp_servers) != 1:
            error_msg = f"Error: expected exactly one entry under 'mcpServers' in {config_path}."
            logger.error(error_msg)
            click.echo(error_msg, err=True)
            sys.exit(1)

        # Extract the single server
        name, server_conf = next(iter(mcp_servers.items()))
        logger.info(f"Configuration loaded for server: {name}")

        loop = asyncio.get_event_loop()
        install_signal_handlers(loop)

        async def start_server(conf: Dict[str, Any]) -> None:
            try:
                # Setup logger (using global creds LOG_FILE and LOG_LEVEL if provided)
                log_file = os.getenv('LOG_FILE')
                log_level = os.getenv('LOG_LEVEL')
                app_logger = setup_logger(log_file=log_file, level=log_level)
                logger.info(f"Logger configured - file: {log_file}, level: {log_level}")

                # Determine mode: optional, infer from config if not set
                provided_mode = conf.get('type')
                if not provided_mode:
                    has_url = 'url' in conf
                    has_cmd = 'command' in conf and conf.get('args')
                    if has_url and not has_cmd:
                        connection_type = 'sse'
                    elif has_cmd and not has_url:
                        connection_type = 'stdio'
                    elif not has_url and not has_cmd:
                        raise RuntimeError(
                            'Cannot infer mode: provide either "url" for SSE or "command"+"args" for STDIO')
                    else:
                        raise RuntimeError('Ambiguous config: both "url" and "command" provided; please specify mode')
                else:
                    connection_type = provided_mode.lower()

                logger.info(f"Connection type determined: {connection_type}")

                # Determine username for welcome
                username = conf.get('username')
                if not username and connection_type == 'stdio':
                    args_list = conf.get('args', [])
                    if '--kyvos-username' in args_list:
                        idx = args_list.index('--kyvos-username')
                        if idx + 1 < len(args_list):
                            username = args_list[idx + 1]

                # Pre-checks
                if not os.getenv('OPENAI_API_KEY'):
                    raise RuntimeError('OPENAI_API_KEY not set')
                if not shutil.which('uvx'):
                    raise RuntimeError('`uvx` CLI not found')

                logger.info("Pre-checks passed successfully")

                # Welcome message
                click.echo(get_welcome_message(username))

                if connection_type == 'sse':
                    auth = os.getenv("AUTH_TYPE", "oauth")
                    logger.info(f"SSE authentication type: {auth}")

                    if auth == "basic":
                        await handle_sse_basic_auth(conf, name)
                    else:
                        await handle_sse_oauth(conf, name)

                elif connection_type == 'stdio':
                    await handle_stdio_connection(conf, name)
                else:
                    raise RuntimeError(f"Invalid connection type '{connection_type}'")

            except RuntimeError as e:
                logger.error(f"Runtime error in server startup: {e}")
                app_logger.error(f"[{name}] Runtime error: {e}")
                click.echo(f"[{name}] Error: {e}", err=True)
                raise
            except Exception as e:
                logger.error(f"Fatal error in server startup: {e}")
                logger.debug(f"Server startup error details: {traceback.format_exc()}")
                app_logger.error(f"[{name}] Fatal error: {e}")
                click.echo(f"[{name}] Error: {e}", err=True)
                raise

        # Launch the single server
        logger.info("Starting MCP client...")
        loop.run_until_complete(start_server(server_conf))

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        click.echo("\nApplication interrupted by user")
    except Exception as e:
        logger.error(f"Fatal application error: {e}")
        logger.debug(f"Application error details: {traceback.format_exc()}")
        click.echo(f"Fatal error: {e}", err=True)
        sys.exit(1)


def cli_main() -> None:
    """Entry point for CLI execution."""
    try:
        main()
    except Exception as e:
        logger.error(f"CLI execution failed: {e}")
        logger.debug(f"CLI error details: {traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    cli_main()