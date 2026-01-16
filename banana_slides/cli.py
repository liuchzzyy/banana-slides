"""
Banana Slides CLI - Command-line interface for PPT generation
"""

import os
import sys
import json
import logging
import time
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeRemainingColumn,
)
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from .config import Config, get_config
from .models import db, Project, Page, Task
from .core.generator import AIService, ProjectContext
from .core.file_service import FileService
from .core.exporter import ExportService
from .services.ai_service_manager import get_ai_service
from .services.image_editability import (
    ImageEditabilityService,
    ServiceConfig,
    InpaintProviderFactory,
    InpaintProviderRegistry,
    TextAttributeExtractorFactory,
)
from concurrent.futures import ThreadPoolExecutor, as_completed

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

console = Console()


class CLIDatabase:
    """Database helper for CLI operations"""

    @staticmethod
    def init_db():
        """Initialize database connection"""
        config = get_config()
        db_path = os.path.join(backend_dir, "instance", "database.db")

        # Ensure instance directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Configure SQLAlchemy for CLI
        db_uri = f"sqlite:///{db_path}"
        db.config = {
            "SQLALCHEMY_DATABASE_URI": db_uri,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "SQLALCHEMY_ENGINE_OPTIONS": {
                "connect_args": {"check_same_thread": False, "timeout": 30},
                "pool_pre_ping": True,
                "pool_recycle": 3600,
            },
        }

        # Create app context for database operations
        from flask import Flask

        app = Flask(__name__)
        app.config.update(db.config)
        db.init_app(app)

        with app.app_context():
            db.create_all()
            return app


# Global Flask app for database context
_cli_app = None


def get_cli_app():
    """Get or create Flask app for CLI operations"""
    global _cli_app
    if _cli_app is None:
        _cli_app = CLIDatabase.init_db()
    return _cli_app


def collect_image_paths(paths):
    """Collect all image paths from provided arguments"""
    image_extensions = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
    result = []

    for path_str in paths:
        path = Path(path_str)

        if path.is_file():
            if path.suffix.lower() in image_extensions:
                result.append(str(path.resolve()))
            else:
                logger.warning(f"Skipping non-image file: {path}")
        elif path.is_dir():
            for file in sorted(path.iterdir()):
                if file.suffix.lower() in image_extensions:
                    result.append(str(file.resolve()))
        else:
            logger.warning(f"Path does not exist: {path}")

    return result


def create_service_config(extractor_method="hybrid", inpaint_method="hybrid"):
    """Create service configuration"""
    # Configure based on method
    use_hybrid_extractor = extractor_method == "hybrid"
    use_hybrid_inpaint = inpaint_method == "hybrid"

    logger.info(f"Config: Extractor={extractor_method}, Inpaint={inpaint_method}")

    config = ServiceConfig.from_defaults(
        use_hybrid_extractor=use_hybrid_extractor,
        use_hybrid_inpaint=use_hybrid_inpaint,
        max_depth=1,
    )

    # Configure non-hybrid inpaint methods
    if inpaint_method != "hybrid":
        inpaint_registry = InpaintProviderRegistry()

        if inpaint_method == "generative":
            provider = InpaintProviderFactory.create_generative_edit_provider()
            inpaint_registry.register_default(provider)
            logger.info("Using generative inpainting (calls text-to-image API)")
        elif inpaint_method == "baidu":
            provider = InpaintProviderFactory.create_baidu_inpaint_provider()
            if provider:
                inpaint_registry.register_default(provider)
                logger.info("Using Baidu inpainting")
            else:
                logger.warning(
                    "Baidu inpainting unavailable, falling back to generative"
                )
                provider = InpaintProviderFactory.create_generative_edit_provider()
                inpaint_registry.register_default(provider)

        config.inpaint_registry = inpaint_registry

    return config


@click.group()
def cli():
    """Banana Slides CLI - AI-powered PPT generation tool"""
    pass


