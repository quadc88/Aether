from aether.action.restricted_file_reader import _scan_governed_content_for_secrets


def test_private_key_begin(): assert _scan_governed_content_for_secrets("-----BEGIN PRIVATE KEY-----")
def test_private_key_end(): assert _scan_governed_content_for_secrets("-----END PRIVATE KEY-----")
def test_password_equal(): assert _scan_governed_content_for_secrets("password=x")
def test_password_colon(): assert _scan_governed_content_for_secrets("password: x")
def test_passwd(): assert _scan_governed_content_for_secrets("passwd = x")
def test_pwd(): assert _scan_governed_content_for_secrets("pwd\tx") is False
def test_secret(): assert _scan_governed_content_for_secrets("secret = x")
def test_secret_key(): assert _scan_governed_content_for_secrets("secret_key: x")
def test_token(): assert _scan_governed_content_for_secrets("token=x")
def test_access_token(): assert _scan_governed_content_for_secrets("access_token=x")
def test_api_key(): assert _scan_governed_content_for_secrets("api_key=x")
def test_api_dash_key(): assert _scan_governed_content_for_secrets("api-key=x")
def test_apikey(): assert _scan_governed_content_for_secrets("apikey=x")
def test_access_key(): assert _scan_governed_content_for_secrets("access_key=x")
def test_credential(): assert _scan_governed_content_for_secrets("credential=x")
def test_credentials(): assert _scan_governed_content_for_secrets("credentials=x")
def test_case_insensitive(): assert _scan_governed_content_for_secrets("PASSWORD = x")
def test_horizontal_space(): assert _scan_governed_content_for_secrets("token \t=\t x")
def test_ordinary_mention_allowed(): assert not _scan_governed_content_for_secrets("a token is mentioned")
def test_non_string_fails():
    try: _scan_governed_content_for_secrets(None)
    except TypeError: assert True
