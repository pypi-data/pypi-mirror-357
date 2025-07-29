import sys
from pathlib import Path
from typing import cast

import typer
import torch
from transformers import pipeline
from transformers.modeling_utils import PreTrainedModel
from transformers.tokenization_utils import PreTrainedTokenizer

from . import __version__
from .extract import extract_embeddings
from .similarity import build_similarity
from .wrap_model import load_wrapped_model as _attach_layer
from .wrapper import load_wrapped_model
from .logits import SRLogitsProcessor
from .utils import download_checkpoint
from .safetensors import split_file, merge_to_file

app = typer.Typer(help="Meaning-Informed Next-token Transformation CLI")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        help="Show the package version and exit.",
        is_eager=True,
    ),
) -> None:
    """Entry point for the CLI.

    Parameters
    ----------
    ctx:
        Invocation context provided by Typer.
    version:
        When ``True``, print the package version and exit.
    """
    if version:
        typer.echo(__version__)
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@app.command()
def pick(source: str, dest: str = ".") -> None:
    """Download a checkpoint from Hugging Face.

    Parameters
    ----------
    source:
        Hugging Face model ID or direct URL to a checkpoint or index file.
    dest:
        Directory in which to store the downloaded ``model.safetensors``.
    """

    path = download_checkpoint(source, dest)
    typer.echo(str(path))


@app.command()
def extract(model_path: str, output_path: str) -> None:
    """Extract embedding matrix from a checkpoint.

    Parameters
    ----------
    model_path:
        Path to the model checkpoint containing embeddings. A
        ``*.safetensors.index.json`` file automatically loads and merges shards.
    output_path:
        File in which to store the extracted embeddings.
    """

    extract_embeddings(model_path, output_path)


@app.command()
def chop(
    checkpoint: str,
    output_dir: str,
    shards: int | None = typer.Option(None, "--shards", "-n"),
    size_mb: int | None = typer.Option(None, "--size-mb", "-s"),
) -> None:
    """Split a checkpoint into multiple shards."""

    size_bytes = size_mb * 1024 * 1024 if size_mb is not None else None
    split_file(
        checkpoint, num_shards=shards, shard_size=size_bytes, output_dir=output_dir
    )
    typer.echo(f"Shards written to {output_dir}")


@app.command()
def blend(
    embedding_path: str,
    output_path: str,
    similarity: str | None = typer.Option(
        None, "--similarity", "-s", help="Reuse existing matrix if available"
    ),
    cpu: bool = typer.Option(
        False, "--cpu", help="Force CPU even if a GPU is available"
    ),
    gpu: int | None = typer.Option(None, "--gpu", help="Select GPU index to use"),
    sdk: str | None = typer.Option(
        None,
        "--sdk",
        help="Acceleration backend (CUDA, Vulkan, ZLUDA, etc.)",
    ),
    tau: float = typer.Option(
        1e-4,
        "--tau",
        help="Sparsity threshold applied to similarity values",
    ),
) -> None:
    """Compute or reuse a token similarity matrix.

    Parameters
    ----------
    embedding_path:
        File containing token embeddings.
    output_path:
        Destination for the resulting similarity matrix.
    similarity:
        Optional existing matrix to reuse if present.
    cpu:
        Force CPU even if a GPU is available.
    gpu:
        GPU index to use when ``cpu`` is ``False``.
    sdk:
        Acceleration backend (``cuda``, ``vulkan``, etc.).
    tau:
        Sparsity threshold applied to similarity values.
    """

    device = "cpu"
    if not cpu:
        gpu_index = gpu if gpu is not None else 0
        sdks = [sdk.lower()] if sdk is not None else ["cuda", "vulkan"]
        for name in sdks:
            if name == "cuda":
                if torch.cuda.is_available():
                    device = f"cuda:{gpu_index}"
                    break
            elif name == "vulkan":
                # TODO: check for Vulkan availability
                pass
            elif name == "zluda":
                # TODO: check for ZLUDA availability
                pass

    build_similarity(embedding_path, similarity, output_path, device, tau)


@app.command()
def crush(index: str, output: str) -> None:
    """Merge a sharded checkpoint into a single file.

    Parameters
    ----------
    index:
        Path to a ``*.safetensors.index.json`` file.
    output:
        Destination for the merged ``.safetensors`` checkpoint.
    """

    merge_to_file(index, output)


@app.command()
def infuse(
    model_path: str,
    similarity: str,
    output: str,
    alpha: float = typer.Option(0.0, help="Demotion strength for original logits"),
) -> None:
    """Load a model and attach a redistribution layer.

    Parameters
    ----------
    model_path:
        Local directory containing the model to modify.
    similarity:
        File containing the similarity tensor to load.
    output:
        Directory where the modified model will be saved.
    alpha:
        Demotion strength for the original logits.
    """

    mpath = Path(model_path)
    if not mpath.exists() or not mpath.is_dir():
        raise typer.BadParameter(
            f"model_path must be an existing directory: {model_path}"
        )

    model = cast(PreTrainedModel, _attach_layer(str(mpath), similarity, alpha))
    Path(output).mkdir(parents=True, exist_ok=True)
    model.save_pretrained(output)
    typer.echo(f"Model infused with similarity data saved to {output}")


@app.command(name="brew")
def generate(
    model: str = typer.Option(..., "--model", help="Model identifier or path"),
    similarity: str = typer.Option(..., "--similarity", help="Similarity tensor"),
    alpha: float = typer.Option(0.0, "--alpha", help="Demotion strength"),
    prompt: str | None = typer.Option("The quick fox jumps over the ", "--prompt"),
    interactive: bool = typer.Option(
        False,
        "--interactive",
        "-i",
        help="Read prompts from stdin until EOF",
    ),
) -> None:
    """Generate text using a model wrapped with the SR layer.

    Parameters
    ----------
    model:
        Name or path of the model to load.
    similarity:
        Path to the similarity tensor to apply.
    prompt:
        Optional prompt passed directly to the model.
    interactive:
        If ``True``, read prompts from ``stdin`` until EOF.
    """

    mdl, tokenizer, layer = load_wrapped_model(model, similarity, alpha)
    device = 0 if torch.cuda.is_available() else -1
    proc = SRLogitsProcessor(layer, alpha)
    pipe = pipeline(
        "text-generation",
        model=cast(PreTrainedModel, mdl),
        tokenizer=cast(PreTrainedTokenizer, tokenizer),
        device=device,
    )

    def run(p: str) -> None:
        outputs = pipe(p, logits_processor=[proc])
        typer.echo(outputs[0]["generated_text"])

    if prompt is not None and not interactive:
        run(prompt)
    else:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                break
            run(line)


if __name__ == "__main__":
    app()
