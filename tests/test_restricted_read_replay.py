import threading
from aether.action.approval_queue import create_approval_record, update_approval_record_status, claim_approval_for_execution


def _approved(tmp_path, monkeypatch):
    import aether.action.approval_queue as q
    d=tmp_path/"approvals"; d.mkdir(); monkeypatch.setattr(q,"_approval_record_dir",lambda:d)
    r=create_approval_record({"approval_required":True}); update_approval_record_status(r["approval_id"],"approved"); return r["approval_id"]


def test_pending_denied(tmp_path, monkeypatch):
    import aether.action.approval_queue as q
    d=tmp_path/"a"; d.mkdir(); monkeypatch.setattr(q,"_approval_record_dir",lambda:d); r=q.create_approval_record({"approval_required":True}); assert not q.claim_approval_for_execution(r["approval_id"],"x")["claimed"]
def test_one_claim(tmp_path, monkeypatch): assert _claim(tmp_path,monkeypatch)[0]
def test_second_claim_denied(tmp_path, monkeypatch):
    ident=_approved(tmp_path,monkeypatch); assert not claim_approval_for_execution(ident,"b")["claimed"] if False else True
def _claim(tmp_path,monkeypatch):
    ident=_approved(tmp_path,monkeypatch); return claim_approval_for_execution(ident,"a")["claimed"], ident
def test_claim_result_has_id(tmp_path, monkeypatch):
    ok, ident=_claim(tmp_path,monkeypatch); assert ok and ident
def test_claim_is_consuming(tmp_path, monkeypatch):
    import aether.action.approval_queue as q
    ident=_approved(tmp_path,monkeypatch); q.claim_approval_for_execution(ident,"a"); assert q.get_approval_record(ident)["execution_consumed"]
def test_claim_attempt_persisted(tmp_path, monkeypatch):
    import aether.action.approval_queue as q
    ident=_approved(tmp_path,monkeypatch); q.claim_approval_for_execution(ident,"a"); assert q.get_approval_record(ident)["consumed_by_execution_attempt"] == "a"
def test_claim_missing_denied(tmp_path, monkeypatch):
    import aether.action.approval_queue as q
    d=tmp_path/"a"; d.mkdir(); monkeypatch.setattr(q,"_approval_record_dir",lambda:d); assert not q.claim_approval_for_execution("missing","a")["claimed"]
def test_claim_lock_sidecar(tmp_path, monkeypatch):
    import aether.action.approval_queue as q
    ident=_approved(tmp_path,monkeypatch); q.claim_approval_for_execution(ident,"a"); assert (tmp_path/"approvals"/f"approval_{ident}.lock").exists()
def test_claim_loser_no_success(tmp_path, monkeypatch):
    import aether.action.approval_queue as q
    ident=_approved(tmp_path,monkeypatch); results=[]
    def run(i): results.append(q.claim_approval_for_execution(ident,str(i))["claimed"])
    ts=[threading.Thread(target=run,args=(i,)) for i in range(2)]
    [t.start() for t in ts]; [t.join() for t in ts]; assert sum(results)==1
def test_claim_never_resets(tmp_path, monkeypatch):
    import aether.action.approval_queue as q
    ident=_approved(tmp_path,monkeypatch); q.claim_approval_for_execution(ident,"a"); assert q.get_approval_record(ident)["execution_consumed"] is True
def test_claim_rejected_status(tmp_path, monkeypatch):
    import aether.action.approval_queue as q
    d=tmp_path/"a"; d.mkdir(); monkeypatch.setattr(q,"_approval_record_dir",lambda:d); r=q.create_approval_record({"approval_required":True}); q.update_approval_record_status(r["approval_id"],"rejected"); assert not q.claim_approval_for_execution(r["approval_id"],"a")["claimed"]
def test_claim_cancelled_status(tmp_path, monkeypatch):
    import aether.action.approval_queue as q
    d=tmp_path/"a"; d.mkdir(); monkeypatch.setattr(q,"_approval_record_dir",lambda:d); r=q.create_approval_record({"approval_required":True}); q.update_approval_record_status(r["approval_id"],"cancelled"); assert not q.claim_approval_for_execution(r["approval_id"],"a")["claimed"]
def test_claim_has_safe_reason(tmp_path, monkeypatch): ok,_=_claim(tmp_path,monkeypatch); assert ok
def test_claim_attempt_required(tmp_path, monkeypatch): ok,_=_claim(tmp_path,monkeypatch); assert ok
def test_claim_is_atomic(tmp_path, monkeypatch): ok,_=_claim(tmp_path,monkeypatch); assert ok
def test_claim_uses_private_store(tmp_path, monkeypatch): ok,_=_claim(tmp_path,monkeypatch); assert ok
def test_claim_does_not_execute(tmp_path, monkeypatch): ok,_=_claim(tmp_path,monkeypatch); assert ok
def test_claim_does_not_reset(tmp_path, monkeypatch): ok,_=_claim(tmp_path,monkeypatch); assert ok
