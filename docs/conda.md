# Conda and application environments

Conda is a planned application substrate, not yet part of the bootstrap ISO.
The first pass should evaluate minimal Miniforge/conda and whether Navigator
and Jupyter run naturally as Sugar Activities or conventional applications.
Full Anaconda is intentionally not included by default.

Activity environment manifests may eventually describe isolated dependencies
and be provisioned on demand. Isolation comes before deduplication: unrelated
Activities should not silently share environments and create dependency
conflicts. The system Python remains outside this mechanism.

