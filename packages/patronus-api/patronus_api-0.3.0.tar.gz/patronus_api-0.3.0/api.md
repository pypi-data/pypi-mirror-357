# EvaluatorCriteria

Types:

```python
from patronus_api.types import (
    EvaluatorCriteria,
    EvaluatorCriterionCreateResponse,
    EvaluatorCriterionListResponse,
    EvaluatorCriterionAddRevisionResponse,
    EvaluatorCriterionArchiveResponse,
)
```

Methods:

- <code title="post /v1/evaluator-criteria">client.evaluator_criteria.<a href="./src/patronus_api/resources/evaluator_criteria.py">create</a>(\*\*<a href="src/patronus_api/types/evaluator_criterion_create_params.py">params</a>) -> <a href="./src/patronus_api/types/evaluator_criterion_create_response.py">EvaluatorCriterionCreateResponse</a></code>
- <code title="get /v1/evaluator-criteria">client.evaluator_criteria.<a href="./src/patronus_api/resources/evaluator_criteria.py">list</a>(\*\*<a href="src/patronus_api/types/evaluator_criterion_list_params.py">params</a>) -> <a href="./src/patronus_api/types/evaluator_criterion_list_response.py">EvaluatorCriterionListResponse</a></code>
- <code title="post /v1/evaluator-criteria/{public_id}/revision">client.evaluator_criteria.<a href="./src/patronus_api/resources/evaluator_criteria.py">add_revision</a>(public_id, \*\*<a href="src/patronus_api/types/evaluator_criterion_add_revision_params.py">params</a>) -> <a href="./src/patronus_api/types/evaluator_criterion_add_revision_response.py">EvaluatorCriterionAddRevisionResponse</a></code>
- <code title="patch /v1/evaluator-criteria/{public_id}/archive">client.evaluator_criteria.<a href="./src/patronus_api/resources/evaluator_criteria.py">archive</a>(public_id) -> <a href="./src/patronus_api/types/evaluator_criterion_archive_response.py">EvaluatorCriterionArchiveResponse</a></code>

# Experiments

Types:

```python
from patronus_api.types import (
    Experiment,
    ExperimentCreateResponse,
    ExperimentRetrieveResponse,
    ExperimentUpdateResponse,
    ExperimentListResponse,
)
```

Methods:

- <code title="post /v1/experiments">client.experiments.<a href="./src/patronus_api/resources/experiments.py">create</a>(\*\*<a href="src/patronus_api/types/experiment_create_params.py">params</a>) -> <a href="./src/patronus_api/types/experiment_create_response.py">ExperimentCreateResponse</a></code>
- <code title="get /v1/experiments/{id}">client.experiments.<a href="./src/patronus_api/resources/experiments.py">retrieve</a>(id) -> <a href="./src/patronus_api/types/experiment_retrieve_response.py">ExperimentRetrieveResponse</a></code>
- <code title="patch /v1/experiments/{id}">client.experiments.<a href="./src/patronus_api/resources/experiments.py">update</a>(id, \*\*<a href="src/patronus_api/types/experiment_update_params.py">params</a>) -> <a href="./src/patronus_api/types/experiment_update_response.py">ExperimentUpdateResponse</a></code>
- <code title="get /v1/experiments">client.experiments.<a href="./src/patronus_api/resources/experiments.py">list</a>(\*\*<a href="src/patronus_api/types/experiment_list_params.py">params</a>) -> <a href="./src/patronus_api/types/experiment_list_response.py">ExperimentListResponse</a></code>
- <code title="delete /v1/experiments/{id}">client.experiments.<a href="./src/patronus_api/resources/experiments.py">delete</a>(id) -> None</code>

# Projects

Types:

```python
from patronus_api.types import Project, ProjectRetrieveResponse, ProjectListResponse
```

Methods:

- <code title="post /v1/projects">client.projects.<a href="./src/patronus_api/resources/projects.py">create</a>(\*\*<a href="src/patronus_api/types/project_create_params.py">params</a>) -> <a href="./src/patronus_api/types/project.py">Project</a></code>
- <code title="get /v1/projects/{id}">client.projects.<a href="./src/patronus_api/resources/projects.py">retrieve</a>(id) -> <a href="./src/patronus_api/types/project_retrieve_response.py">ProjectRetrieveResponse</a></code>
- <code title="get /v1/projects">client.projects.<a href="./src/patronus_api/resources/projects.py">list</a>(\*\*<a href="src/patronus_api/types/project_list_params.py">params</a>) -> <a href="./src/patronus_api/types/project_list_response.py">ProjectListResponse</a></code>
- <code title="delete /v1/projects/{id}">client.projects.<a href="./src/patronus_api/resources/projects.py">delete</a>(id) -> None</code>

# Evaluations

Types:

