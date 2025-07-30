from pathlib import Path
from aiohttp import web
import aiohttp_jinja2
import jinja2
from rich.console import Console
from rich.panel import Panel
from ..core.engine import Engine
from ..admin import AdminPanel
from ..plugins import initialize_plugins
from ..utils.logging import get_logger

# Получаем логгер для данного модуля
logger = get_logger("core.server")

console = Console()

REQUIRED_DIRECTORIES = ['content', 'templates', 'static']
REQUIRED_FILES = ['config.toml']


def validate_project_structure(config):
    """Validate project structure and permissions."""
    errors = []
    warnings = []

    for dir_name in REQUIRED_DIRECTORIES:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            errors.append(f"Directory '{dir_name}' not found")
        elif not dir_path.is_dir():
            errors.append(f"'{dir_name}' exists but is not a directory")
        else:
            try:
                test_file = dir_path / '.write_test'
                test_file.touch()
                test_file.unlink()
            except (PermissionError, OSError):
                warnings.append(
                    f"Warning: Limited permissions on '{dir_name}' directory"
                )

    content_path = Path('content')
    if not content_path.exists() or not any(content_path.iterdir()):
        warnings.append("No content found in content directory")

    return errors, warnings


class Server:
    """StaticFlow server with optional development features."""

    def __init__(self, config, engine=None, host='localhost', port=8000, 
                 dev_mode=False):
        """
        Initialize the server.

        Args:
            config: Config instance
            engine: Engine instance, if not provided, a new one will be created
            host: Host to bind the server to
            port: Port to bind the server to
            dev_mode: Whether to enable development features
        """
        self.config = config
        self.host = host
        self.port = port
        self.dev_mode = dev_mode

        if engine is None:
            self.engine = Engine(config)
        else:
            self.engine = engine

        source_dir = Path(self.config.get('source_dir', 'content'))
        output_dir = self.config.get('output_dir')
        template_dir = Path(self.config.get('template_dir', 'templates'))
        self.engine.initialize(source_dir, output_dir, template_dir)

        self.app = web.Application()
        self.admin = AdminPanel(config, self.engine)

        if dev_mode:
            initialize_plugins(self.engine)

            errors, warnings = validate_project_structure(self.config)

            if errors:
                error_msg = "\n".join([
                    "Critical errors found:",
                    *[f"• {error}" for error in errors],
                    "\nPlease fix these issues before starting the server:",
                    "1. Make sure you're in the correct project directory",
                    "2. Check if all required directories and files exist",
                    "3. Verify file and directory permissions",
                    "\nProject structure should be:",
                    "project_name/",
                    "├── content/",
                    "├── templates/",
                    "├── static/",
                    f"├── {self.config.get('output_dir', 'output')}/",
                    "└── config.toml"
                ])
                logger.error(error_msg)
                console.print(Panel(
                    error_msg,
                    title="[red]Project Structure Errors[/red]",
                    border_style="red"
                ))
                raise SystemExit(1)

            if warnings:
                warning_msg = "\n".join([
                    "Warnings:",
                    *[f"• {warning}" for warning in warnings]
                ])
                logger.warning(warning_msg)
                console.print(Panel(
                    warning_msg,
                    title="[yellow]Project Structure Warnings[/yellow]",
                    border_style="yellow"
                ))

        self.setup_routes()
        self.setup_templates()

    def setup_templates(self):
        """Setup Jinja2 templates."""
        template_dir = self.config.get('template_dir', 'templates')
        if not template_dir:
            template_dir = 'templates'

        if not isinstance(template_dir, Path):
            template_path = Path(template_dir)
        else:
            template_path = template_dir

        if not template_path.exists():
            template_path.mkdir(parents=True)
            logger.info(f"Created template directory: {template_path}")

        aiohttp_jinja2.setup(
            self.app,
            loader=jinja2.FileSystemLoader(str(template_path))
        )

    def setup_routes(self):
        """Setup server routes."""
        # Admin routes
        self.app.router.add_get('/admin', self.admin_handler)
        self.app.router.add_get('/admin/{tail:.*}', self.admin_handler)
        self.app.router.add_post('/admin/api/{tail:.*}', self.admin_handler)
        self.app.router.add_post('/admin/{tail:.*}', self.admin_handler)

        # Static files
        static_dir = self.config.get('static_dir', 'static')
        if not isinstance(static_dir, Path):
            static_path = Path(static_dir)
        else:
            static_path = static_dir
        
        # Ensure static_dir starts with / for aiohttp
        if not static_dir.startswith('/'):
            static_dir = '/' + static_dir
            
        self.app.router.add_static(static_dir, static_path)

        # Media files - use output/media instead of root media
        output_dir = self.config.get('output_dir', 'output')
        if not isinstance(output_dir, Path):
            output_path = Path(output_dir)
        else:
            output_path = output_dir
            
        media_path = output_path / 'media'
        
        # Create media directory if it doesn't exist
        if not media_path.exists():
            media_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created media directory: {media_path}")
        
        # Ensure media_dir starts with / for aiohttp
        media_dir = '/media'
            
        self.app.router.add_static(media_dir, media_path)

        # All other routes
        self.app.router.add_get('/{tail:.*}', self.handle_request)

    async def admin_redirect(self, request):
        """Redirect /admin to /admin/."""
        return web.HTTPFound('/admin/')

    async def admin_handler(self, request):
        """Handle admin panel requests."""
        return await self.admin.handle_request(request)

    async def handle_request(self, request):
        """Handle regular site requests."""
        path = request.path

        if path == '/':
            path = '/index.html'

        output_dir = self.config.get('output_dir')
        if not isinstance(output_dir, Path):
            output_path = Path(output_dir)
        else:
            output_path = output_dir

        if isinstance(path, Path):
            path = str(path)

        file_path = output_path / path.lstrip('/')

        if not file_path.exists():
            potential_index = file_path / 'index.html'
            if potential_index.exists() and potential_index.is_file():
                file_path = potential_index
            else:
                if self.dev_mode:
                    return web.Response(status=404, text="Not Found")
                else:
                    raise web.HTTPNotFound()

        if file_path.is_dir():
            index_file = file_path / 'index.html'
            if index_file.exists() and index_file.is_file():
                file_path = index_file
            else:
                return web.Response(status=403, text="Forbidden")

        if not file_path.is_file():
            return web.Response(status=403, text="Forbidden")

        content_type = "text/html"
        if str(file_path).endswith(".css"):
            content_type = "text/css"
        elif str(file_path).endswith(".js"):
            content_type = "application/javascript"

        return web.FileResponse(
            file_path, 
            headers={"Content-Type": content_type}
        )

    def run(self):
        """Run the server."""
        if self.dev_mode:
            server_url = f"http://{self.host}:{self.port}"
            console.print(
                Panel.fit(
                    f"[green]Server running at[/green] {server_url}\n"
                    "[dim]Press CTRL+C to stop[/dim]",
                    title="StaticFlow Dev Server"
                )
            )
            web.run_app(
                self.app,
                host=self.host,
                port=self.port,
                print=None
            )
        else:
            server_url = f"http://{self.host}:{self.port}"
            web.run_app(self.app, host=self.host, port=self.port)