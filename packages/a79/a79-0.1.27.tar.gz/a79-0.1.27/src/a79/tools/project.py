<<<<<<< HEAD
from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.project_models import CreateProjectInput, CreateProjectOutput
=======
from a79.client import A79Client
from a79.models.tools import DEFAULT
from a79.models.tools.project_models import CreateProjectInput, CreateProjectOutput
>>>>>>> 0155b70e2 (Fix external a79 sdk imports)

__all__ = ["CreateProjectInput", "CreateProjectOutput", "create_project"]


def create_project(
    *,
    name: str = DEFAULT,
    description: str = DEFAULT,
    datasource_ids: list[int] = DEFAULT,
    worksheet_id: int | None = DEFAULT,
    use_case: str = DEFAULT,
) -> CreateProjectOutput:
    """Create an A79 project from the specified worksheets / datasources."""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = CreateProjectInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="project", name="create_project", input=input_model.model_dump()
    )
    return CreateProjectOutput.model_validate(output_model)
