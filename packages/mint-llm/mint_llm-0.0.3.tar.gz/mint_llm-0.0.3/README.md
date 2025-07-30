[![Publish to PyPI](https://github.com/Reithan/MINT/actions/workflows/publish.yml/badge.svg?event=push)](https://pypi.org/project/mint-llm/)
[![CI](https://github.com/Reithan/MINT/actions/workflows/ci.yml/badge.svg?branch=main&event=push)](https://github.com/Reithan/MINT/actions/workflows/ci.yml)
# MINT
Meaning-Informed Next-token Transformation

## Project Goals
MINT adds a transformation layer that redistributes next\-token probabilities
according to semantic token similarity based on the model's embedding space. The
aim is to produce more varied, human\-like text without sacrificing coherence.

## Installation
Create a virtual environment and install the package in editable mode:

```bash
pip install -e .
```

This installs the `mint` package and provides the `mint` command-line interface.

To use the published release from PyPI (when available), run:

```bash
pip install mint-llm
```

## CLI Usage
Run the CLI with:

```bash
mint --help
```

The `mint` command exposes several subcommands. The typical workflow is shown
below.

## Using MINT

Run the commands below to build and apply the redistribution layer:

1. **Pick** a checkpoint from the Hugging Face Hub (optional).

   ```bash
   mint pick <model_id> checkpoint/
   ```

2. **Extract** token embeddings from the checkpoint.

   ```bash
   mint extract checkpoint/model.safetensors embeddings.safetensors
   ```

3. **Blend** the embeddings into a low-rank similarity factor.

   ```bash
   mint blend embeddings.safetensors mint_out/ --rank 1024
   # → mint_out/W.safetensors (plus R.safetensors with --keep-residual)
   ```
   Use `-r/--rank` to set factor rank (default 1024). Pass `--keep-residual` to
   also save a sparse `R.safetensors` file.

4. **Brew** new text from the wrapped model.

   ```bash
   mint brew model_id_or_path mint_out/ --prompt "Hello"
   ```
   Omit `--prompt` or pass `--interactive` to read prompts from stdin.

5. **Infuse** the tested similarity matrix into a local model and save the result
   to a directory.

   ```bash
   mint infuse path/to/model mint_out/ infused-model --alpha 0.1
   ```

   ```python
   from mint.wrapper import load_wrapped_model
   from mint.logits import SRLogitsProcessor

   model, tokenizer, layer = load_wrapped_model("model_id_or_path", "mint_out/")
   processor = SRLogitsProcessor(layer)
   ```

See the [notebooks](notebooks/) and [`examples/quickstart.py`](examples/quickstart.py)
for a more detailed walk-through and an automated script. You can also explore
the generator interactively using the CLI.

## Additional Utilities
The CLI exposes optional commands for working with checkpoints:

- **Crush** merge sharded checkpoints referenced by an index file.

  ```bash
  mint crush checkpoint/model.safetensors.index.json checkpoint/model.safetensors
  ```

- **Chop** split a `.safetensors` checkpoint into shards. Provide a shard count
  or size:

  ```bash
  mint chop model.safetensors shards/ --shards 2

  mint chop model.safetensors shards/ --size-mb 500
  ```

## Quickstart Script
Run [`examples/quickstart.py`](examples/quickstart.py) for an end-to-end
demonstration. The script mirrors the `mint` CLI commands:
`extract`, `blend` and `brew`.

Required argument:

- `--prompt` – input text to generate from.

Optional arguments default to values defined in
[`tests/utils/model_config.json`](tests/utils/model_config.json):

- `--checkpoint` – checkpoint path. If this points to a
  `*.safetensors.index.json` file the required shards are downloaded and merged
  automatically. If omitted `model_url` is used.
- `--model` – model identifier or path. When a model ID is provided the
  checkpoint shards are fetched and merged automatically. Defaults to
  `model_id` or one derived from `model_url`.
- `--embeddings` – output file for embeddings (default
`embeddings.safetensors`).
- `--similarity` – output directory for `W.safetensors` (and optionally
  `R.safetensors`, default `.cache/mint`).

```bash
python examples/quickstart.py --prompt "Hello"
```

The script extracts embeddings, builds the similarity matrix and generates text
using the wrapped model.

## Examples
Practical examples are provided in the [notebooks](notebooks/) directory.
They demonstrate embedding extraction, building a similarity matrix and
brewing text from a short prompt.

## Development
Install development dependencies with:

```bash
pip install -e '.[dev]'
```

Use the provided Makefile to run common tasks:

```bash
make format # check black formatting
make lint   # run ruff and mypy (if configured)
make test   # run the pytest suite
make all    # runs all checks
```

`make` commands `format`, `lint`, and `all` can also be suffixed with `-fix` (e.g. `make format-fix`)
to attempt to automatically fix issues. `make fix` will also run all fixes.

## Contributing
Development tasks are tracked in `todos.json`. See
[`project_proposal-MINT.md`](project_proposal-MINT.md) for the full technical
plan. Release notes are available in
[`CHANGELOG.md`](CHANGELOG.md). Feel free to open issues or pull requests to
contribute.


## Citation
If you use MINT in your research, please cite the project using the metadata in [CITATION.cff](CITATION.cff).