@cli.command()
@click.option(
    "--prompt", "-p", required=True, help="PPT generation prompt (idea/description)"
)
@click.option(
    "--output",
    "-o",
    required=False,
    help="Output PPTX file path (default: {project_name}.pptx)",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["pptx", "pdf"]),
    default="pptx",
    help="Output format",
)
@click.option(
    "--template",
    "-t",
    type=click.Path(exists=True),
    help="Template image file for style reference",
)
@click.option(
    "--language",
    "-l",
    type=click.Choice(["zh", "en", "ja", "auto"]),
    default="auto",
    help="Output language",
)
@click.option(
    "--pages", "-n", type=int, default=None, help="Number of pages (optional)"
)
def create(
    prompt: str,
    output: Optional[str],
    format: str,
    template: Optional[str],
    language: str,
    pages: Optional[int],
):
    """
    Generate PPT from a prompt

    Example:
        banana-slides create --prompt "Create a presentation about climate change" --output climate.pptx
    """
    rprint(
        Panel.fit(
            f"[bold blue]🍌 Banana Slides CLI[/bold blue]\nGenerating PPT from prompt..."
        )
    )

    app = get_cli_app()
    with app.app_context():
        # Initialize services
        ai_service = get_ai_service()

        # Determine output filename
        if output:
            output_path = Path(output)
        else:
            # Generate filename from prompt (first 20 chars, sanitized)
            safe_name = "".join(
                c if c.isalnum() or c in " _-" else "_" for c in prompt[:20]
            )
            output_path = Path(f"{safe_name}.{format}")

        config = get_config()
        file_service = FileService(
            upload_folder=config.UPLOAD_FOLDER,
            allowed_extensions=config.ALLOWED_EXTENSIONS,
        )

        # Step 1: Create project
        rprint("\n[yellow]Step 1/4[/yellow]: Creating project...")

        project = Project(
            creation_type="idea",
            idea_prompt=prompt,
            status="DRAFT",
            extra_requirements=""
            if pages is None
            else f"Generate approximately {pages} pages",
        )
        db.session.add(project)
        db.session.commit()

        rprint(f"  ✓ Created project [cyan]{project.id}[/cyan]")

        # Step 2: Upload template (if provided)
        template_path = None
        if template:
            rprint("\n[yellow]Step 2/4[/yellow]: Uploading template...")
            try:
                template_path = file_service.save_template_image(template, project.id)
                rprint(f"  ✓ Template saved")
            except Exception as e:
                rprint(f"  [red]✗ Failed to save template: {e}[/red]")
                template_path = None

        # Step 3: Generate outline
        rprint("\n[yellow]Step 3/4[/yellow]: Generating outline...")

        project_context = ProjectContext(project)
        outline = ai_service.generate_outline(project_context, language=language)

        # Flatten outline and create pages
        pages_data = ai_service.flatten_outline(outline)
        rprint(f"  ✓ Generated {len(pages_data)} pages")

        for idx, page_data in enumerate(pages_data):
            page = Page(
                project_id=project.id,
                order_index=idx,
                outline_content=page_data,
                status="DRAFT",
            )
            db.session.add(page)

        db.session.commit()

        # Step 4: Generate descriptions and images
        rprint("\n[yellow]Step 4/4[/yellow]: Generating PPT content...")

        # Use progress bar for generation
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console,
        ) as progress:
            # Generate descriptions
            desc_task = progress.add_task(
                "Generating descriptions...", total=len(pages_data)
            )
            for idx, page_data in enumerate(pages_data):
                page = Page.query.filter_by(
                    project_id=project.id, order_index=idx
                ).first()

                desc_text = ai_service.generate_page_description(
                    project_context=project_context,
                    outline=outline,
                    page_outline=page_data,
                    page_index=idx + 1,
                    language=language,
                )

                page.set_description_content(
                    {
                        "text": desc_text,
                        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    }
                )
                page.status = "DESCRIPTION_GENERATED"
                db.session.commit()

                progress.update(desc_task, advance=1)

            # Generate images
            img_task = progress.add_task("Generating images...", total=len(pages_data))
            for idx, page_data in enumerate(pages_data):
                page = Page.query.filter_by(
                    project_id=project.id, order_index=idx
                ).first()

                desc_content = page.get_description_content()
                desc_text = desc_content.get("text", "")

                # Extract material images from description
                additional_ref_images = ai_service.extract_image_urls_from_markdown(
                    desc_text
                )

                # Generate image prompt
                prompt_text = ai_service.generate_image_prompt(
                    outline=outline,
                    page=page_data,
                    page_desc=desc_text,
                    page_index=idx + 1,
                    has_material_images=bool(additional_ref_images),
                    language=language,
                    has_template=bool(template_path),
                )

                # Generate image
                image = ai_service.generate_image(
                    prompt=prompt_text,
                    ref_image_path=template_path,
                    aspect_ratio=config.DEFAULT_ASPECT_RATIO,
                    resolution=config.DEFAULT_RESOLUTION,
                    additional_ref_images=additional_ref_images
                    if additional_ref_images
                    else None,
                )

                if image:
                    image_path = file_service.save_generated_image(
                        image, project.id, page.id
                    )
                    page.generated_image_path = image_path
                    page.status = "COMPLETED"
                else:
                    page.status = "FAILED"
                    rprint(
                        f"  [red]✗ Failed to generate image for page {idx + 1}[/red]"
                    )

                db.session.commit()
                progress.update(img_task, advance=1)

        # Export to PPTX/PDF
        rprint(f"\n[yellow]Exporting to {format.upper()}...[/yellow]")

        pages = (
            Page.query.filter_by(project_id=project.id).order_by(Page.order_index).all()
        )
        image_paths = []

        for page in pages:
            if page.generated_image_path:
                abs_path = file_service.get_absolute_path(page.generated_image_path)
                if os.path.exists(abs_path):
                    image_paths.append(abs_path)

        if not image_paths:
            rprint("[red]✗ No images generated, cannot export[/red]")
            return

        try:
            if format == "pptx":
                ExportService.create_pptx_from_images(image_paths, str(output_path))
            else:  # pdf
                ExportService.create_pdf_from_images(image_paths, str(output_path))

            rprint(
                f"\n[green]✓ Success! PPT exported to: [cyan]{output_path.absolute()}[/cyan][/green]"
            )
            rprint(f"  [dim]Project ID: {project.id}[/dim]")
            rprint(f"  [dim]Pages: {len(image_paths)}[/dim]")
        except Exception as e:
            rprint(f"\n[red]✗ Failed to export: {e}[/red]")


