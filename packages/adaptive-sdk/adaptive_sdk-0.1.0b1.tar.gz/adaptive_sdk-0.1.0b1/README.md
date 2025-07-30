# adaptive-sdk

The Python Client SDK for Adaptive Engine

## Installation

```bash
pip install -e .

```

## Usage 

```python
from adaptive_sdk import Adaptive, AsyncAdaptive

client = Adaptive("http://localhost:9000", "key-kitt")
# aclient = AsyncAdaptive("http://localhost:9000", "key-kitt")  # all the same methods as Adaptive, but async

try:
    use_case = client.create_use_case(name="Open Assistant", key="open_assistant")
    print(f"Use case created id={use_case.id} key={use_case.key}")
except:
    use_case = client.get_use_case("open_assistant")

if use_case is None:
    raise Exception("Could not get or create a use case")

metrics = client.list_metrics()
if not any(metric.key == "accepted" for metric in metrics):
    client.create_metric(name="accepted", key="accepted", kind="BOOL")

client.link_metric(use_case="open_assistant", metric="accepted")

model_attached = any(srv.model.key == "minimal" for srv in use_case.model_services)
if not model_attached:
    client.attach_model(model="minimal", use_case="open_assistant", wait=False)

response = client.add_interactions(
        model="minimal",
        use_case=str(use_case.id),
        messages=[{"role":"user", "content":"Prompt here"}],
        completion="Completion here",
        feedbacks=[{"metric":"accepted", "value":1, "details":"This was a good completion"}],
        ab_campaign=None,
        labels={"country": "Argentina"},
)
print(f"Interaction stored completion_id={response.completion_id}")

```

## Development

- Install dev dependencies

```bash
pip install -e '.[dev]'
```

- Download new REST/GQL schemas, generate types, and format the resulting files

```bash
CONCORDE_URL="http://localhost:9000"
python generate_gql_pt_datamodel.py --base-url $CONCORDE_URL
python generate_openapi_datamodel.py --base-url $CONCORDE_URL
black src/adaptive_sdk/graphql_client
black src/adaptive_sdk/rest
```

### How to add a new graphql query and/or new SDK methods/resources

1. Add the query or mutation in the file `src/adaptive_sdk/queries.graphql` (if REST schema changed, no need to write queries)
2. Regenerate graphql or REST types with the scripts above, depending on what has changed
3. If new REST types have been added or renamed, make sure to export them in `src/adaptive_sdk/rest/__init__.py` for the automatic SDK reference docs generator to pick up on.
3. Wrap the new queries/types in a nice, user-facing method respecting the existing naming conventions,
within the appropriate resource in `src/adaptive_sdk/resources` (create a new resource if needed).
4. If the input types for the new method are too complicated/nested, help the user by creating new TypedDict(s) and using them as input function parameter type hints, which enables nice suggestion for your new method, and self-documenting of methods. You can add these in `src/adaptive_sdk/input_types/typed_dicts.py`. If you add new typed dicts, make sure to export them in `src/adaptive_sdk/input_types/__init__.py`, so the automatic SDK reference docs generator picks up on them.
5. If you create a new resource, make sure to export it in `src/adaptive_sdk/resources/__init__.py`, and then add it without disrupting the alphabetical order of resources
in `src/adaptive_sdk/client.py`. Always add a new sync and async resource. 
