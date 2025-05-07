from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    OutputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    output_guardrail,
)
from typing import Optional

class MLReport(BaseModel): 
    baseline_model_results: str
    best_model: str
    feature_importance: Optional[str]
    next_steps: Optional[str]

class MLReportOutput(BaseModel): 
    reasoning: str
    is_ml_report: bool

# Implementing Guardrails
guardrail_agent = Agent(
    name="Guardrail check",
    instructions="""
    Examine the output and ensure it includes the appropriate section of an ML report:
    - Baseline model results
    - Best model
    - Feature Importance (this is optional)
    - Next steps (optional)
    """,
    output_type=MLReportOutput,
)

@output_guardrail
async def ml_report_guardrail_naive(ctx: RunContextWrapper, agent: Agent, output: MLReport) -> GuardrailFunctionOutput:
    errors = []

    # Check required fields
    if not output.baseline_model_results.strip():
        errors.append("Missing `baseline_model_results`.")
    if not output.best_model.strip():
        errors.append("Missing `best_model`.")

    # Optional fields can be None, but if present, must be non-empty
    if output.feature_importance is not None and not output.feature_importance.strip():
        errors.append("`feature_importance` is present but empty.")
    if output.next_steps is not None and not output.next_steps.strip():
        errors.append("`next_steps` is present but empty.")

    is_valid = len(errors) == 0

    return GuardrailFunctionOutput(
        output_info={"errors": errors if not is_valid else "All checks passed."},
        tripwire_triggered=not is_valid,
    )

@output_guardrail
async def ml_report_guardrail_complete(ctx: RunContextWrapper, agent: Agent, output: MLReport) -> GuardrailFunctionOutput:
    report_summary = (
        f"Baseline model results:\n{output.baseline_model_results}\n\n"
        f"Best model:\n{output.best_model}\n\n"
        f"Feature importance:\n{output.feature_importance or 'None'}\n\n"
        f"Next steps:\n{output.next_steps or 'None'}"
    )

    result = await Runner.run(guardrail_agent, report_summary, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=not result.final_output.is_ml_report,  # Negate since tripwire means failure
    )