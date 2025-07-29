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

The recommended workflow progresses through several commands:
1. **Pick** a checkpoint from the Hugging Face Hub (optional).

   ```bash
   mint pick <model_id> checkpoint/
   ```

2. **Crush** merge sharded checkpoints referenced by an index file.

   ```bash
   mint crush model.safetensors.index.json model.safetensors
   ```

3. **Extract** token embeddings from a checkpoint.
4. **Blend** the embeddings into a sparse similarity matrix. The command tries
   to use GPU 0 via CUDA, then Vulkan, before falling back to the CPU. Use
   `--cpu` to disable GPU usage or `--gpu <index>` to choose a device. The
   `--sdk` option selects the acceleration backend and values below `--tau`
   (default: `1e-4`) are pruned before saving the matrix as a PyTorch sparse
   tensor:

   ```bash
   mint blend embeddings.safetensors similarity.pt --cpu --tau 0.00001
   ```


5. **Brew** new text from the wrapped model.

   ```bash
   mint brew --model <model_id_or_path> --similarity similarity.pt --prompt "Hello"
   ```
  Omit `--prompt` or pass `--interactive` to read prompts line by line from
  stdin.

6. **Infuse** the tested similarity matrix into a local model and save the
   result to a directory.

   ```bash
   mint infuse path/to/model similarity.pt infused-model --alpha 0.1
   ```

7. **Chop** split a full checkpoint back into shards (optional).

   ```bash
   mint chop model.safetensors --size 2GB
   ```



### Example workflow

Run the commands sequentially to build and use the redistribution layer:

```bash
mint pick my-model checkpoint/
mint crush checkpoint/model.safetensors.index.json checkpoint/model.safetensors
mint extract checkpoint/model.safetensors embeddings.safetensors
mint blend embeddings.safetensors similarity.pt --tau 1e-4
mint brew --model my-model --similarity similarity.pt --prompt "Hello" --seed 42
mint infuse ./my-model similarity.pt my-model-infused --alpha 0.1
mint chop my-model-infused --size 2GB # optional
```

See the [notebooks](notebooks/) and [`examples/quickstart.py`](examples/quickstart.py)
for a more detailed walk-through and an automated script. You can also
explore the generator interactively using the CLI.

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
- `--similarity` – output file for the similarity matrix (default
  `similarity.pt`).
- `--tau` – sparsity threshold (default `1e-4`).

```bash
python examples/quickstart.py --prompt "Hello"
```

The script extracts embeddings, builds the similarity matrix and generates text
using the wrapped model.

## Examples
Practical examples are provided in the [notebooks](notebooks/) directory.
They demonstrate embedding extraction, building a similarity matrix and
brewing text from a short prompt.

## Splitting Large Checkpoints
Use the `chop` command to divide a `.safetensors` checkpoint into shards:

```bash
mint chop model.safetensors shards/ --shards 2
```

The command writes shard files and a matching `model.safetensors.index.json`
inside the output directory. You can instead target a specific shard size:

```bash
mint chop model.safetensors shards/ --size-mb 500
```

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
