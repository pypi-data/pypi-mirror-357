from typing import Type, Union, Literal, Optional, Dict, List, Tuple, Set, Annotated, Callable, Awaitable, Any
from mindor.dsl.schema.workflow import WorkflowVariableConfig
from .schema import WorkflowSchema
import gradio, json

class GradioWebUIBuilder:
    def build(self, schema: Dict[str, WorkflowSchema], runner: Callable[[Optional[str], Any], Awaitable[Any]]) -> gradio.Blocks:
        with gradio.Blocks() as blocks:
            for workflow_id, workflow in schema.items():
                async def run_workflow(input: Any, workflow_id=workflow_id) -> Any:
                    return await runner(workflow_id, input)

                if len(schema) > 1:
                    with gradio.Tab(label=workflow.name or workflow_id):
                        self._build_workflow_section(workflow, run_workflow)
                else:
                    self._build_workflow_section(workflow, run_workflow)

        return blocks

    def _build_workflow_section(self, workflow: WorkflowSchema, runner: Callable[[Any], Awaitable[Any]]) -> gradio.Column:
        with gradio.Column() as section:
            gradio.Markdown(f"## **{workflow.title or 'Untitled Workflow'}**")  

            if workflow.description:
                gradio.Markdown(f"📝 {workflow.description}")

            gradio.Markdown("#### 📥 Input Parameters")
            input_components = [ self._build_input_component(variable) for variable in workflow.input ]
            run_button = gradio.Button("🚀 Run Workflow", variant="primary")

            gradio.Markdown("#### 📤 Output Values")
            output_components = [ self._build_output_component(variable) for variable in workflow.output ]

            if not output_components:
                output_components = gradio.Textbox(label="", lines=8, interactive=False, show_copy_button=True)

            async def run_workflow(*args):
                input = { variable.name: value for variable, value in zip(workflow.input, args) }
                output = await runner(input)

                if workflow.output and isinstance(output, dict):
                    output = [ output[variable.name] for variable in workflow.output ]
                    output = output[0] if len(output) == 1 else output

                return output

            run_button.click(
                fn=run_workflow,
                inputs=input_components,
                outputs=output_components
            )

        return section

    def _build_input_component(self, variable: WorkflowVariableConfig) -> gradio.Component:
        label = f"{variable.name} {'*' if variable.required else ''}"
        info = variable.description or ""
        default = variable.default

        if variable.type == "string":
            return gradio.Textbox(label=label, value=default or "", info=info)
        
        if variable.type == "integer":
            return gradio.Number(label=label, value=default or 0, precision=0, info=info)
        
        if variable.type == "float":
            return gradio.Number(label=label, value=default or 0.0, info=info)
        
        if variable.type == "boolean":
            return gradio.Checkbox(label=label, value=default or False, info=info)
        
        if variable.type == "file":
            return gradio.File(label=label, file_types=["*"], info=info)
        
        if variable.type == "select":
            return gradio.Dropdown(choices=variable.options or [], label=label, value=default, info=info)
        
        return gradio.Textbox(label=label, value=default or "", info=f"Unsupported type: {variable.type}")

    def _build_output_component(self, variable: WorkflowVariableConfig) -> gradio.Component:
        label = variable.name
        info = variable.description or ""
        
        if variable.type == "string":
            return gradio.Textbox(label=label, interactive=False, show_copy_button=True, info=info)
        
        return gradio.Textbox(label=label, info=f"Unsupported type: {variable.type}")
