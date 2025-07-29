import click
from pathlib import Path
from typing import Optional
from .scanner import RepoScanner
from .parser import GitignoreParser, LlmMdParser
from .generator import MarkdownGenerator


@click.command()
@click.argument('repo_path', type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path))
@click.option('-o', '--output', type=click.Path(path_type=Path), default='llm-context.md',
              help='Output markdown file path (default: llm-context.md)')
@click.option('-c', '--config', type=click.Path(exists=True, path_type=Path),
              help='Override path to llm.md configuration file (default: auto-detect in repo root)')
@click.option('-v', '--verbose', is_flag=True, help='Enable verbose output')
def main(repo_path: Path, output: Path, config: Optional[Path], verbose: bool):
    """Generate LLM context from a GitHub repository.
    
    This tool scans through files in a repository and creates a single markdown
    file containing all relevant code, with a table of contents for easy navigation.
    
    Files are filtered based on .gitignore rules and optional llm.md configuration.
    If an llm.md file exists in the repository root, it will be used automatically
    unless overridden with the -c option.
    """
    click.echo(f"Scanning repository: {repo_path}")
    
    # Initialize parsers
    gitignore_parser = GitignoreParser(repo_path)
    
    # Determine which llm.md config to use
    if config:
        # User explicitly provided a config file
        llm_config_path = config
        click.echo(f"Using specified llm.md config: {llm_config_path}")
    else:
        # Check if llm.md exists in the repo root
        default_llm_path = repo_path / 'llm.md'
        if default_llm_path.exists():
            llm_config_path = default_llm_path
            click.echo(f"Found llm.md in repository root: {llm_config_path}")
        else:
            llm_config_path = None
            if verbose:
                click.echo("No llm.md file found in repository root")
    
    llm_parser = LlmMdParser(llm_config_path)
    
    # Create scanner with filtering rules
    scanner = RepoScanner(repo_path, gitignore_parser, llm_parser, verbose=verbose)
    
    # Scan files
    files = scanner.scan()
    
    if not files:
        click.echo("No files found matching the criteria.", err=True)
        return
    
    click.echo(f"Found {len(files)} files to process")
    
    # Generate markdown
    generator = MarkdownGenerator()
    content = generator.generate(files, repo_path)
    
    # Write output
    output.write_text(content, encoding='utf-8')
    click.echo(f"✓ Generated context file: {output}")
    
    if verbose:
        click.echo(f"  Total size: {len(content):,} characters")
        click.echo(f"  Files included: {len(files)}")


if __name__ == '__main__':
    main()