# Physics (async)

Example script showing how to use the [AsyncPhysics][msl.kcdb.general_physics.AsyncPhysics] class to asynchronously extract information from the KCDB.

## Script

<!-- fmt: off -->
```python
--8<-- "examples/physics_async.py"
```
<!-- fmt: on -->

## Output

Running this script outputs the following, although, some values may change from what you observe when you run this script since information in the KCDB is continually changing.

```
AUV ResultsPhysics(number_of_elements=52, page_number=0, page_size=1000, total_elements=52, total_pages=1, version_api_kcdb='1.0.13')
EM ResultsPhysics(number_of_elements=185, page_number=0, page_size=1000, total_elements=185, total_pages=1, version_api_kcdb='1.0.13')
L ResultsPhysics(number_of_elements=102, page_number=0, page_size=1000, total_elements=102, total_pages=1, version_api_kcdb='1.0.13')
M ResultsPhysics(number_of_elements=187, page_number=0, page_size=1000, total_elements=187, total_pages=1, version_api_kcdb='1.0.13')
PR ResultsPhysics(number_of_elements=95, page_number=0, page_size=1000, total_elements=95, total_pages=1, version_api_kcdb='1.0.13')
T ResultsPhysics(number_of_elements=119, page_number=0, page_size=1000, total_elements=119, total_pages=1, version_api_kcdb='1.0.13')
TF ResultsPhysics(number_of_elements=25, page_number=0, page_size=1000, total_elements=25, total_pages=1, version_api_kcdb='1.0.13')
```