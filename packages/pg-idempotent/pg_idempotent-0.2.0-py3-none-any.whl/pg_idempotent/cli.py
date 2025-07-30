"""PG Idempotent CLI."""

import typer
from pathlib import Path
from typing import Optional, List
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

from .transformer.transformer import SQLTransformer
from .utils.file_utils import FileOperations

app = typer.Typer(help="PostgreSQL Idempotent Migration Tool")
console = Console()


@app.command()
def transform(
    input_file: Path = typer.Argument(..., help="Input SQL file to transform"),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file for transformed SQL"),
    backup: bool = typer.Option(True, "--backup/--no-backup", help="Create backup of input file"),
    validate: bool = typer.Option(True, "--validate/--no-validate", help="Validate transformed SQL"),
    stats: bool = typer.Option(False, "--stats", help="Show transformation statistics"),
) -> None:
    """Transform SQL file to idempotent version."""
    
    if not input_file.exists():
        rprint(f"[red]Error:[/red] File not found: {input_file}")
        raise typer.Exit(1)
    
    # Create transformer
    transformer = SQLTransformer()
    
    # Show stats if requested
    if stats:
        with open(input_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        transformation_stats = transformer.get_transformation_stats(sql_content)
        _display_stats(transformation_stats)
    
    # Create backup if requested
    if backup and not output_file:
        backup_file = input_file.with_suffix(f"{input_file.suffix}.backup")
        backup_file.write_text(input_file.read_text())
        rprint(f"[green]✓[/green] Backup created: {backup_file}")
    
    # Determine output file
    if not output_file:
        output_file = input_file
    
    # Transform file
    result = transformer.transform_file(str(input_file), str(output_file))
    
    if not result.success:
        rprint(f"[red]Error:[/red] Transformation failed")
        for error in result.errors:
            rprint(f"  • {error}")
        raise typer.Exit(1)
    
    # Display results
    rprint(f"[green]✓[/green] Transformation completed")
    rprint(f"  • Processed {result.statement_count} statements")
    rprint(f"  • Transformed {result.transformed_count} statements")
    
    if result.warnings:
        rprint(f"[yellow]Warnings:[/yellow]")
        for warning in result.warnings:
            rprint(f"  • {warning}")
    
    if result.errors:
        rprint(f"[red]Errors:[/red]")
        for error in result.errors:
            rprint(f"  • {error}")
    
    # Validate if requested
    if validate:
        validation = transformer.validate_transformed_sql(result.transformed_sql)
        if not validation['valid']:
            rprint(f"[yellow]Validation issues found:[/yellow]")
            for issue in validation['issues']:
                rprint(f"  • {issue}")
        else:
            rprint(f"[green]✓[/green] Validation passed")
    
    rprint(f"[green]Output written to:[/green] {output_file}")


@app.command()
def check(
    input_file: Path = typer.Argument(..., help="SQL file to analyze"),
) -> None:
    """Analyze SQL file without transforming."""
    
    if not input_file.exists():
        rprint(f"[red]Error:[/red] File not found: {input_file}")
        raise typer.Exit(1)
    
    # Create transformer and analyze
    transformer = SQLTransformer()
    
    with open(input_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    stats = transformer.get_transformation_stats(sql_content)
    _display_stats(stats)
    
    # Parse to get detailed info
    statements = transformer.parser.parse_sql(sql_content)
    
    if statements:
        rprint(f"\n[bold]Statement Details:[/bold]")
        
        table = Table()
        table.add_column("Type", style="cyan")
        table.add_column("Object", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Notes")
        
        for stmt in statements[:10]:  # Show first 10
            status = "✓ Idempotent" if stmt.is_idempotent else "⚠ Needs Transform"
            if stmt.error:
                status = "✗ Error"
            elif not stmt.can_be_wrapped:
                status = "⚠ Cannot Wrap"
            
            notes = ""
            if stmt.error:
                notes = stmt.error
            elif not stmt.can_be_wrapped:
                notes = "Cannot be wrapped in DO block"
            
            table.add_row(
                stmt.statement_type,
                stmt.object_name or "N/A",
                status,
                notes
            )
        
        console.print(table)
        
        if len(statements) > 10:
            rprint(f"... and {len(statements) - 10} more statements")


@app.command()
def preview(
    input_file: Path = typer.Argument(..., help="SQL file to preview transformation"),
    lines: int = typer.Option(20, "--lines", "-n", help="Number of lines to show"),
) -> None:
    """Preview transformation without writing to file."""
    
    if not input_file.exists():
        rprint(f"[red]Error:[/red] File not found: {input_file}")
        raise typer.Exit(1)
    
    # Transform and show preview
    transformer = SQLTransformer()
    result = transformer.transform_file(str(input_file))
    
    if not result.success:
        rprint(f"[red]Error:[/red] Transformation failed")
        for error in result.errors:
            rprint(f"  • {error}")
        raise typer.Exit(1)
    
    # Show preview
    preview_lines = result.transformed_sql.split('\n')[:lines]
    preview_content = '\n'.join(preview_lines)
    
    syntax = Syntax(preview_content, "sql", theme="monokai", line_numbers=True)
    
    panel = Panel(
        syntax,
        title=f"Preview: {input_file.name}",
        subtitle=f"Showing first {len(preview_lines)} lines"
    )
    
    console.print(panel)
    
    if len(result.transformed_sql.split('\n')) > lines:
        total_lines = len(result.transformed_sql.split('\n'))
        rprint(f"\n[dim]... and {total_lines - lines} more lines[/dim]")


# Supabase-specific commands
supabase_app = typer.Typer(help="Supabase integration commands")
app.add_typer(supabase_app, name="supabase")


@supabase_app.command(name="check")
def supabase_check(
    directory: Optional[Path] = typer.Argument(None, help="Supabase project directory (auto-detected if not provided)"),
    include_schemas: bool = typer.Option(False, "--schemas", help="Also check declarative schema files"),
) -> None:
    """Check Supabase migration files for idempotency issues."""
    
    # Auto-detect Supabase project
    if directory is None:
        project_root = FileOperations.detect_supabase_project(Path.cwd())
        if project_root is None:
            rprint("[red]Error:[/red] No Supabase project found. Run from a Supabase project directory or specify path.")
            raise typer.Exit(1)
    else:
        project_root = directory
        if not (project_root / "supabase").exists():
            rprint(f"[red]Error:[/red] No Supabase directory found in {project_root}")
            raise typer.Exit(1)
    
    rprint(f"[green]Checking Supabase project:[/green] {project_root}")
    
    # Get project structure
    structure = FileOperations.get_supabase_structure(project_root)
    
    migration_files = structure["migrations"]
    schema_files = structure["schemas"] if include_schemas else []
    
    all_files = migration_files + schema_files
    
    if not all_files:
        rprint("[yellow]No migration files found.[/yellow]")
        return
    
    rprint(f"Found {len(migration_files)} migration files" + 
           (f" and {len(schema_files)} schema files" if schema_files else ""))
    
    transformer = SQLTransformer()
    total_issues = 0
    
    for sql_file in all_files:
        file_type = "migration" if sql_file in migration_files else "schema"
        stats = transformer.get_transformation_stats(sql_file.read_text())
        
        needs_transformation = stats['transformable'] - stats['already_idempotent']
        if needs_transformation > 0:
            total_issues += needs_transformation
            rprint(f"[yellow]⚠ {sql_file.name}[/yellow] ({file_type}): {needs_transformation} statements need transformation")
        else:
            rprint(f"[green]✓ {sql_file.name}[/green] ({file_type}): All statements are idempotent")
    
    if total_issues > 0:
        rprint(f"\n[yellow]Summary:[/yellow] {total_issues} statements across {len(all_files)} files need transformation")
        rprint("Run [bold]pg-idempotent supabase fix[/bold] to make them idempotent")
    else:
        rprint(f"\n[green]✓ All migration files are already idempotent![/green]")


@supabase_app.command(name="fix")
def supabase_fix(
    directory: Optional[Path] = typer.Argument(None, help="Supabase project directory (auto-detected if not provided)"),
    output_dir: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory for fixed files"),
    backup: bool = typer.Option(True, "--backup/--no-backup", help="Create backup of original files"),
    include_schemas: bool = typer.Option(False, "--schemas", help="Also process declarative schema files"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be changed without making changes"),
) -> None:
    """Fix Supabase migration files to be idempotent."""
    
    # Auto-detect Supabase project
    if directory is None:
        project_root = FileOperations.detect_supabase_project(Path.cwd())
        if project_root is None:
            rprint("[red]Error:[/red] No Supabase project found. Run from a Supabase project directory or specify path.")
            raise typer.Exit(1)
    else:
        project_root = directory
    
    rprint(f"[green]Processing Supabase project:[/green] {project_root}")
    
    # Get project structure
    structure = FileOperations.get_supabase_structure(project_root)
    
    migration_files = structure["migrations"]
    schema_files = structure["schemas"] if include_schemas else []
    all_files = migration_files + schema_files
    
    if not all_files:
        rprint("[yellow]No files to process.[/yellow]")
        return
    
    transformer = SQLTransformer()
    processed_files = 0
    transformed_statements = 0
    
    for sql_file in all_files:
        file_type = "migration" if sql_file in migration_files else "schema"
        
        # Determine output path
        if output_dir:
            # Maintain relative structure in output directory
            rel_path = FileOperations.get_relative_path(sql_file, project_root)
            output_path = output_dir / rel_path
            FileOperations.ensure_parent_dir(output_path)
        else:
            output_path = sql_file
        
        # Create backup if needed and not dry run
        if backup and not dry_run and output_path == sql_file:
            try:
                backup_path = FileOperations.backup_file(sql_file)
                rprint(f"[dim]Backup created: {backup_path.name}[/dim]")
            except Exception as e:
                rprint(f"[yellow]Warning:[/yellow] Could not create backup for {sql_file.name}: {e}")
        
        # Transform file
        if dry_run:
            result = transformer.transform_sql(sql_file.read_text())
        else:
            result = transformer.transform_file(str(sql_file), str(output_path) if output_path != sql_file else None)
        
        if result.success and result.transformed_count > 0:
            processed_files += 1
            transformed_statements += result.transformed_count
            status = "[green]✓[/green]" if not dry_run else "[yellow]→[/yellow]"
            rprint(f"{status} {sql_file.name} ({file_type}): {result.transformed_count} statements transformed")
        elif result.transformed_count == 0:
            rprint(f"[dim]- {sql_file.name} ({file_type}): Already idempotent[/dim]")
        else:
            rprint(f"[red]✗ {sql_file.name} ({file_type}): Failed to transform[/red]")
            for error in result.errors:
                rprint(f"  [red]Error:[/red] {error}")
    
    action = "Would transform" if dry_run else "Transformed"
    rprint(f"\n[green]Summary:[/green] {action} {transformed_statements} statements in {processed_files} files")
    
    if dry_run and transformed_statements > 0:
        rprint("Run without --dry-run to apply changes")


@supabase_app.command(name="preview")
def supabase_preview(
    file_path: Path = typer.Argument(..., help="Supabase migration file to preview"),
    lines: int = typer.Option(50, "--lines", "-l", help="Number of lines to show"),
) -> None:
    """Preview transformation of a specific Supabase migration file."""
    
    if not file_path.exists():
        rprint(f"[red]Error:[/red] File not found: {file_path}")
        raise typer.Exit(1)
    
    # Check if it's a Supabase migration
    if not FileOperations.is_supabase_migration(file_path):
        rprint(f"[yellow]Warning:[/yellow] {file_path.name} doesn't appear to be a Supabase migration file")
    
    transformer = SQLTransformer()
    result = transformer.transform_sql(file_path.read_text())
    
    if not result.success:
        rprint("[red]Transformation failed:[/red]")
        for error in result.errors:
            rprint(f"  [red]Error:[/red] {error}")
        raise typer.Exit(1)
    
    # Show preview
    preview_lines = result.transformed_sql.split('\n')[:lines]
    preview_content = '\n'.join(preview_lines)
    
    syntax = Syntax(preview_content, "sql", theme="monokai", line_numbers=True)
    panel = Panel(
        syntax, 
        title=f"Preview: {file_path.name} (Transformed)", 
        subtitle=f"Processed {result.statement_count} statements, transformed {result.transformed_count}",
        expand=False
    )
    
    console.print(panel)
    
    if len(result.transformed_sql.split('\n')) > lines:
        total_lines = len(result.transformed_sql.split('\n'))
        rprint(f"\n[dim]... and {total_lines - lines} more lines[/dim]")


@app.command()
def batch(
    directory: Path = typer.Argument(..., help="Directory containing SQL files"),
    pattern: str = typer.Option("*.sql", "--pattern", "-p", help="File pattern to match"),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir", "-o", help="Output directory"),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Search recursively"),
    supabase: bool = typer.Option(False, "--supabase", help="Process Supabase migration files only"),
) -> None:
    """Transform multiple SQL files in a directory."""
    
    if not directory.exists():
        rprint(f"[red]Error:[/red] Directory not found: {directory}")
        raise typer.Exit(1)
    
    # Find SQL files
    if supabase:
        # Check if it's a Supabase project
        project_root = FileOperations.detect_supabase_project(directory)
        if project_root is None:
            rprint("[red]Error:[/red] No Supabase project found. Use --supabase flag only in Supabase projects.")
            raise typer.Exit(1)
        
        structure = FileOperations.get_supabase_structure(project_root)
        files = structure["migrations"]
        rprint(f"Found {len(files)} Supabase migration files")
    else:
        if recursive:
            files = list(directory.rglob(pattern))
        else:
            files = list(directory.glob(pattern))
        
        if not files:
            rprint(f"[yellow]No files found matching pattern: {pattern}")
            raise typer.Exit(0)
        
        rprint(f"Found {len(files)} files to process")
    
    # Create transformer
    transformer = SQLTransformer()
    
    success_count = 0
    error_count = 0
    
    for file_path in files:
        rprint(f"\n[cyan]Processing:[/cyan] {file_path.name}")
        
        # Calculate output path
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            if recursive:
                # Preserve directory structure
                rel_path = file_path.relative_to(directory)
                out_path = output_dir / rel_path
                out_path.parent.mkdir(parents=True, exist_ok=True)
            else:
                out_path = output_dir / file_path.name
        else:
            out_path = file_path
        
        # Transform file
        result = transformer.transform_file(str(file_path), str(out_path))
        
        if result.success:
            success_count += 1
            rprint(f"  [green]✓[/green] {result.transformed_count}/{result.statement_count} statements transformed")
        else:
            error_count += 1
            rprint(f"  [red]✗[/red] Failed")
            for error in result.errors[:2]:  # Show first 2 errors
                rprint(f"    • {error}")
    
    rprint(f"\n[bold]Summary:[/bold]")
    rprint(f"  • {success_count} files processed successfully")
    rprint(f"  • {error_count} files failed")


def _display_stats(stats: dict) -> None:
    """Display transformation statistics."""
    
    table = Table(title="Transformation Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Count", style="green")
    
    table.add_row("Total Statements", str(stats['total_statements']))
    table.add_row("Already Idempotent", str(stats['already_idempotent']))
    table.add_row("Can Transform", str(stats['transformable']))
    table.add_row("Cannot Transform", str(stats['not_transformable']))
    table.add_row("Errors", str(stats['errors']))
    
    console.print(table)
    
    if stats['by_type']:
        rprint(f"\n[bold]By Statement Type:[/bold]")
        type_table = Table()
        type_table.add_column("Type", style="cyan")
        type_table.add_column("Count", style="green")
        
        for stmt_type, count in sorted(stats['by_type'].items()):
            type_table.add_row(stmt_type, str(count))
        
        console.print(type_table)


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()