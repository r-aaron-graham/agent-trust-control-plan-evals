import os
import tempfile

# Keep traces, the review queue and benchmark output out of the repo during tests.
os.environ.setdefault("RUNTIME_DIR", tempfile.mkdtemp(prefix="atcp-evals-tests-"))