@cli.command()
@click.argument("project_id")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["pptx", "pdf"]),
    default="pptx",
    help="Output format",
)
@click.option(
    "--output", "-o", help="Output file path (default: project_name.{format})"
)
def export(project_id: str, format: str, output: Optional[str]):
    """
    Export an existing project to PPTX or PDF

    Example:
        banana-slides export abc123 --format pdf --output presentation.pdf
    """
    rprint(
        Panel.fit(
            f"[bold blue]🍌 Banana Slides CLI[/bold blue]\nExporting project {project_id}..."
        )
    )

    app = get_cli_app()
    with app.app_context():
        config = get_config()
        file_service = FileService(
            upload_folder=config.UPLOAD_FOLDER,
            allowed_extensions=config.ALLOWED_EXTENSIONS,
        )

        # Get project
        project = Project.query.get(project_id)
        if not project:
            rprint(f"[red]✗ Project {project_id} not found[/red]")
            return

        # Get pages
        pages = (
            Page.query.filter_by(project_id=project.id).order_by(Page.order_index).all()
        )
        if not pages:
            rprint(f"[red]✗ No pages found for project {project_id}[/red]")
            return

        rprint(f"  Found [cyan]{len(pages)}[/cyan] pages")

        # Collect image paths
        image_paths = []
        for page in pages:
            if page.generated_image_path:
                abs_path = file_service.get_absolute_path(page.generated_image_path)
                if os.path.exists(abs_path):
                    image_paths.append(abs_path)
                else:
                    rprint(f"  [yellow]⚠ Image not found: {abs_path}[/yellow]")

        if not image_paths:
            rprint("[red]✗ No valid images found for export[/red]")
            return

        # Determine output path
        if output:
            output_path = Path(output)
        else:
            output_path = Path(f"project_{project_id}.{format}")

        # Export
        rprint(f"\n[yellow]Exporting to {format.upper()}...[/yellow]")

        try:
            if format == "pptx":
                ExportService.create_pptx_from_images(image_paths, str(output_path))
            else:  # pdf
                ExportService.create_pdf_from_images(image_paths, str(output_path))

            rprint(
                f"\n[green]✓ Exported to: [cyan]{output_path.absolute()}[/cyan][/green]"
            )
        except Exception as e:
            rprint(f"\n[red]✗ Export failed: {e}[/red]")


