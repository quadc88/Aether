"""Human-approved proposal dry-run gate; never performs a real apply."""
from pathlib import Path
import json,uuid,yaml
from aether.action.proposal_review_console import get_proposal_review_console_record
from aether.action.revised_proposal_review_loop import get_revised_proposal_review_loop_record
from aether.action.patch_review import get_patch_review
from aether.action.patch_proposal import get_patch_proposal
from aether.action.patch_apply import apply_patch_proposal
from aether.time.clock import get_timezone,now_iso
def load_aether_config(path="config/aether.yaml"):
 p=Path(path);return yaml.safe_load(p.read_text(encoding="utf-8")) or {} if p.exists() else {}
def get_approved_dry_run_gate_dir():return Path(load_aether_config().get("paths",{}).get("private_dir","private"))/"approved_dry_run_gate"
def get_approved_dry_run_gate_path():return get_approved_dry_run_gate_dir()/"approved_dry_run_gate_records.json"
def load_approved_dry_run_gate_records():
 p=get_approved_dry_run_gate_path()
 try:d=json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
 except json.JSONDecodeError:d={}
 t=now_iso();d.setdefault("type","approved_dry_run_gate_records");d.setdefault("version","0.1.0");d.setdefault("created",t);d.setdefault("updated",d["created"]);d.setdefault("timezone",get_timezone());d.setdefault("records",[]);return d
def save_approved_dry_run_gate_records(d):
 p=get_approved_dry_run_gate_path();p.parent.mkdir(parents=True,exist_ok=True);d["updated"]=now_iso();d["timezone"]=get_timezone();p.write_text(json.dumps(d,indent=2),encoding="utf-8")
def _target(v):
 s=str(v or "").replace("\\","/");x="C:/Aether/";return s[len(x):] if s.lower().startswith(x.lower()) else None
def _save(r):
 d=load_approved_dry_run_gate_records()
 for i,x in enumerate(d["records"]):
  if x["id"]==r["id"]:d["records"][i]=r;break
 else:d["records"].append(r)
 save_approved_dry_run_gate_records(d);return r
def open_approved_dry_run_gate(source_type,source_id,metadata=None):
 t=now_iso();r={"id":f"approved_dry_run_gate_{uuid.uuid4().hex}","created":t,"updated":t,"timezone":get_timezone(),"status":"blocked","source_type":source_type,"source_id":source_id,"proposal_id":None,"patch_review_id":None,"review_decision":None,"patch_apply_id":None,"dry_run_status":None,"proposal_status":None,"target_path":None,"current_step":"approval_validation","next_recommended_step":"Only approved proposals can enter the dry-run gate.","warnings":[],"metadata":metadata or {}}
 p=None
 if source_type=="proposal_review_console":
  x=get_proposal_review_console_record(source_id);r.update({"proposal_id":(x or {}).get("proposal_id"),"patch_review_id":(x or {}).get("patch_review_id"),"review_decision":(x or {}).get("review_decision")});p=get_patch_proposal(r["proposal_id"])
 elif source_type=="revised_proposal_review_loop":
  x=get_revised_proposal_review_loop_record(source_id);r.update({"proposal_id":(x or {}).get("revised_proposal_id"),"patch_review_id":(x or {}).get("patch_review_id"),"review_decision":(x or {}).get("review_decision")});p=get_patch_proposal(r["proposal_id"])
 elif source_type=="patch_review":
  x=get_patch_review(source_id);r.update({"proposal_id":(x or {}).get("proposal_id"),"patch_review_id":source_id,"review_decision":(x or {}).get("review_decision")});p=get_patch_proposal(r["proposal_id"])
 elif source_type=="patch_proposal":r["proposal_id"]=source_id;p=get_patch_proposal(source_id)
 else:r["warnings"].append("Unsupported dry-run gate source type.")
 if not p:r["warnings"].append("Approved proposal was not found.")
 else:
  r.update({"proposal_status":p.get("status"),"target_path":_target(p.get("target_path") or p.get("normalized_path"))})
  if r["review_decision"]=="approve" or p.get("status")=="approved":r.update({"status":"ready","current_step":"approved_for_dry_run","next_recommended_step":"Execute the guarded dry-run."})
  else:r["warnings"].append("Proposal is not approved.")
 return _save(r)
def execute_approved_dry_run(gate_record_id,create_approval_if_required=False,metadata=None):
 r=get_approved_dry_run_gate_record(gate_record_id)
 if not r:return {"id":gate_record_id,"status":"blocked","warnings":["Dry-run gate record was not found."]}
 if r["status"]=="dry_run_completed" and not (metadata or {}).get("force_dry_run"):r["status"]="blocked";r["warnings"].append("Dry-run has already been completed.")
 elif r["status"]!="ready":r["status"]="blocked";r["warnings"].append("Dry-run gate is not ready.")
 else:
  a=apply_patch_proposal(r["proposal_id"],True,{**(metadata or {}),"source":"approved_dry_run_gate","gate_record_id":gate_record_id,"approval_requested":bool(create_approval_if_required)})
  r.update({"patch_apply_id":a.get("id"),"dry_run_status":a.get("status"),"status":"dry_run_completed" if a.get("status")=="dry_run" else "blocked","current_step":"dry_run_completed","next_recommended_step":"Human should inspect dry-run result before any real apply approval."});r["warnings"]+=a.get("warnings",[])
 r["updated"]=now_iso();return _save(r)
def get_approved_dry_run_gate_record(i):return next((r for r in load_approved_dry_run_gate_records()["records"] if r["id"]==i),None)
def list_approved_dry_run_gate_records(status=None,proposal_id=None,limit=50):return [r for r in load_approved_dry_run_gate_records()["records"] if (not status or r["status"]==status) and (not proposal_id or r.get("proposal_id")==proposal_id)][-limit:][::-1]
def approved_dry_run_gate_status():d=load_approved_dry_run_gate_records();return {"record_count":len(d["records"]),"policy":"Dry-run gate hard-codes dry_run=True and never performs real apply."}
def summarize_approved_dry_run_gate(i):
 r=get_approved_dry_run_gate_record(i);return {k:r.get(k) for k in ("id","status","source_type","source_id","proposal_id","patch_review_id","review_decision","patch_apply_id","dry_run_status","proposal_status","target_path","current_step","next_recommended_step","warnings")} if r else None