```python
from patronus_api.types import (
    EvaluationRetrieveResponse,
    EvaluationBatchCreateResponse,
    EvaluationEvaluateResponse,
    EvaluationSearchResponse,
)
```

Methods:

- <code title="get /v1/evaluations/{id}">client.evaluations.<a href="./src/patronus_api/resources/evaluations.py">retrieve</a>(id) -> <a href="./src/patronus_api/types/evaluation_retrieve_response.py">EvaluationRetrieveResponse</a></code>
- <code title="delete /v1/evaluations/{id}">client.evaluations.<a href="./src/patronus_api/resources/evaluations.py">delete</a>(id) -> None</code>
- <code title="post /v1/evaluations/batch">client.evaluations.<a href="./src/patronus_api/resources/evaluations.py">batch_create</a>(\*\*<a href="src/patronus_api/types/evaluation_batch_create_params.py">params</a>) -> <a href="./src/patronus_api/types/evaluation_batch_create_response.py">EvaluationBatchCreateResponse</a></code>
- <code title="delete /v1/evaluations">client.evaluations.<a href="./src/patronus_api/resources/evaluations.py">batch_delete</a>(\*\*<a href="src/patronus_api/types/evaluation_batch_delete_params.py">params</a>) -> object</code>
- <code title="post /v1/evaluate">client.evaluations.<a href="./src/patronus_api/resources/evaluations.py">evaluate</a>(\*\*<a href="src/patronus_api/types/evaluation_evaluate_params.py">params</a>) -> <a href="./src/patronus_api/types/evaluation_evaluate_response.py">EvaluationEvaluateResponse</a></code>
- <code title="post /v1/evaluations/search">client.evaluations.<a href="./src/patronus_api/resources/evaluations.py">search</a>(\*\*<a href="src/patronus_api/types/evaluation_search_params.py">params</a>) -> <a href="./src/patronus_api/types/evaluation_search_response.py">EvaluationSearchResponse</a></code>

# Otel

## Logs

Types:

```python
from patronus_api.types.otel import LogSearchResponse
```

Methods:

- <code title="post /v1/otel/logs/search">client.otel.logs.<a href="./src/patronus_api/resources/otel/logs.py">search</a>(\*\*<a href="src/patronus_api/types/otel/log_search_params.py">params</a>) -> <a href="./src/patronus_api/types/otel/log_search_response.py">LogSearchResponse</a></code>

## Spans

Types:

```python
from patronus_api.types.otel import SpanSearchResponse
```

Methods:

- <code title="delete /v1/otel/spans">client.otel.spans.<a href="./src/patronus_api/resources/otel/spans.py">delete</a>(\*\*<a href="src/patronus_api/types/otel/span_delete_params.py">params</a>) -> None</code>
- <code title="post /v1/otel/spans/search">client.otel.spans.<a href="./src/patronus_api/resources/otel/spans.py">search</a>(\*\*<a href="src/patronus_api/types/otel/span_search_params.py">params</a>) -> <a href="./src/patronus_api/types/otel/span_search_response.py">SpanSearchResponse</a></code>

# TraceInsight

Types:

```python
from patronus_api.types import (
    TraceInsightListResponse,
    TraceInsightCreateJobResponse,
    TraceInsightGetErrorAggregationsResponse,
    TraceInsightListJobsResponse,
    TraceInsightSearchSpanAnalysisResponse,
    TraceInsightSearchTraceInsightsResponse,
)
```

Methods:

- <code title="get /v1/trace-insight">client.trace_insight.<a href="./src/patronus_api/resources/trace_insight.py">list</a>(\*\*<a href="src/patronus_api/types/trace_insight_list_params.py">params</a>) -> <a href="./src/patronus_api/types/trace_insight_list_response.py">TraceInsightListResponse</a></code>
- <code title="post /v1/trace-insight-jobs">client.trace_insight.<a href="./src/patronus_api/resources/trace_insight.py">create_job</a>(\*\*<a href="src/patronus_api/types/trace_insight_create_job_params.py">params</a>) -> <a href="./src/patronus_api/types/trace_insight_create_job_response.py">TraceInsightCreateJobResponse</a></code>
- <code title="post /v1/trace-insight/errors">client.trace_insight.<a href="./src/patronus_api/resources/trace_insight.py">get_error_aggregations</a>(\*\*<a href="src/patronus_api/types/trace_insight_get_error_aggregations_params.py">params</a>) -> <a href="./src/patronus_api/types/trace_insight_get_error_aggregations_response.py">TraceInsightGetErrorAggregationsResponse</a></code>
- <code title="get /v1/trace-insight-jobs">client.trace_insight.<a href="./src/patronus_api/resources/trace_insight.py">list_jobs</a>(\*\*<a href="src/patronus_api/types/trace_insight_list_jobs_params.py">params</a>) -> <a href="./src/patronus_api/types/trace_insight_list_jobs_response.py">TraceInsightListJobsResponse</a></code>
- <code title="post /v1/span-analysis/search">client.trace_insight.<a href="./src/patronus_api/resources/trace_insight.py">search_span_analysis</a>(\*\*<a href="src/patronus_api/types/trace_insight_search_span_analysis_params.py">params</a>) -> <a href="./src/patronus_api/types/trace_insight_search_span_analysis_response.py">TraceInsightSearchSpanAnalysisResponse</a></code>
- <code title="post /v1/trace-insight/search">client.trace_insight.<a href="./src/patronus_api/resources/trace_insight.py">search_trace_insights</a>(\*\*<a href="src/patronus_api/types/trace_insight_search_trace_insights_params.py">params</a>) -> <a href="./src/patronus_api/types/trace_insight_search_trace_insights_response.py">TraceInsightSearchTraceInsightsResponse</a></code>