@cli.command()
@click.argument("images", nargs=-1, required=True, type=click.Path(exists=True))
@click.option(
    "--output",
    "-o",
    default="output_editable.pptx",
    help="Output PPTX file path (default: output_editable.pptx)",
)
@click.option(
    "--extractor",
    type=click.Choice(["mineru", "hybrid"]),
    default="hybrid",
    help="Component extraction method (default: hybrid)",
)
@click.option(
    "--inpaint",
    type=click.Choice(["generative", "baidu", "hybrid"]),
    default="hybrid",
    help="Background inpainting method (default: hybrid)",
)
@click.option(
    "--extract-styles/--no-extract-styles",
    default=True,
    help="Extract text styles (bold, color, etc.)",
)
def convert(images, output, extractor, inpaint, extract_styles):
    """
    Convert images to editable PPTX

    Example:
        banana-slides convert slide1.png slide2.png -o presentation.pptx
        banana-slides convert ./slides/ --extractor hybrid
    """
    rprint(
        Panel.fit(
            f"[bold blue]🍌 Banana Slides CLI[/bold blue]\nConverting images to editable PPTX..."
        )
    )

    image_paths = collect_image_paths(images)
    if not image_paths:
        rprint("[red]✗ No valid images found[/red]")
        return

    rprint(f"Found [cyan]{len(image_paths)}[/cyan] images")

    app = get_cli_app()
    with app.app_context():
        try:
            # 1. Initialize Service
            rprint("\n[yellow]Step 1/3[/yellow]: Analyzing image structure...")
            service_config = create_service_config(extractor, inpaint)
            service = ImageEditabilityService(service_config)

            # 2. Analyze images
            editable_images = []
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = {
                    executor.submit(service.make_image_editable, path): idx
                    for idx, path in enumerate(image_paths)
                }

                results = [None] * len(image_paths)
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    console=console,
                ) as progress:
                    task = progress.add_task("Analyzing...", total=len(image_paths))

                    for future in as_completed(futures):
                        idx = futures[future]
                        try:
                            results[idx] = future.result()
                            progress.update(task, advance=1)
                        except Exception as e:
                            logger.error(
                                f"Failed to analyze image {image_paths[idx]}: {e}"
                            )
                            raise

            editable_images = results

            # 3. Text Attributes
            text_attribute_extractor = None
            if extract_styles:
                rprint("\n[yellow]Step 2/3[/yellow]: Extracting text styles...")
                try:
                    text_attribute_extractor = (
                        TextAttributeExtractorFactory.create_caption_model_extractor()
                    )
                except Exception as e:
                    logger.warning(f"Failed to create text extractor: {e}")
            else:
                rprint("\n[yellow]Step 2/3[/yellow]: Skipping text style extraction")

            # 4. Generate PPTX
            rprint("\n[yellow]Step 3/3[/yellow]: Generating PPTX...")

            # Determine slide size
            ASPECT_RATIO_16_9 = 16 / 9
            ASPECT_RATIO_TOLERANCE = 0.02
            min_width = float("inf")
            min_height = float("inf")

            for idx, img in enumerate(editable_images):
                aspect_ratio = img.width / img.height
                ratio_diff = abs(aspect_ratio - ASPECT_RATIO_16_9) / ASPECT_RATIO_16_9

                if ratio_diff > ASPECT_RATIO_TOLERANCE:
                    logger.warning(
                        f"Image {idx + 1} is not 16:9 (Ratio: {aspect_ratio:.2f})"
                    )

                min_width = min(min_width, img.width)
                min_height = min(min_height, img.height)

            if not editable_images:
                min_width, min_height = 1920, 1080

            slide_width = int(min_width)
            slide_height = int(min_height)

            def progress_callback(step, message, percent):
                logger.info(f"[{percent}%] {step}: {message}")

            output_path = Path(output)
            if output_path.exists():
                stem = output_path.stem
                suffix = output_path.suffix
                output_path = output_path.with_name(f"{stem}_1{suffix}")
                rprint(
                    f"[yellow]Output file exists, renaming to: {output_path}[/yellow]"
                )

            ExportService.create_editable_pptx_with_recursive_analysis(
                editable_images=editable_images,
                output_file=str(output_path),
                slide_width_pixels=slide_width,
                slide_height_pixels=slide_height,
                text_attribute_extractor=text_attribute_extractor,
                progress_callback=progress_callback,
            )

            rprint(
                f"\n[green]✓ Success! PPT exported to: [cyan]{output_path.absolute()}[/cyan][/green]"
            )

        except Exception as e:
            rprint(f"\n[red]✗ Conversion failed: {e}[/red]")
            logger.exception("Conversion failed")


