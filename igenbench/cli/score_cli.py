"""Score aggregation command for IGenBench evaluation results."""

from collections import defaultdict
from pathlib import Path
from typing import Optional

import typer

from igenbench.cli.main import app
from igenbench.utils.logger import logger
from igenbench.vis_item import VISItem


@app.command("score")
def cmd_score(
    output_dir: str = typer.Option(
        "outputs/", "--output-dir", help="Directory containing evaluation results"
    ),
    gen_model: Optional[str] = typer.Option(
        None, "--gen-model", help="Filter by generation model name (optional)"
    ),
    eval_model: Optional[str] = typer.Option(
        None, "--eval-model", help="Filter by evaluation model name (optional)"
    ),
    by_source: bool = typer.Option(
        True,
        "--by-source/--no-by-source",
        help="Show accuracy breakdown by question source (prompt vs seed)",
    ),
    by_type: bool = typer.Option(
        False,
        "--by-type/--no-by-type",
        help="Show accuracy breakdown by question type",
    ),
):
    """Aggregate and display evaluation accuracy scores from the output directory."""
    output_path = Path(output_dir)

    if not output_path.exists():
        logger.error(f"Output directory not found: {output_dir}")
        raise typer.Exit(code=2)

    json_files = sorted(output_path.glob("*/*.json"))

    if not json_files:
        logger.error(f"No result files found in {output_dir}")
        raise typer.Exit(code=2)

    # {(gen_model, eval_model): [correct, total]}
    overall: dict = defaultdict(lambda: [0, 0])
    # {(gen_model, eval_model, source): [correct, total]}
    by_source_scores: dict = defaultdict(lambda: [0, 0])
    # {(gen_model, eval_model, question_type): [correct, total]}
    by_type_scores: dict = defaultdict(lambda: [0, 0])

    item_count = 0
    skipped = 0

    for json_file in json_files:
        try:
            item = VISItem.from_dict(str(json_file))
        except Exception as e:
            logger.warning(f"Skipping {json_file.name}: {e}")
            skipped += 1
            continue

        if not item.evaluation:
            continue

        item_count += 1
        for eval_entry in item.evaluation:
            for judgment in eval_entry.judgments:
                gm = judgment.gen_model
                em = judgment.eval_model

                if gen_model and gm != gen_model:
                    continue
                if eval_model and em != eval_model:
                    continue

                correct = 1 if str(judgment.answer) == "1" else 0
                overall[(gm, em)][0] += correct
                overall[(gm, em)][1] += 1

                if by_source and eval_entry.source:
                    by_source_scores[(gm, em, eval_entry.source)][0] += correct
                    by_source_scores[(gm, em, eval_entry.source)][1] += 1

                if by_type and eval_entry.question_type:
                    by_type_scores[(gm, em, eval_entry.question_type)][0] += correct
                    by_type_scores[(gm, em, eval_entry.question_type)][1] += 1

    if not overall:
        typer.echo("No evaluation results found matching the filters.")
        raise typer.Exit(code=0)

    col_w = 60
    typer.echo(f"\n{'=' * col_w}")
    typer.echo(f"IGenBench Scores  ({item_count} items{', ' + str(skipped) + ' skipped' if skipped else ''})")
    typer.echo(f"{'=' * col_w}")
    typer.echo(f"{'Gen Model':<28} {'Eval Model':<20} {'Accuracy':>9}  {'(correct/total)':>15}")
    typer.echo(f"{'-' * col_w}")

    for (gm, em), (correct, total) in sorted(overall.items()):
        acc = correct / total if total else 0.0
        typer.echo(f"{gm:<28} {em:<20} {acc:>8.1%}  ({correct}/{total})")

        if by_source:
            sources = sorted(
                {k[2] for k in by_source_scores if k[0] == gm and k[1] == em}
            )
            for src in sources:
                c, t = by_source_scores[(gm, em, src)]
                a = c / t if t else 0.0
                typer.echo(f"  {'[' + src + ']':<26} {'':<20} {a:>8.1%}  ({c}/{t})")

        if by_type:
            qtypes = sorted(
                {k[2] for k in by_type_scores if k[0] == gm and k[1] == em}
            )
            for qt in qtypes:
                c, t = by_type_scores[(gm, em, qt)]
                a = c / t if t else 0.0
                typer.echo(f"  {'[' + qt + ']':<26} {'':<20} {a:>8.1%}  ({c}/{t})")

    typer.echo(f"{'=' * col_w}\n")
