# canonmap/cli.py
import click
import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
import spacy
import sys
import subprocess

from canonmap.config import CanonMapConfig
from canonmap.utils.model_loader import FlexibleModelLoader

@click.group()
def cli():
    """CanonMap CLI tools for model management and configuration."""
    pass

@cli.command()
@click.argument("model", default="all-MiniLM-L6-v2")
@click.option("--model-dir", help="Custom model directory for caching")
@click.option("--offline", is_flag=True, help="Download in offline mode")
def download_model(model, model_dir, offline):
    """
    Download the given Sentence-Transformer into the local cache.
    """
    click.echo(f"⏬ Downloading {model}…")
    
    # Set up configuration
    config = CanonMapConfig()
    if model_dir:
        config.model_dir = Path(model_dir)
    if offline:
        config.offline_mode = True
    
    # Use model loader for consistent behavior
    model_loader = FlexibleModelLoader(config)
    
    try:
        model_loader.load_sentence_transformer(model)
        click.echo(f"✅ Cached {model} successfully.")
    except Exception as e:
        click.echo(f"❌ Failed to download {model}: {e}")
        sys.exit(1)

@cli.command()
@click.argument("model", default="en_core_web_sm")
@click.option("--spacy-model-dir", help="Custom spaCy model directory")
@click.option("--offline", is_flag=True, help="Download in offline mode")
def download_spacy_model(model, spacy_model_dir, offline):
    """
    Download the given spaCy model into the local cache.
    """
    click.echo(f"⏬ Downloading spaCy model {model}…")
    
    # Set up configuration
    config = CanonMapConfig()
    if spacy_model_dir:
        config.spacy_model_dir = Path(spacy_model_dir)
    if offline:
        config.offline_mode = True
    
    # Use model loader for consistent behavior
    model_loader = FlexibleModelLoader(config)
    
    try:
        model_loader.load_spacy_model(model)
        click.echo(f"✅ Cached spaCy model {model} successfully.")
    except Exception as e:
        click.echo(f"❌ Failed to download spaCy model {model}: {e}")
        sys.exit(1)

@cli.command()
def show_config():
    """
    Show current CanonMap configuration.
    """
    config = CanonMapConfig()
    click.echo("📋 CanonMap Configuration:")
    click.echo(f"  Model Directory: {config.model_dir}")
    click.echo(f"  spaCy Model Directory: {config.spacy_model_dir}")
    click.echo(f"  Artifacts Directory: {config.artifacts_dir}")
    click.echo(f"  Offline Mode: {config.offline_mode}")
    click.echo(f"  SentenceTransformer Model: {config.sentence_transformer_model}")
    click.echo(f"  spaCy Model: {config.spacy_model}")

@cli.command()
@click.option("--model-dir", help="Custom model directory")
@click.option("--spacy-model-dir", help="Custom spaCy model directory")
def setup_directories(model_dir, spacy_model_dir):
    """
    Create CanonMap directories and set up initial structure.
    """
    config = CanonMapConfig()
    
    if model_dir:
        config.model_dir = Path(model_dir)
    if spacy_model_dir:
        config.spacy_model_dir = Path(spacy_model_dir)
    
    # Create directories
    config.model_dir.mkdir(parents=True, exist_ok=True)
    config.spacy_model_dir.mkdir(parents=True, exist_ok=True)
    config.artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    click.echo(f"✅ Created directories:")
    click.echo(f"  Model Directory: {config.model_dir}")
    click.echo(f"  spaCy Model Directory: {config.spacy_model_dir}")
    click.echo(f"  Artifacts Directory: {config.artifacts_dir}")

# Backward compatibility - keep the original function name
download_model_command = download_model

# in setup.py or pyproject.toml under [tool.poetry.scripts] / entry_points:
#   canonmap-download-model = canonmap.cli:download_model