@cli.group()
def config():
    """Manage configuration (settings in .env file)"""
    pass


@config.command("show")
def config_show():
    """Show current configuration"""
    rprint(Panel.fit("[bold blue]🍌 Banana Slides Configuration[/bold blue]"))

    config = get_config()

    # Create a nice table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    table.add_column("Source", style="dim")

    settings = [
        (
            "OPENAI_API_KEY",
            config.OPENAI_API_KEY[:10] + "***"
            if config.OPENAI_API_KEY
            else "(not set)",
            ".env",
        ),
        ("OPENAI_API_BASE", config.OPENAI_API_BASE, ".env"),
        ("TEXT_MODEL", config.TEXT_MODEL or "(not set)", ".env"),
        ("IMAGE_MODEL", config.IMAGE_MODEL or "(not set)", ".env"),
        ("OUTPUT_LANGUAGE", config.OUTPUT_LANGUAGE, ".env"),
        ("UPLOAD_FOLDER", config.UPLOAD_FOLDER, "config"),
        ("DATABASE", config.SQLALCHEMY_DATABASE_URI, "config"),
    ]

    for setting, value, source in settings:
        table.add_row(setting, value, source)

    console.print(table)


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str):
    """
    Set a configuration value in .env file

    Example:
        banana-slides config set TEXT_MODEL gpt-4
        banana-slides config set IMAGE_MODEL dall-e-3
    """
    env_file = Path(__file__).parent.parent / ".env"

    if not env_file.exists():
        rprint(f"[red]✗ .env file not found at {env_file}[/red]")
        rprint("[yellow]Please copy .env.example to .env first[/yellow]")
        return

    # Read existing .env
    lines = env_file.read_text(encoding="utf-8").splitlines()
    updated = False
    new_lines = []

    key_upper = key.upper()

    # Find and update existing key
    for line in lines:
        if line.strip().startswith(key_upper + "="):
            new_lines.append(f"{key_upper}={value}")
            updated = True
        elif line.strip() and not line.strip().startswith("#"):
            new_lines.append(line)
        else:
            new_lines.append(line)

    # Add new key if not found
    if not updated:
        new_lines.append(f"{key_upper}={value}")

    # Write back
    env_file.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

    rprint(f"[green]✓ Set {key_upper}={value}[/green]")
    rprint(
        "[yellow]Note: You may need to restart any running services for changes to take effect[/yellow]"
    )


