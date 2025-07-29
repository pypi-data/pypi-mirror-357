from xpectranet.sdk import remix_texts
from xpectranet.licensing.sign import sign_license
from tests.utils import dump_json

def test_remix_resolve():
    sign_license("test_user", "developer_plus", 1, "dev_secret_key")
    remixed = remix_texts(["We failed.", "Customer angry."], remix_type="resolve", user_id="test_user")
    dump_json(remixed, "remix_output.json")
    assert remixed["xko_remixOf"]
