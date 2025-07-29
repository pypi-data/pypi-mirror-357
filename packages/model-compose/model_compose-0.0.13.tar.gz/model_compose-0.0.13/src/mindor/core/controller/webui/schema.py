from typing import Type, Union, Literal, Optional, Dict, List, Tuple, Set, Annotated, Any
from pydantic import BaseModel
from mindor.dsl.schema.workflow import WorkflowConfig, WorkflowVariableConfig
from mindor.dsl.schema.component import ComponentConfig
import re

class WorkflowVariableResolver:
    def __init__(self):
        self.patterns: Dict[str, re.Pattern] = {
            "variable": re.compile(
                r"""\$\{                   # ${ 
                    ([a-zA-Z_][\w\-]*)     # key: input, env, etc.
                    (?:\.([^\|\}]+))?      # path: key, key.path[0], etc.
                    (?:\s*\|\s*([^\}]+))?  # default value after `|`
                \}""",                     # }
                re.VERBOSE,
            )
        }

    def _enumerate_variables(self, data: Any, wanted_key: str) -> Any:
        if isinstance(data, str):
            variables = []

            for match in self.patterns["variable"].finditer(data):
                key, path = match.group(1), match.group(2)
                
                if key == wanted_key:
                    variables.append(path)

            return variables

        if isinstance(data, BaseModel):
            return self._enumerate_variables(data.model_dump(exclude_none=True), wanted_key)
        
        if isinstance(data, dict):
            return sum([ self._enumerate_variables(v, wanted_key) for v in data.values() ], [])

        if isinstance(data, list):
            return sum([ self._enumerate_variables(v, wanted_key) for v in data ], [])
        
        return []

class WorkflowInputResolver(WorkflowVariableResolver):
    def resolve(self, workflow: WorkflowConfig, components: Dict[str, ComponentConfig]) -> List[WorkflowVariableConfig]:
        variables = []
        for job in workflow.jobs.values():
            if not job.input or job.input == "${input}":
                action_id = job.action or "__default__"
                if isinstance(job.component, str):
                    component: ComponentConfig = components[job.component] if job.component in components else None
                    if component:
                        variables.extend(self._enumerate_variables(component.actions[action_id], "input"))
                else:
                    variables.extend(self._enumerate_variables(job.component.actions[action_id], "input"))
            else:
                variables.extend(self._enumerate_variables(job.input, "input"))

        return [ WorkflowVariableConfig(name=name, type="string") for name in set(variables) ]

class WorkflowOutputResolver(WorkflowVariableResolver):
    def resolve(self, workflow: WorkflowConfig, components: Dict[str, ComponentConfig]) -> List[WorkflowVariableConfig]:
        variables = []
        for job_id, job in workflow.jobs.items():
            if not self._is_terminal_job(workflow, job_id):
                continue
            
            if not job.output or job.output == "${output}":
                action_id = job.action or "__default__"
                if isinstance(job.component, str):
                    component: ComponentConfig = components[job.component] if job.component in components else None
                    if component:
                        action = component.actions[action_id]
                        if isinstance(action.output, dict):
                            variables.extend(action.output.keys())
                else:
                    action = component.actions[action_id]
                    if isinstance(action.output, dict):
                        variables.extend(action.output.keys())
            else:
                if isinstance(job.output, dict):
                    variables.extend(job.output.keys())

        return [ WorkflowVariableConfig(name=name, type="string") for name in set(variables) ]
    
    def _is_terminal_job(self, workflow: WorkflowConfig, job_id: str) -> bool:
        return all(job_id not in job.depends_on for other_id, job in workflow.jobs.items() if other_id != job_id)

class WorkflowSchema:
    def __init__(self, name: str, title: str, description: Optional[str], input: List[WorkflowVariableConfig], output: List[WorkflowVariableConfig]):
        self.name: str = name
        self.title: str = title
        self.description: Optional[str] = description
        self.input: List[WorkflowVariableConfig] = input
        self.output: List[WorkflowVariableConfig] = output