@config.command("validate")
def config_validate():
    """Validate configuration and test API connection"""
    rprint(Panel.fit("[bold blue]🍌 Validating Configuration[/bold blue]"))

    config = get_config()
    has_errors = False

    # Check API key
    if not config.OPENAI_API_KEY:
        rprint("[red]✗ OPENAI_API_KEY is not set[/red]")
        has_errors = True
    else:
        rprint("[green]✓ OPENAI_API_KEY is set[/green]")

    # Check models
    if not config.TEXT_MODEL:
        rprint("[red]✗ TEXT_MODEL is not set[/red]")
        has_errors = True
    else:
        rprint(f"[green]✓ TEXT_MODEL: {config.TEXT_MODEL}[/green]")

    if not config.IMAGE_MODEL:
        rprint("[red]✗ IMAGE_MODEL is not set[/red]")
        has_errors = True
    else:
        rprint(f"[green]✓ IMAGE_MODEL: {config.IMAGE_MODEL}[/green]")

    # Check API base
    rprint(f"[green]✓ API Base: {config.OPENAI_API_BASE}[/green]")

    # Test API connection
    if not has_errors:
        rprint("\n[yellow]Testing API connection...[/yellow]")
        try:
            ai_service = initialize_ai_service()
            # Try a simple generation
            test_result = ai_service.text_provider.generate_text(
                "Say 'OK' in one word.", thinking_budget=100
            )
            rprint(
                f"[green]✓ API connection successful! Response: {test_result.strip()}[/green]"
            )
        except Exception as e:
            rprint(f"[red]✗ API connection failed: {e}[/red]")
            has_errors = True

    if has_errors:
        rprint("\n[red]Configuration has errors. Please check your .env file.[/red]")
        sys.exit(1)
    else:
        rprint("\n[green]✓ Configuration is valid![/green]")


@cli.command()
def status():
    """Show running tasks and recent projects"""
    rprint(Panel.fit("[bold blue]🍌 Banana Slides Status[/bold blue]"))

    app = get_cli_app()
    with app.app_context():
        # Show active tasks
        tasks = Task.query.filter(Task.status.in_(["PENDING", "PROCESSING"])).all()

        if tasks:
            rprint("\n[bold yellow]Active Tasks:[/bold yellow]")
            for task in tasks:
                progress = task.get_progress()
                completed = progress.get("completed", 0)
                total = progress.get("total", 1)
                percent = int((completed / total) * 100) if total > 0 else 0

                rprint(f"  [cyan]{task.id}[/cyan] - {task.task_type}")
                rprint(
                    f"    Status: {task.status} | Progress: {percent}% ({completed}/{total})"
                )
        else:
            rprint("\n[dim]No active tasks[/dim]")

        # Show recent projects
        rprint("\n[bold yellow]Recent Projects:[/bold yellow]")

        projects = Project.query.order_by(Project.created_at.desc()).limit(5).all()

        if not projects:
            rprint("  [dim]No projects found[/dim]")
        else:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("ID", style="cyan")
            table.add_column("Title", style="green")
            table.add_column("Status", style="yellow")
            table.add_column("Pages", style="blue")
            table.add_column("Created", style="dim")

            for project in projects:
                page_count = Page.query.filter_by(project_id=project.id).count()
                title = (
                    project.idea_prompt[:30] + "..."
                    if len(project.idea_prompt or "") > 30
                    else project.idea_prompt or "Untitled"
                )

                table.add_row(
                    project.id,
                    title,
                    project.status,
                    str(page_count),
                    project.created_at.strftime("%Y-%m-%d %H:%M"),
                )

            console.print(table)


if __name__ == "__main__":
    cli()
