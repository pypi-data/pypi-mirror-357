from xpectranet.sdk import collapse_trail
from tests.utils import dump_json

def test_collapse_simple_trail():
    state = collapse_trail(["We are behind schedule.", "Customer complained."])
    dump_json(state, "collapse_output.json")
    assert "xko_hasIntent" in state
