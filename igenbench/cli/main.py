"""CLI for IGenBench - Infographic Generation and Evaluation."""

import typer

app = typer.Typer(no_args_is_help=True)

# Register commands
import igenbench.cli.gen_cli  # noqa: E402, F401
import igenbench.cli.eval_cli  # noqa: E402, F401
import igenbench.cli.batch_cli  # noqa: E402, F401
import igenbench.cli.score_cli  # noqa: E402, F401


def main() -> None:
    """Entry point for the IGenBench CLI."""
    app()


if __name__ == "__main__":
    main()