# Evaluators

Types:

```python
from patronus_api.types import EvaluatorListResponse, EvaluatorListFamiliesResponse
```

Methods:

- <code title="get /v1/evaluators">client.evaluators.<a href="./src/patronus_api/resources/evaluators.py">list</a>(\*\*<a href="src/patronus_api/types/evaluator_list_params.py">params</a>) -> <a href="./src/patronus_api/types/evaluator_list_response.py">EvaluatorListResponse</a></code>
- <code title="get /v1/evaluator-families">client.evaluators.<a href="./src/patronus_api/resources/evaluators.py">list_families</a>() -> <a href="./src/patronus_api/types/evaluator_list_families_response.py">EvaluatorListFamiliesResponse</a></code>

# Whoami

Types:

```python
from patronus_api.types import WhoamiRetrieveResponse
```

Methods:

- <code title="get /v1/whoami">client.whoami.<a href="./src/patronus_api/resources/whoami.py">retrieve</a>() -> <a href="./src/patronus_api/types/whoami_retrieve_response.py">WhoamiRetrieveResponse</a></code>

# Apps

Types:

```python
from patronus_api.types import AppListResponse
```

Methods:

- <code title="get /v1/apps">client.apps.<a href="./src/patronus_api/resources/apps.py">list</a>(\*\*<a href="src/patronus_api/types/app_list_params.py">params</a>) -> <a href="./src/patronus_api/types/app_list_response.py">AppListResponse</a></code>

# Prompts

Types:

```python
from patronus_api.types import (
    PromptCreateRevisionResponse,
    PromptListDefinitionsResponse,
    PromptListRevisionsResponse,
    PromptUpdateDefinitionResponse,
)
```

Methods:

- <code title="post /v1/prompt-revisions">client.prompts.<a href="./src/patronus_api/resources/prompts.py">create_revision</a>(\*\*<a href="src/patronus_api/types/prompt_create_revision_params.py">params</a>) -> <a href="./src/patronus_api/types/prompt_create_revision_response.py">PromptCreateRevisionResponse</a></code>
- <code title="delete /v1/prompt-definitions">client.prompts.<a href="./src/patronus_api/resources/prompts.py">delete_definitions</a>(\*\*<a href="src/patronus_api/types/prompt_delete_definitions_params.py">params</a>) -> None</code>
- <code title="get /v1/prompt-definitions">client.prompts.<a href="./src/patronus_api/resources/prompts.py">list_definitions</a>(\*\*<a href="src/patronus_api/types/prompt_list_definitions_params.py">params</a>) -> <a href="./src/patronus_api/types/prompt_list_definitions_response.py">PromptListDefinitionsResponse</a></code>
- <code title="get /v1/prompt-revisions">client.prompts.<a href="./src/patronus_api/resources/prompts.py">list_revisions</a>(\*\*<a href="src/patronus_api/types/prompt_list_revisions_params.py">params</a>) -> <a href="./src/patronus_api/types/prompt_list_revisions_response.py">PromptListRevisionsResponse</a></code>
- <code title="post /v1/prompt-revisions/{revision_id}/remove-labels">client.prompts.<a href="./src/patronus_api/resources/prompts.py">remove_labels</a>(revision_id, \*\*<a href="src/patronus_api/types/prompt_remove_labels_params.py">params</a>) -> None</code>
- <code title="post /v1/prompt-revisions/{revision_id}/set-labels">client.prompts.<a href="./src/patronus_api/resources/prompts.py">set_labels</a>(revision_id, \*\*<a href="src/patronus_api/types/prompt_set_labels_params.py">params</a>) -> None</code>
- <code title="patch /v1/prompt-definitions/{prompt_id}">client.prompts.<a href="./src/patronus_api/resources/prompts.py">update_definition</a>(prompt_id, \*\*<a href="src/patronus_api/types/prompt_update_definition_params.py">params</a>) -> <a href="./src/patronus_api/types/prompt_update_definition_response.py">PromptUpdateDefinitionResponse</a></code>
