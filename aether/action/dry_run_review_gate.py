"""Human review record for a completed dry-run; never applies or rolls back."""
from pathlib import Path
import json,uuid,yaml
from aether.action.approved_dry_run_gate import get_approved_dry_run_gate_record
from aether.action.patch_apply import get_patch_apply
from aether.time.clock import get_timezone,now_iso
DECISIONS={"accept","reject","request_changes","needs_investigation"}
def load_aether_config(path="config/aether.yaml"):
 p=Path(path);return yaml.safe_load(p.read_text(encoding="utf-8")) or {} if p.exists() else {}
def get_dry_run_review_gate_dir():return Path(load_aether_config().get("paths",{}).get("private_dir","private"))/"dry_run_review_gate"
def get_dry_run_review_gate_path():return get_dry_run_review_gate_dir()/"dry_run_review_gate_records.json"
def load_dry_run_review_gate_records():
 p=get_dry_run_review_gate_path()
 try:d=json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
 except json.JSONDecodeError:d={}
 t=now_iso();d.setdefault("type","dry_run_review_gate_records");d.setdefault("version","0.1.0");d.setdefault("created",t);d.setdefault("updated",d["created"]);d.setdefault("timezone",get_timezone());d.setdefault("records",[]);return d
def save_dry_run_review_gate_records(d):
 p=get_dry_run_review_gate_path();p.parent.mkdir(parents=True,exist_ok=True);d["updated"]=now_iso();p.write_text(json.dumps(d,indent=2),encoding="utf-8")
def _target(v):
 s=str(v or "").replace("\\","/");x="C:/Aether/";return s[len(x):] if s.lower().startswith(x.lower()) else None
def _save(r):
 d=load_dry_run_review_gate_records()
 for i,x in enumerate(d["records"]):
  if x["id"]==r["id"]:d["records"][i]=r;break
 else:d["records"].append(r)
 save_dry_run_review_gate_records(d);return r
def open_dry_run_review_gate(source_type,source_id,metadata=None):
 t=now_iso();r={"id":f"dry_run_review_gate_{uuid.uuid4().hex}","created":t,"updated":t,"timezone":get_timezone(),"status":"blocked","source_type":source_type,"source_id":source_id,"approved_dry_run_gate_id":None,"proposal_id":None,"patch_review_id":None,"patch_apply_id":None,"dry_run_status":None,"dry_run_mode":None,"dry_run_review_decision":None,"dry_run_review_comment":None,"reviewer":None,"proposal_status":None,"target_path":None,"current_step":"dry_run_validation","next_recommended_step":"Only completed dry-run records can enter dry-run result review.","warnings":[],"metadata":metadata or {}}
 a=None
 if source_type=="approved_dry_run_gate":
  g=get_approved_dry_run_gate_record(source_id);r.update({"approved_dry_run_gate_id":source_id,"proposal_id":(g or {}).get("proposal_id"),"patch_review_id":(g or {}).get("patch_review_id"),"patch_apply_id":(g or {}).get("patch_apply_id"),"dry_run_status":(g or {}).get("dry_run_status"),"proposal_status":(g or {}).get("proposal_status"),"target_path":(g or {}).get("target_path")});a=get_patch_apply(r["patch_apply_id"])
  valid=bool(g and g.get("status")=="dry_run_completed")
 elif source_type=="patch_apply":
  a=get_patch_apply(source_id);r.update({"patch_apply_id":source_id,"proposal_id":(a or {}).get("proposal_id"),"dry_run_status":(a or {}).get("status"),"proposal_status":(a or {}).get("proposal_status"),"target_path":_target((a or {}).get("target_path") or (a or {}).get("normalized_path"))});valid=False
 else:valid=False;r["warnings"].append("Unsupported dry-run review source type.")
 if a:r["dry_run_mode"]="dry_run" if a.get("dry_run") else "not_dry_run";r["target_path"]=_target(a.get("target_path") or a.get("normalized_path"));valid=valid and a.get("dry_run") and a.get("status")=="dry_run" if source_type=="approved_dry_run_gate" else bool(a.get("dry_run") and a.get("status") in {"dry_run","success"})
 if valid:r.update({"status":"opened","current_step":"dry_run_result_ready","next_recommended_step":"Human should review the dry-run result."})
 else:r["warnings"].append("Completed dry-run record was not found.")
 return _save(r)
def submit_dry_run_review(review_gate_record_id,decision,comment=None,reviewer="human",metadata=None):
 r=get_dry_run_review_gate_record(review_gate_record_id)
 if not r:return {"id":review_gate_record_id,"status":"blocked","warnings":["Dry-run review gate record was not found."]}
 if r["status"]=="reviewed" and not (metadata or {}).get("force_review"):r["status"]="blocked";r["warnings"].append("Dry-run result has already been reviewed.")
 elif r["status"]!="opened":r["status"]="blocked";r["warnings"].append("Dry-run review gate is not open.")
 elif decision not in DECISIONS:r["status"]="blocked";r["warnings"].append("Invalid dry-run review decision.")
 else:
  r.update({"status":"reviewed","dry_run_review_decision":decision,"dry_run_review_comment":str(comment or "")[:300],"reviewer":reviewer or "human","current_step":"dry_run_review_completed","next_recommended_step":{"accept":"Proceed to real-apply approval gate in a future milestone.","reject":"Stop this proposal or create a new proposal.","request_changes":"Open proposal revision console before another dry-run.","needs_investigation":"Inspect dry-run result before continuing."}[decision]})
 r["updated"]=now_iso();return _save(r)
def get_dry_run_review_gate_record(i):return next((r for r in load_dry_run_review_gate_records()["records"] if r["id"]==i),None)
def list_dry_run_review_gate_records(status=None,proposal_id=None,limit=50):return [r for r in load_dry_run_review_gate_records()["records"] if (not status or r["status"]==status) and (not proposal_id or r.get("proposal_id")==proposal_id)][-limit:][::-1]
def dry_run_review_gate_status():return {"record_count":len(load_dry_run_review_gate_records()["records"]),"policy":"Records human dry-run decisions only; never applies patches."}
def summarize_dry_run_review_gate(i):
 r=get_dry_run_review_gate_record(i);return {k:r.get(k) for k in ("id","status","source_type","source_id","approved_dry_run_gate_id","proposal_id","patch_review_id","patch_apply_id","dry_run_status","dry_run_mode","dry_run_review_decision","reviewer","proposal_status","target_path","current_step","next_recommended_step","warnings")} if r else None
