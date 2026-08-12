from types import SimpleNamespace
from aether.verification.restricted_file_read import verify_restricted_file_read, STATUSES


def _obs(): return SimpleNamespace(reader_status="success")
def _result(**changes):
    v={"status":"success","truncated":False,"privacy_filtered":True,"read_started":True}; v.update(changes); return v
def test_six_statuses(): assert len(STATUSES)==6
def test_internal_malformed_result(): assert verify_restricted_file_read(authorized=True,reader_result=None,observation=_obs())=="INTERNAL_ERROR"
def test_internal_malformed_observation(): assert verify_restricted_file_read(authorized=True,reader_result=_result(),observation=object())=="INTERNAL_ERROR"
def test_denied_authorization(): assert verify_restricted_file_read(authorized=False,reader_result=_result(),observation=_obs())=="DENIED"
def test_denied_reader(): assert verify_restricted_file_read(authorized=True,reader_result=_result(status="blocked"),observation=_obs())=="DENIED"
def test_not_found(): assert verify_restricted_file_read(authorized=True,reader_result=_result(status="not_found",read_started=False),observation=_obs())=="NOT_FOUND"
def test_changed(): assert verify_restricted_file_read(authorized=True,reader_result=_result(status="changed",changed_during_read=True),observation=_obs())=="CHANGED_DURING_READ"
def test_error(): assert verify_restricted_file_read(authorized=True,reader_result=_result(status="error"),observation=_obs())=="INTERNAL_ERROR"
def test_success(): assert verify_restricted_file_read(authorized=True,reader_result=_result(),observation=_obs())=="VERIFIED_SUCCESS"
def test_partial(): assert verify_restricted_file_read(authorized=True,reader_result=_result(truncated=True),observation=_obs())=="VERIFIED_PARTIAL"
def test_privacy_denial_precedes_partial(): assert verify_restricted_file_read(authorized=True,reader_result=_result(status="blocked",truncated=True),observation=_obs())=="DENIED"
def test_changed_precedes_partial(): assert verify_restricted_file_read(authorized=True,reader_result=_result(status="changed",truncated=True,changed_during_read=True),observation=_obs())=="CHANGED_DURING_READ"
def test_unknown_status_internal(): assert verify_restricted_file_read(authorized=True,reader_result=_result(status="unknown"),observation=_obs())=="INTERNAL_ERROR"
def test_missing_fact_internal():
    r=_result(); del r["privacy_filtered"]; assert verify_restricted_file_read(authorized=True,reader_result=r,observation=_obs())=="INTERNAL_ERROR"
def test_missing_read_started_internal():
    r=_result(); del r["read_started"]; assert verify_restricted_file_read(authorized=True,reader_result=r,observation=_obs())=="INTERNAL_ERROR"
def test_status_literal_success(): assert verify_restricted_file_read(authorized=True,reader_result=_result(),observation=_obs()) in STATUSES
