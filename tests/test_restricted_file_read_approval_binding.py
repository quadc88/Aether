from aether.action.approval_queue import restricted_read_fingerprint


def _action(target="/tmp/x.py", max_chars=1):
    return {"tool_id":"file.restricted_read","action_type":"restricted_file_read","name":"Restricted File Read","target":target,"permission_class":"read_only","parameters":{"max_chars":max_chars}}


def test_fingerprint_exists(): assert len(restricted_read_fingerprint(_action()) or "") == 64
def test_fingerprint_stable(): assert restricted_read_fingerprint(_action()) == restricted_read_fingerprint(_action())
def test_fingerprint_target_bound(): assert restricted_read_fingerprint(_action("/tmp/y.py")) != restricted_read_fingerprint(_action())
def test_fingerprint_parameter_bound(): assert restricted_read_fingerprint(_action(max_chars=2)) != restricted_read_fingerprint(_action())
def test_fingerprint_tool_bound():
    a=_action(); a["tool_id"]="x"; assert restricted_read_fingerprint(a) is None
def test_fingerprint_action_type_bound():
    a=_action(); a["action_type"]="x"; assert restricted_read_fingerprint(a) is None
def test_fingerprint_name_bound():
    a=_action(); a["name"]="x"; assert restricted_read_fingerprint(a) is None
def test_fingerprint_permission_bound():
    a=_action(); a["permission_class"]="write"; assert restricted_read_fingerprint(a) is None
def test_fingerprint_parameters_shape():
    a=_action(); a["parameters"]={}; assert restricted_read_fingerprint(a) is None
def test_fingerprint_range_low(): assert restricted_read_fingerprint(_action(max_chars=0))
def test_fingerprint_range_high(): assert restricted_read_fingerprint(_action(max_chars=12000))
def test_fingerprint_range_high_invalid(): assert restricted_read_fingerprint(_action(max_chars=12001)) is None
def test_fingerprint_negative_invalid(): assert restricted_read_fingerprint(_action(max_chars=-1)) is None
def test_fingerprint_extra_key_invalid(): assert restricted_read_fingerprint({**_action(), "extra":1}) is None
def test_fingerprint_non_mapping_invalid(): assert restricted_read_fingerprint(None) is None
def test_fingerprint_target_is_string(): assert restricted_read_fingerprint({**_action(), "target": 1}) is None
def test_fingerprint_parameters_integer(): assert restricted_read_fingerprint({**_action(), "parameters":{"max_chars":True}}) is None
def test_fingerprint_is_lowercase(): assert (restricted_read_fingerprint(_action()) or "").islower()
def test_fingerprint_excludes_comment(): assert restricted_read_fingerprint(_action()) == restricted_read_fingerprint(_action())
def test_fingerprint_excludes_attempt(): assert restricted_read_fingerprint(_action()) == restricted_read_fingerprint(_action())
def test_fingerprint_is_hex(): assert all(c in "0123456789abcdef" for c in restricted_read_fingerprint(_action()))
def test_fingerprint_has_sha_length(): assert len(restricted_read_fingerprint(_action())) == 64
