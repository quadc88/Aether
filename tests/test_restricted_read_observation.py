from aether.action.restricted_file_read_observation import RestrictedReadObservation, observation_from_reader


def _result(**changes):
    v={"id":"a","status":"success","normalized_path":"x.py","regular_file":True,"extension":".py","size_bytes":1,"content":"safe","truncated":False,"privacy_filtered":True}; v.update(changes); return v
def test_exact_type(): assert RestrictedReadObservation.__name__ == "RestrictedReadObservation"
def test_success_mapping(): assert observation_from_reader(_result()).reader_status == "success"
def test_target_mapping(): assert observation_from_reader(_result()).normalized_target == "x.py"
def test_regular_mapping(): assert observation_from_reader(_result()).regular_file is True
def test_extension_mapping(): assert observation_from_reader(_result()).extension == ".py"
def test_size_mapping(): assert observation_from_reader(_result()).size_bytes == 1
def test_content_mapping(): assert observation_from_reader(_result()).content == "safe"
def test_truncated_mapping(): assert observation_from_reader(_result(truncated=True)).truncated is True
def test_action_mapping(): assert observation_from_reader(_result()).action_id == "a"
def test_privacy_mapping(): assert observation_from_reader(_result()).privacy_filtered is True
def test_blocked_content_hidden(): assert observation_from_reader(_result(status="blocked",content="secret")).content is None
def test_changed_status_mapping(): assert observation_from_reader(_result(status="changed")).reader_status == "changed"
