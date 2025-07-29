from xpectranet.sdk import resume_symbolic
from tests.utils import dump_json

def test_resume_flow():
    resumed = resume_symbolic(["Agent forgot reply", "Escalation from client"], "What's next?")
    dump_json(resumed, "resume_output.json")
    assert "xko_hasFocus" in resumed or "xko_hasIntent" in resumed
