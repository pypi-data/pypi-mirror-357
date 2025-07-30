"""Pipeline generator module for creating pipeline structure from configuration."""

import os
import shutil
from pathlib import Path
from typing import (
    Dict,
    List,
    Optional,
    Tuple,
)

from bclearer_core.pipeline_builder.schema import (
    DomainConfig,
    PipelineConfig,
    StageConfig,
    SubStageConfig,
    ThinSliceConfig,
)


class PipelineGenerator:
    """Generator class for creating pipeline structure from configuration."""

    def __init__(
        self,
        template_path: str,
        output_base_path: str,
    ):
        """
        Initialize the PipelineGenerator.

        Args:
            template_path: Path to the template pipeline directory
            output_base_path: Base path where the new pipeline will be created
        """
        self.template_path = Path(
            template_path
        )
        self.output_base_path = Path(
            output_base_path
        )

        if (
            not self.template_path.exists()
        ):
            raise FileNotFoundError(
                f"Template path not found: {template_path}"
            )

        if (
            not self.template_path.is_dir()
        ):
            raise NotADirectoryError(
                f"Template path is not a directory: {template_path}"
            )

    def generate_pipeline(
        self, config: DomainConfig
    ) -> str:
        """
        Generate pipeline structure from configuration.

        Args:
            config: Domain configuration

        Returns:
            Path to the generated pipeline
        """
        domain_name = config.domain_name
        domain_path = (
            self.output_base_path
            / "pipelines"
            / domain_name
        )

        if domain_path.exists():
            raise FileExistsError(
                f"Domain path already exists: {domain_path}"
            )

        # Create domain directory
        domain_path.mkdir(
            parents=True, exist_ok=True
        )

        # Copy template structure first
        self._copy_template_structure(
            domain_path
        )

        # Create b_source directory
        b_source_path = (
            domain_path / "b_source"
        )
        b_source_path.mkdir(
            exist_ok=True
        )

        # Create __init__.py in b_source
        self._create_init_file(
            b_source_path
        )

        # Create app_runners directory
        app_runners_path = (
            b_source_path
            / "app_runners"
        )
        app_runners_path.mkdir(
            exist_ok=True
        )
        self._create_init_file(
            app_runners_path
        )

        # Create aa_b_clearer_pipeline_b_application_runner.py
        self._create_application_runner(
            app_runners_path,
            domain_name,
        )

        # Create app_runners/runners directory
        runners_path = (
            app_runners_path / "runners"
        )
        runners_path.mkdir(
            exist_ok=True
        )
        self._create_init_file(
            runners_path
        )

        # Create aa_b_clearer_pipelines_runner.py
        self._create_pipelines_runner(
            runners_path,
            domain_name,
            config.pipelines,
        )

        # Create common directory structure
        common_path = (
            b_source_path / "common"
        )
        common_path.mkdir(exist_ok=True)
        self._create_init_file(
            common_path
        )

        common_objects_path = (
            common_path / "objects"
        )
        common_objects_path.mkdir(
            exist_ok=True
        )
        self._create_init_file(
            common_objects_path
        )

        common_enums_path = (
            common_objects_path
            / "enums"
        )
        common_enums_path.mkdir(
            exist_ok=True
        )
        self._create_init_file(
            common_enums_path
        )

        common_universes_path = (
            common_objects_path
            / "universes"
        )
        common_universes_path.mkdir(
            exist_ok=True
        )
        self._create_init_file(
            common_universes_path
        )

        common_operations_path = (
            common_path / "operations"
        )
        common_operations_path.mkdir(
            exist_ok=True
        )
        self._create_init_file(
            common_operations_path
        )

        b_units_path = (
            common_operations_path
            / "b_units"
        )
        b_units_path.mkdir(
            exist_ok=True
        )
        self._create_init_file(
            b_units_path
        )

        # Copy b_unit_creator_and_runner.py
        template_b_unit_creator_path = (
            self.template_path
            / "b_source"
            / "common"
            / "operations"
            / "b_units"
            / "b_unit_creator_and_runner.py"
        )
        if (
            template_b_unit_creator_path.exists()
        ):
            shutil.copy(
                template_b_unit_creator_path,
                b_units_path
                / "b_unit_creator_and_runner.py",
            )
        else:
            self._create_b_unit_creator_and_runner(
                b_units_path
            )

        # Process each pipeline
        for (
            pipeline_config
        ) in config.pipelines:
            self._create_pipeline(
                b_source_path,
                pipeline_config,
                domain_name,
            )

            # Create pipeline runner
            self._create_pipeline_runner(
                runners_path,
                domain_name,
                pipeline_config.name,
            )

        # Create resources directory
        resources_path = (
            domain_path / "resources"
        )
        resources_path.mkdir(
            exist_ok=True
        )
        self._create_init_file(
            resources_path
        )

        collect_path = (
            resources_path / "collect"
        )
        collect_path.mkdir(
            exist_ok=True
        )
        self._create_init_file(
            collect_path
        )

        # Create tests directory structure
        tests_path = (
            domain_path / "tests"
        )
        tests_path.mkdir(exist_ok=True)
        self._create_init_file(
            tests_path
        )

        common_tests_path = (
            tests_path / "common"
        )
        common_tests_path.mkdir(
            exist_ok=True
        )
        self._create_init_file(
            common_tests_path
        )

        fixtures_path = (
            common_tests_path
            / "fixtures"
        )
        fixtures_path.mkdir(
            exist_ok=True
        )
        self._create_init_file(
            fixtures_path
        )

        inputs_path = (
            common_tests_path / "inputs"
        )
        inputs_path.mkdir(exist_ok=True)
        self._create_init_file(
            inputs_path
        )

        universal_path = (
            tests_path / "universal"
        )
        universal_path.mkdir(
            exist_ok=True
        )
        self._create_init_file(
            universal_path
        )

        e2e_path = (
            universal_path / "e2e"
        )
        e2e_path.mkdir(exist_ok=True)
        self._create_init_file(e2e_path)

        e2e_fixtures_path = (
            e2e_path / "fixtures"
        )
        e2e_fixtures_path.mkdir(
            exist_ok=True
        )
        self._create_init_file(
            e2e_fixtures_path
        )

        e2e_outputs_path = (
            e2e_path / "outputs"
        )
        e2e_outputs_path.mkdir(
            exist_ok=True
        )
        self._create_init_file(
            e2e_outputs_path
        )

        # Create basic test files
        self._create_conftest(e2e_path)
        self._create_e2e_test(
            e2e_path, domain_name
        )

        return str(domain_path)

    def _copy_template_structure(
        self, domain_path: Path
    ) -> None:
        """
        Copy basic template structure to start with.

        Args:
            domain_path: Path to the domain directory
        """
        # We don't copy everything directly to maintain control over what gets created
        # Instead, we'll create each directory and file as needed
        pass

    def _create_init_file(
        self, directory_path: Path
    ) -> None:
        """
        Create an empty __init__.py file in a directory.

        Args:
            directory_path: Path to the directory
        """
        init_file = (
            directory_path
            / "__init__.py"
        )
        init_file.touch()

    def _create_application_runner(
        self,
        app_runners_path: Path,
        domain_name: str,
    ) -> None:
        """
        Create the main application runner file.

        Args:
            app_runners_path: Path to the app_runners directory
            domain_name: Name of the domain
        """
        file_path = (
            app_runners_path
            / f"{domain_name}_b_clearer_pipeline_b_application_runner.py"
        )

        content = f"""from bclearer_orchestration_services.b_app_runner_service.b_application_runner import (
    run_b_application,
)
from {domain_name}.b_source.app_runners.runners.{domain_name}_b_clearer_pipelines_runner import (
    run_{domain_name}_b_clearer_pipelines,
)


def run_{domain_name}_b_clearer_pipeline_b_application() -> (
    None
):
    run_b_application(
        app_startup_method=run_{domain_name}_b_clearer_pipelines
    )
"""

        with open(file_path, "w") as f:
            f.write(content)

    def _create_pipelines_runner(
        self,
        runners_path: Path,
        domain_name: str,
        pipelines: List[PipelineConfig],
    ) -> None:
        """
        Create the pipelines runner file.

        Args:
            runners_path: Path to the runners directory
            domain_name: Name of the domain
            pipelines: List of pipeline configurations
        """
        file_path = (
            runners_path
            / f"{domain_name}_b_clearer_pipelines_runner.py"
        )

        imports = [
            "from bclearer_orchestration_services.reporting_service.wrappers.run_and_log_function_wrapper_latest import (",
            "    run_and_log_function,",
            ")",
        ]

        for pipeline in pipelines:
            imports.extend(
                [
                    f"from {domain_name}.b_source.app_runners.runners.{pipeline.name}_runner import (",
                    f"    run_{pipeline.name},",
                    ")",
                ]
            )

        function_calls = []
        for pipeline in pipelines:
            function_calls.append(
                f"    run_{pipeline.name}()"
            )

        content = (
            "\n".join(imports)
            + "\n\n\n"
        )
        content += (
            "@run_and_log_function()\n"
        )
        content += f"def run_{domain_name}_b_clearer_pipelines() -> (\n"
        content += "    None\n"
        content += "):\n"

        if function_calls:
            content += (
                "\n".join(
                    function_calls
                )
                + "\n"
            )
        else:
            content += "    pass\n"

        with open(file_path, "w") as f:
            f.write(content)

    def _create_pipeline_runner(
        self,
        runners_path: Path,
        domain_name: str,
        pipeline_name: str,
    ) -> None:
        """
        Create a pipeline runner file.

        Args:
            runners_path: Path to the runners directory
            domain_name: Name of the domain
            pipeline_name: Name of the pipeline
        """
        file_path = (
            runners_path
            / f"{pipeline_name}_runner.py"
        )

        content = f"""from bclearer_orchestration_services.reporting_service.wrappers.run_and_log_function_wrapper_latest import (
    run_and_log_function,
)
from {domain_name}.b_source.{pipeline_name}.orchestrators.pipeline.{pipeline_name}_orchestrator import (
    orchestrate_{pipeline_name},
)


@run_and_log_function()
def run_{pipeline_name}() -> None:
    orchestrate_{pipeline_name}()
"""

        with open(file_path, "w") as f:
            f.write(content)

    def _create_pipeline(
        self,
        b_source_path: Path,
        pipeline_config: PipelineConfig,
        domain_name: str,
    ) -> None:
        """
        Create a pipeline directory structure.

        Args:
            b_source_path: Path to the b_source directory
            pipeline_config: Pipeline configuration
            domain_name: Name of the domain
        """
        pipeline_name = (
            pipeline_config.name
        )
        pipeline_path = (
            b_source_path
            / pipeline_name
        )
        pipeline_path.mkdir(
            exist_ok=True
        )
        self._create_init_file(
            pipeline_path
        )

        # Create pipeline objects directory
        objects_path = (
            pipeline_path / "objects"
        )
        objects_path.mkdir(
            exist_ok=True
        )
        self._create_init_file(
            objects_path
        )

        enums_path = (
            objects_path / "enums"
        )
        enums_path.mkdir(exist_ok=True)
        self._create_init_file(
            enums_path
        )

        universes_path = (
            objects_path / "universes"
        )
        universes_path.mkdir(
            exist_ok=True
        )
        self._create_init_file(
            universes_path
        )

        b_units_path = (
            objects_path / "b_units"
        )
        b_units_path.mkdir(
            exist_ok=True
        )
        self._create_init_file(
            b_units_path
        )

        # Create operations directory
        operations_path = (
            pipeline_path / "operations"
        )
        operations_path.mkdir(
            exist_ok=True
        )
        self._create_init_file(
            operations_path
        )

        # Create orchestrators directory
        orchestrators_path = (
            pipeline_path
            / "orchestrators"
        )
        orchestrators_path.mkdir(
            exist_ok=True
        )
        self._create_init_file(
            orchestrators_path
        )

        pipeline_orchestrators_path = (
            orchestrators_path
            / "pipeline"
        )
        pipeline_orchestrators_path.mkdir(
            exist_ok=True
        )
        self._create_init_file(
            pipeline_orchestrators_path
        )

        # Create thin_slices directory
        thin_slices_path = (
            orchestrators_path
            / "thin_slices"
        )
        thin_slices_path.mkdir(
            exist_ok=True
        )
        self._create_init_file(
            thin_slices_path
        )

        # Create stages directory
        stages_path = (
            orchestrators_path
            / "stages"
        )
        stages_path.mkdir(exist_ok=True)
        self._create_init_file(
            stages_path
        )

        # Create sub_stages directory
        sub_stages_path = (
            orchestrators_path
            / "sub_stages"
        )
        sub_stages_path.mkdir(
            exist_ok=True
        )
        self._create_init_file(
            sub_stages_path
        )

        # Create pipeline orchestrator
        self._create_pipeline_orchestrator(
            pipeline_orchestrators_path,
            domain_name,
            pipeline_name,
            pipeline_config,
        )

        # Create thin slices
        for (
            thin_slice
        ) in (
            pipeline_config.thin_slices
        ):
            self._create_thin_slice(
                domain_name,
                pipeline_name,
                thin_slice,
                thin_slices_path,
                stages_path,
                sub_stages_path,
                b_units_path,
            )

    def _create_pipeline_orchestrator(
        self,
        pipeline_orchestrators_path: Path,
        domain_name: str,
        pipeline_name: str,
        pipeline_config: PipelineConfig,
    ) -> None:
        """
        Create pipeline orchestrator file.

        Args:
            pipeline_orchestrators_path: Path to the pipeline orchestrators directory
            domain_name: Name of the domain
            pipeline_name: Name of the pipeline
            pipeline_config: Pipeline configuration
        """
        file_path = (
            pipeline_orchestrators_path
            / f"{pipeline_name}_orchestrator.py"
        )

        imports = []

        if pipeline_config.thin_slices:
            for (
                thin_slice
            ) in (
                pipeline_config.thin_slices
            ):
                imports.append(
                    f"from {domain_name}.b_source.{pipeline_name}.orchestrators.thin_slices.{thin_slice.name}_orchestrator import ("
                )
                imports.append(
                    f"    orchestrate_{thin_slice.name},"
                )
                imports.append(")")

        content = (
            "\n".join(imports)
            + "\n\n\n"
            if imports
            else ""
        )
        content += f"def orchestrate_{pipeline_name}():\n"
        content += "    __run_contained_bie_pipeline_components()\n\n\n"
        content += "def __run_contained_bie_pipeline_components() -> (\n"
        content += "    None\n"
        content += "):\n"

        if pipeline_config.thin_slices:
            for (
                thin_slice
            ) in (
                pipeline_config.thin_slices
            ):
                content += f"    orchestrate_{thin_slice.name}()\n"
        else:
            content += "    pass\n"

        with open(file_path, "w") as f:
            f.write(content)

    def _create_thin_slice(
        self,
        domain_name: str,
        pipeline_name: str,
        thin_slice: ThinSliceConfig,
        thin_slices_path: Path,
        stages_path: Path,
        sub_stages_path: Path,
        b_units_path: Path,
    ) -> None:
        """
        Create thin slice orchestrator and related files.

        Args:
            domain_name: Name of the domain
            pipeline_name: Name of the pipeline
            thin_slice: Thin slice configuration
            thin_slices_path: Path to the thin slices directory
            stages_path: Path to the stages directory
            sub_stages_path: Path to the sub-stages directory
            b_units_path: Path to the b_units directory
        """
        slice_name = thin_slice.name
        file_path = (
            thin_slices_path
            / f"{slice_name}_orchestrator.py"
        )

        imports = []

        for stage in thin_slice.stages:
            stage_name = stage.name
            imports.append(
                f"from {domain_name}.b_source.{pipeline_name}.orchestrators.stages.{pipeline_name}_{stage_name}_orchestrator import ("
            )
            imports.append(
                f"    orchestrate_{pipeline_name}_{stage_name},"
            )
            imports.append(")")

            # Create stage orchestrator
            self._create_stage_orchestrator(
                domain_name,
                pipeline_name,
                stage,
                stages_path,
                sub_stages_path,
                b_units_path,
            )

        content = (
            "\n".join(imports)
            + "\n\n\n"
            if imports
            else ""
        )
        content += f"def orchestrate_{slice_name}():\n"
        content += "    __run_contained_bie_pipeline_components()\n\n\n"
        content += "def __run_contained_bie_pipeline_components() -> (\n"
        content += "    None\n"
        content += "):\n"

        if thin_slice.stages:
            for (
                stage
            ) in thin_slice.stages:
                content += f"    orchestrate_{pipeline_name}_{stage.name}()\n"
        else:
            content += "    pass\n"

        with open(file_path, "w") as f:
            f.write(content)

    def _create_stage_orchestrator(
        self,
        domain_name: str,
        pipeline_name: str,
        stage: StageConfig,
        stages_path: Path,
        sub_stages_path: Path,
        b_units_path: Path,
    ) -> None:
        """
        Create stage orchestrator file.

        Args:
            domain_name: Name of the domain
            pipeline_name: Name of the pipeline
            stage: Stage configuration
            stages_path: Path to the stages directory
            sub_stages_path: Path to the sub-stages directory
            b_units_path: Path to the b_units directory
        """
        stage_name = stage.name
        file_path = (
            stages_path
            / f"{pipeline_name}_{stage_name}_orchestrator.py"
        )

        imports = [
            "from bclearer_orchestration_services.reporting_service.wrappers.run_and_log_function_wrapper_latest import (",
            "    run_and_log_function,",
            ")",
        ]

        if stage.sub_stages:
            for (
                sub_stage
            ) in stage.sub_stages:
                sub_stage_name = (
                    sub_stage.name
                )
                imports.append(
                    f"from {domain_name}.b_source.{pipeline_name}.orchestrators.sub_stages.{pipeline_name}_{stage_name}_{sub_stage_name}.{pipeline_name}_{stage_name}_{sub_stage_name}_orchestrator import ("
                )
                imports.append(
                    f"    orchestrate_{pipeline_name}_{stage_name}_{sub_stage_name},"
                )
                imports.append(")")

                # Create sub-stage directory and orchestrator
                sub_stage_dir = (
                    sub_stages_path
                    / f"{pipeline_name}_{stage_name}_{sub_stage_name}"
                )
                sub_stage_dir.mkdir(
                    exist_ok=True
                )
                self._create_init_file(
                    sub_stage_dir
                )
                self._create_sub_stage_orchestrator(
                    domain_name,
                    pipeline_name,
                    stage_name,
                    sub_stage,
                    sub_stage_dir,
                    b_units_path,
                )

        if stage.b_units:
            imports.append(
                "from {0}.b_source.common.operations.b_units.b_unit_creator_and_runner import (".format(
                    domain_name
                )
            )
            imports.append(
                "    create_and_run_b_unit,"
            )
            imports.append(")")

            for b_unit in stage.b_units:
                # Create stage directory for b_units if doesn't exist
                stage_b_units_dir = (
                    b_units_path
                    / f"{pipeline_name}_{stage_name}"
                )
                stage_b_units_dir.mkdir(
                    exist_ok=True
                )
                self._create_init_file(
                    stage_b_units_dir
                )

                imports.append(
                    f"from {domain_name}.b_source.{pipeline_name}.objects.b_units.{pipeline_name}_{stage_name}.{b_unit.lower()}_b_units import ("
                )
                # Format the class name by removing underscores and capitalizing words
                class_name_parts = (
                    b_unit.split("_")
                )
                class_name = "".join(
                    part.capitalize()
                    for part in class_name_parts
                )
                imports.append(
                    f"    {class_name}BUnits,"
                )
                imports.append(")")

                # Create b_unit file
                self._create_b_unit(
                    b_unit,
                    stage_b_units_dir,
                )

        content = (
            "\n".join(imports)
            + "\n\n\n"
            if imports
            else ""
        )
        content += (
            "@run_and_log_function()\n"
        )
        content += f"def orchestrate_{pipeline_name}_{stage_name}() -> None:\n"
        content += "    __run_contained_bie_pipeline_components()\n\n\n"
        content += "def __run_contained_bie_pipeline_components() -> (\n"
        content += "    None\n"
        content += "):\n"

        if stage.sub_stages:
            for (
                sub_stage
            ) in stage.sub_stages:
                sub_stage_name = (
                    sub_stage.name
                )
                content += f"    orchestrate_{pipeline_name}_{stage_name}_{sub_stage_name}()\n"

        if stage.b_units:
            if stage.sub_stages:
                content += "\n"

            for b_unit in stage.b_units:
                content += "    create_and_run_b_unit(\n"
                # Format the class name by removing underscores and capitalizing words
                class_name_parts = (
                    b_unit.split("_")
                )
                class_name = "".join(
                    part.capitalize()
                    for part in class_name_parts
                )
                content += f"        b_unit_type={class_name}BUnits\n"
                content += "    )\n\n"

        if (
            not stage.sub_stages
            and not stage.b_units
        ):
            content += "    pass\n"

        with open(file_path, "w") as f:
            f.write(content)

    def _create_sub_stage_orchestrator(
        self,
        domain_name: str,
        pipeline_name: str,
        stage_name: str,
        sub_stage: SubStageConfig,
        sub_stage_dir: Path,
        b_units_path: Path,
    ) -> None:
        """
        Create sub-stage orchestrator file.

        Args:
            domain_name: Name of the domain
            pipeline_name: Name of the pipeline
            stage_name: Name of the stage
            sub_stage: Sub-stage configuration
            sub_stage_dir: Path to the sub-stage directory
            b_units_path: Path to the b_units directory
        """
        sub_stage_name = sub_stage.name
        file_path = (
            sub_stage_dir
            / f"{pipeline_name}_{stage_name}_{sub_stage_name}_orchestrator.py"
        )

        imports = [
            "from bclearer_orchestration_services.reporting_service.wrappers.run_and_log_function_wrapper_latest import (",
            "    run_and_log_function,",
            ")",
        ]

        if sub_stage.b_units:
            imports.append(
                "from {0}.b_source.common.operations.b_units.b_unit_creator_and_runner import (".format(
                    domain_name
                )
            )
            imports.append(
                "    create_and_run_b_unit,"
            )
            imports.append(")")

            for (
                b_unit
            ) in sub_stage.b_units:
                # Create sub-stage directory for b_units if doesn't exist
                sub_stage_b_units_dir = (
                    b_units_path
                    / f"{pipeline_name}_{stage_name}"
                    / f"{pipeline_name}_{stage_name}_{sub_stage_name}"
                )
                sub_stage_b_units_dir.mkdir(
                    parents=True,
                    exist_ok=True,
                )
                self._create_init_file(
                    sub_stage_b_units_dir
                )

                imports.append(
                    f"from {domain_name}.b_source.{pipeline_name}.objects.b_units.{pipeline_name}_{stage_name}.{pipeline_name}_{stage_name}_{sub_stage_name}.{b_unit.lower()}_b_units import ("
                )
                # Format the class name by removing underscores and capitalizing words
                class_name_parts = (
                    b_unit.split("_")
                )
                class_name = "".join(
                    part.capitalize()
                    for part in class_name_parts
                )
                imports.append(
                    f"    {class_name}BUnits,"
                )
                imports.append(")")

                # Create b_unit file
                self._create_b_unit(
                    b_unit,
                    sub_stage_b_units_dir,
                )

        content = (
            "\n".join(imports)
            + "\n\n\n"
            if imports
            else ""
        )
        content += (
            "@run_and_log_function()\n"
        )
        content += f"def orchestrate_{pipeline_name}_{stage_name}_{sub_stage_name}() -> (\n"
        content += "    None\n"
        content += "):\n"
        content += "    __run_contained_bie_pipeline_components()\n\n\n"
        content += "def __run_contained_bie_pipeline_components() -> (\n"
        content += "    None\n"
        content += "):\n"

        if sub_stage.b_units:
            for (
                b_unit
            ) in sub_stage.b_units:
                content += "    create_and_run_b_unit(\n"
                # Format the class name by removing underscores and capitalizing words
                class_name_parts = (
                    b_unit.split("_")
                )
                class_name = "".join(
                    part.capitalize()
                    for part in class_name_parts
                )
                content += f"        b_unit_type={class_name}BUnits\n"
                content += "    )\n"
        else:
            content += "    pass\n"

        with open(file_path, "w") as f:
            f.write(content)

    def _create_b_unit(
        self,
        b_unit: str,
        directory_path: Path,
    ) -> None:
        """
        Create a b_unit file.

        Args:
            b_unit: Name of the b_unit
            directory_path: Path to the directory for the b_unit
        """
        file_path = (
            directory_path
            / f"{b_unit.lower()}_b_units.py"
        )

        # Format the class name by removing underscores and capitalizing words
        # For example: 'ca_b_unit' becomes 'Ca' + 'B' + 'Unit' = 'CaBUnit'
        class_name_parts = b_unit.split(
            "_"
        )
        class_name = "".join(
            part.capitalize()
            for part in class_name_parts
        )

        content = """from bclearer_core.configurations.datastructure.logging_inspection_level_b_enums import (
    LoggingInspectionLevelBEnums,
)
from bclearer_orchestration_services.reporting_service.reporters.inspection_message_logger import (
    log_inspection_message,
)


# TODO: All bUnit classes should inherit from class BUnits, developed in core graph mvp dev, and that should be promoted
#  to nf_common or any repository where the bCLEARer stuff is going to be stored
class {0}BUnits:
    def __init__(self):
        pass

    def run(self) -> None:
        log_inspection_message(
            message="Running bUnit: {{}}".format(
                self.__class__.__name__
            ),
            logging_inspection_level_b_enum=LoggingInspectionLevelBEnums.INFO,
        )

        self.b_unit_process_function()

    def b_unit_process_function(
        self,
    ) -> None:
        pass
""".format(
            class_name
        )

        with open(file_path, "w") as f:
            f.write(content)

    def _create_b_unit_creator_and_runner(
        self, b_units_path: Path
    ) -> None:
        """
        Create b_unit_creator_and_runner.py file.

        Args:
            b_units_path: Path to the b_units directory
        """
        file_path = (
            b_units_path
            / "b_unit_creator_and_runner.py"
        )

        content = """# TODO: Minimal version of the method developed in core graph mvp dev that should be promoted to a bCLEARer importable
#  library
def create_and_run_b_unit(
    b_unit_type,
) -> None:
    b_unit = b_unit_type()

    b_unit.run()
"""

        with open(file_path, "w") as f:
            f.write(content)

    def _create_conftest(
        self, e2e_path: Path
    ) -> None:
        """
        Create a basic conftest.py file for tests.

        Args:
            e2e_path: Path to the e2e directory
        """
        file_path = (
            e2e_path / "conftest.py"
        )

        content = """import pytest


@pytest.fixture(scope="module")
def e2e_test_setup():
    # Add setup code here
    pass


@pytest.fixture(scope="module")
def e2e_test_teardown():
    # Add teardown code here
    pass
"""

        with open(file_path, "w") as f:
            f.write(content)

    def _create_e2e_test(
        self,
        e2e_path: Path,
        domain_name: str,
    ) -> None:
        """
        Create a basic e2e test file.

        Args:
            e2e_path: Path to the e2e directory
            domain_name: Name of the domain
        """
        file_path = (
            e2e_path
            / f"test_{domain_name}_b_clearer_pipeline_b_application_runner.py"
        )

        content = f"""import pytest
from {domain_name}.b_source.app_runners.{domain_name}_b_clearer_pipeline_b_application_runner import (
    run_{domain_name}_b_clearer_pipeline_b_application,
)


def test_{domain_name}_b_clearer_pipeline_b_application(e2e_test_setup, e2e_test_teardown):
    # Run the pipeline
    run_{domain_name}_b_clearer_pipeline_b_application()

    # Add assertions here
    assert True
"""

        with open(file_path, "w") as f:
            f.write(content)


def generate_pipeline(
    config: Dict,
    template_path: str,
    output_base_path: str,
) -> str:
    """
    Generate a pipeline from configuration.

    Args:
        config: Pipeline configuration dictionary
        template_path: Path to the template pipeline directory
        output_base_path: Base path where the new pipeline will be created

    Returns:
        Path to the generated pipeline
    """
    from bclearer_core.pipeline_builder.schema import (
        validate_pipeline_config,
    )

    config_obj = (
        validate_pipeline_config(config)
    )
    generator = PipelineGenerator(
        template_path, output_base_path
    )

    return generator.generate_pipeline(
        config_obj
    )


def update_pipeline(
    config: Dict, pipeline_path: str
) -> str:
    """
    Update an existing pipeline with new configuration.

    Args:
        config: Pipeline configuration dictionary
        pipeline_path: Path to the existing pipeline

    Returns:
        Path to the updated pipeline
    """
    # TODO: Implement update functionality
    raise NotImplementedError(
        "Update pipeline functionality is not yet implemented"
    )
