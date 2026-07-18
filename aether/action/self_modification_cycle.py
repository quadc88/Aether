"""Approval-preserving workflow wrapper for Aether self-modification."""
from pathlib import Path
import json,uuid,yaml
from aether.action.patch_proposal import create_patch_proposal
from aether.action.patch_review import review_patch_proposal
from aether.action.patch_apply import apply_patch_proposal
from aether.action.patch_rollback import rollback_patch_apply
from aether.time.clock import get_timezone,now_iso
from aether.memory.timeline.recorder import record_event
from aether.memory.graph.store import add_edge
def load_aether_config(path="config/aether.yaml"):
 p=Path(path);return yaml.safe_load(p.read_text(encoding="utf-8")) or {} if p.exists() else {}
def get_self_modification_dir():return Path(load_aether_config().get("paths",{}).get("private_dir","private"))/"self_modification"
def get_self_modification_path():return get_self_modification_dir()/"self_modification_sessions.json"
def load_self_modification_sessions():
 p=get_self_modification_path()
 try:d=json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
 except json.JSONDecodeError:d={}
 t=now_iso();d.setdefault("type","self_modification_sessions");d.setdefault("version","0.1.0");d.setdefault("created",t);d.setdefault("updated",t);d.setdefault("timezone",get_timezone());d.setdefault("sessions",[]);return d
def save_self_modification_sessions(d):
 p=get_self_modification_path();p.parent.mkdir(parents=True,exist_ok=True);d["updated"]=now_iso();p.write_text(json.dumps(d,indent=2),encoding="utf-8")
def _save(s):
 d=load_self_modification_sessions();
 for i,x in enumerate(d["sessions"]):
  if x["id"]==s["id"]:d["sessions"][i]=s;break
 else:d["sessions"].append(s)
 save_self_modification_sessions(d)
 try:
  from aether.core.runtime import runtime
  runtime.working_memory.add_event(role="aether",content=f"Self-modification session updated: {s['status']}",event_type="self_modification_session_updated",metadata={k:s.get(k) for k in ("id","status","proposal_id","review_id","apply_id","rollback_id","risk_level","current_step","next_recommended_step")})
 except Exception as error:s["warnings"].append(f"Working Memory audit was unavailable: {error}")
 try:
  record_event("self_modification",f"Self-modification session: {s['status']}",f"Aether updated self-modification session {s['id']}.","high" if s["status"] in {"applied","rolled_back","blocked","failed","approval_required"} else "normal")
  for source,relation,target in [("Aether","created_self_modification_session",s["id"]),(s["id"],"targets_file",s["normalized_path"]),(s["id"],"has_status",s["status"])]:add_edge(source,relation,target)
 except Exception as error:s["warnings"].append(f"Session audit integration was unavailable: {error}")
 return s
def create_self_modification_session(goal,target_path,proposed_change_summary,proposed_excerpt,reason="",original_excerpt=None,create_approval_if_required=False,metadata=None):
 p=create_patch_proposal(target_path,goal,proposed_change_summary,proposed_excerpt,reason,original_excerpt,create_approval_if_required,metadata);status="approval_required" if p["status"]=="approval_required" else "review_pending" if p["status"]=="draft" else "blocked";t=now_iso();s={"id":f"self_modification_{uuid.uuid4().hex}","created":t,"updated":t,"timezone":get_timezone(),"status":status,"goal":goal,"target_path":target_path,"normalized_path":p["normalized_path"],"request_text":goal,"proposed_change_summary":proposed_change_summary,"reason":reason,"proposal_id":p["id"],"review_id":None,"approval_id":p.get("approval_id"),"apply_id":None,"rollback_id":None,"risk_level":p["risk_level"],"requires_user_approval":p["requires_user_approval"],"dry_run_status":None,"apply_status":None,"rollback_status":None,"current_step":"proposal_created","next_recommended_step":"Request an explicit review decision.","history":[{"step":"proposal_created","proposal_id":p["id"],"status":p["status"]}],"checks":[],"warnings":p.get("warnings",[]),"metadata":metadata or {}};return _save(s)
def get_self_modification_session(i):return next((s for s in load_self_modification_sessions()["sessions"] if s["id"]==i),None)
def list_self_modification_sessions(status=None,target_path=None,limit=50):return [s for s in load_self_modification_sessions()["sessions"] if (not status or s["status"]==status) and (not target_path or s["target_path"]==target_path)][-limit:][::-1]
def self_modification_status():return {"self_modification_path":str(get_self_modification_path()),"session_count":len(load_self_modification_sessions()["sessions"])}
def review_self_modification_session(i,decision,review_reason="",reviewer="user",metadata=None):
 s=get_self_modification_session(i);r=review_patch_proposal(s["proposal_id"],decision,review_reason,reviewer,metadata);s["review_id"]=r.get("id");s["status"]="review_approved" if r.get("proposal_status_after")=="approved" else "review_rejected" if decision=="reject" else "blocked" if r["status"]!="success" else "review_pending";s["history"].append({"step":"review_created","review_id":r.get("id"),"decision":decision});return _save(s)
def dry_run_self_modification_session(i,metadata=None):
 s=get_self_modification_session(i);a=apply_patch_proposal(s["proposal_id"],True,metadata);s["apply_id"]=a["id"];s["dry_run_status"]=a["status"];s["status"]="dry_run_ready" if a["status"]=="dry_run" else "blocked";s["history"].append({"step":"dry_run","apply_id":a["id"],"status":a["status"]});return _save(s)
def apply_self_modification_session(i,metadata=None):
 s=get_self_modification_session(i);a=apply_patch_proposal(s["proposal_id"],False,metadata);s["apply_id"]=a["id"];s["apply_status"]=a["status"];s["status"]="applied" if a["status"]=="success" else "blocked";s["history"].append({"step":"patch_applied","apply_id":a["id"],"status":a["status"]});return _save(s)
def rollback_self_modification_session(i,metadata=None):
 s=get_self_modification_session(i);r=rollback_patch_apply(s["apply_id"],False,metadata);s["rollback_id"]=r["id"];s["rollback_status"]=r["status"];s["status"]="rolled_back" if r["status"]=="success" else "blocked";s["history"].append({"step":"rollback_performed","rollback_id":r["id"],"status":r["status"]});return _save(s)
def summarize_self_modification_session(i):
 s=get_self_modification_session(i);return {k:s.get(k) for k in ("id","status","goal","target_path","risk_level","requires_user_approval","proposal_id","review_id","approval_id","apply_id","rollback_id","current_step","next_recommended_step","history","warnings")}
