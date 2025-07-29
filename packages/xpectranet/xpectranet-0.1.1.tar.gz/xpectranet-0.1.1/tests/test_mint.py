from xpectranet.sdk import mint_insight
from tests.utils import dump_json

def test_mint_basic(sample_user_id):
    cmb = mint_insight("This is a test insight.", role="user", user_id=sample_user_id)
    dump_json(cmb, "mint_output.json")
    assert "xko_hasIntent" in cmb
