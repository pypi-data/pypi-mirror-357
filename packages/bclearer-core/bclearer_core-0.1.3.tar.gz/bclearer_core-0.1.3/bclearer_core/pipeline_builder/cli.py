"""Command-line interface for the bclearer pipeline builder."""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Optional

from bclearer_core.pipeline_builder.generator import (
    generate_pipeline,
    update_pipeline,
)
from bclearer_core.pipeline_builder.schema import (
    get_sample_config,
)


def create_parser() -> (
    argparse.ArgumentParser
):
    """
    Create argument parser for the CLI.

    Returns:
        ArgumentParser object
    """
    parser = argparse.ArgumentParser(
        description="BClearer Pipeline Builder CLI"
    )
    subparsers = parser.add_subparsers(
        dest="command",
        help="Command to execute",
    )

    # create command
    create_parser = subparsers.add_parser(
        "create",
        help="Create a new pipeline",
    )
    create_parser.add_argument(
        "--config",
        "-c",
        required=False,
        help="Path to the pipeline configuration JSON file",
    )
    create_parser.add_argument(
        "--template",
        "-t",
        required=False,
        default=None,
        help="Path to the template pipeline directory (default: pipelines/template_pipeline)",
    )
    create_parser.add_argument(
        "--output",
        "-o",
        required=False,
        default=os.getcwd(),
        help="Base path where the new pipeline will be created (default: current directory)",
    )
    create_parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Run in interactive mode to create pipeline configuration",
    )

    # update command
    update_parser = subparsers.add_parser(
        "update",
        help="Update an existing pipeline",
    )
    update_parser.add_argument(
        "--config",
        "-c",
        required=True,
        help="Path to the pipeline configuration JSON file",
    )
    update_parser.add_argument(
        "--pipeline",
        "-p",
        required=True,
        help="Path to the existing pipeline directory",
    )

    # sample command
    sample_parser = subparsers.add_parser(
        "sample",
        help="Generate a sample configuration file",
    )
    sample_parser.add_argument(
        "--output",
        "-o",
        required=False,
        default="pipeline_config_sample.json",
        help="Output file path for sample configuration (default: pipeline_config_sample.json)",
    )

    return parser


def interactive_config() -> Dict:
    """
    Create pipeline configuration interactively.

    Returns:
        Dictionary with pipeline configuration
    """
    print(
        "=== BClearer Pipeline Builder Interactive Configuration ==="
    )

    domain_name = input("Domain name: ")

    pipelines = []
    pipeline_count = int(
        input("Number of pipelines: ")
    )

    for i in range(pipeline_count):
        pipeline_name = input(
            f"Pipeline {i+1} name: "
        )

        thin_slices = []
        slice_count = int(
            input(
                f"Number of thin slices for pipeline '{pipeline_name}': "
            )
        )

        for j in range(slice_count):
            slice_name = input(
                f"Thin slice {j+1} name for pipeline '{pipeline_name}': "
            )

            # Create standard stages
            stages = []
            for stage_info in [
                (
                    "1c_collect",
                    "Collect",
                ),
                ("2l_load", "Load"),
                ("3e_evolve", "Evolve"),
                (
                    "4a_assimilate",
                    "Assimilate",
                ),
                ("5r_reuse", "Reuse"),
            ]:
                (
                    stage_name,
                    stage_desc,
                ) = stage_info

                print(
                    f"\nStage: {stage_desc} ({stage_name})"
                )
                include_stage = (
                    input(
                        f"Include {stage_desc} stage? (y/n): "
                    ).lower()
                    == "y"
                )

                if include_stage:
                    b_units = []
                    has_b_units = (
                        input(
                            f"Does {stage_desc} stage have direct b_units? (y/n): "
                        ).lower()
                        == "y"
                    )

                    if has_b_units:
                        b_units_input = input(
                            "Enter b_unit names (comma-separated, e.g., ca,cb): "
                        )
                        b_units = [
                            unit.strip()
                            for unit in b_units_input.split(
                                ","
                            )
                            if unit.strip()
                        ]

                    sub_stages = []
                    has_sub_stages = (
                        input(
                            f"Does {stage_desc} stage have sub-stages? (y/n): "
                        ).lower()
                        == "y"
                    )

                    if has_sub_stages:
                        sub_stage_count = int(
                            input(
                                f"Number of sub-stages for {stage_desc}: "
                            )
                        )

                        for k in range(
                            sub_stage_count
                        ):
                            sub_stage_name = input(
                                f"Sub-stage {k+1} name for {stage_desc}: "
                            )

                            sub_b_units = (
                                []
                            )
                            sub_b_units_input = input(
                                f"Enter b_unit names for sub-stage {sub_stage_name} (comma-separated): "
                            )
                            sub_b_units = [
                                unit.strip()
                                for unit in sub_b_units_input.split(
                                    ","
                                )
                                if unit.strip()
                            ]

                            sub_stages.append(
                                {
                                    "name": sub_stage_name,
                                    "b_units": sub_b_units,
                                }
                            )

                    stages.append(
                        {
                            "name": stage_name,
                            "sub_stages": sub_stages,
                            "b_units": b_units,
                        }
                    )

            thin_slices.append(
                {
                    "name": slice_name,
                    "stages": stages,
                }
            )

        pipelines.append(
            {
                "name": pipeline_name,
                "thin_slices": thin_slices,
            }
        )

    return {
        "domain_name": domain_name,
        "pipelines": pipelines,
    }


def save_sample_config(
    output_path: str,
) -> None:
    """
    Save a sample configuration file.

    Args:
        output_path: Path to save the sample configuration file
    """
    sample_config = get_sample_config()

    with open(output_path, "w") as f:
        json.dump(
            sample_config, f, indent=2
        )

    print(
        f"Sample configuration saved to '{output_path}'"
    )


def run_cli() -> None:
    """Run the bclearer pipeline builder CLI."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "sample":
        save_sample_config(args.output)
        return

    if args.command == "create":
        config = None

        if args.interactive:
            config = (
                interactive_config()
            )
        elif args.config:
            try:
                with open(
                    args.config, "r"
                ) as f:
                    config = json.load(
                        f
                    )
            except Exception as e:
                print(
                    f"Error loading configuration file: {str(e)}"
                )
                return
        else:
            print(
                "Error: Either --config or --interactive must be specified"
            )
            return

        template_path = (
            args.template
            or os.path.join(
                os.getcwd(),
                "pipelines",
                "template_pipeline",
            )
        )

        try:
            pipeline_path = (
                generate_pipeline(
                    config,
                    template_path,
                    args.output,
                )
            )
            print(
                f"Pipeline created successfully at '{pipeline_path}'"
            )
        except Exception as e:
            print(
                f"Error creating pipeline: {str(e)}"
            )
            return

    elif args.command == "update":
        try:
            with open(
                args.config, "r"
            ) as f:
                config = json.load(f)
        except Exception as e:
            print(
                f"Error loading configuration file: {str(e)}"
            )
            return

        try:
            pipeline_path = (
                update_pipeline(
                    config,
                    args.pipeline,
                )
            )
            print(
                f"Pipeline updated successfully at '{pipeline_path}'"
            )
        except NotImplementedError:
            print(
                "Update functionality is not yet implemented"
            )
        except Exception as e:
            print(
                f"Error updating pipeline: {str(e)}"
            )
            return


if __name__ == "__main__":
    run_cli()
