"""Bridge a restricted review finding into a guarded self-modification session."""
from pathlib import Path
import json,uuid,yaml
from aether.action.code_reviewer import get_code_review
from aether.action.self_modification_cycle import create_self_modification_session
from aether.time.clock import get_timezone,now_iso
from aether.memory.timeline.recorder import record_event
from aether.memory.graph.store import add_edge
from aether.action.mutation_log import record_mutation
def load_aether_config(path="config/aether.yaml"):
 p=Path(path);return yaml.safe_load(p.read_text(encoding="utf-8")) or {} if p.exists() else {}
def get_review_bridge_dir():return Path(load_aether_config().get("paths",{}).get("private_dir","private"))/"review_bridge"
def get_review_bridge_path():return get_review_bridge_dir()/"review_bridge_records.json"
def load_review_bridge_records():
 p=get_review_bridge_path()
 try:d=json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
 except json.JSONDecodeError:d={}
 t=now_iso();d.setdefault("type","review_bridge_records");d.setdefault("version","0.1.0");d.setdefault("created",t);d.setdefault("updated",t);d.setdefault("timezone",get_timezone());d.setdefault("records",[]);return d
def save_review_bridge_records(d):
 p=get_review_bridge_path();p.parent.mkdir(parents=True,exist_ok=True);d["updated"]=now_iso();p.write_text(json.dumps(d,indent=2),encoding="utf-8")
def _audit_review_bridge_record(r):
 warnings=[]
 try:
  from aether.core.runtime import runtime
  runtime.working_memory.add_event(role="aether",content=f"Review bridge created: {r['status']}",event_type="review_bridge_created",metadata={"bridge_id":r["id"],"report_id":r["review_report_id"],"finding_id":r["finding_id"],"status":r["status"],"session_id":r["session_id"],"proposal_id":r["proposal_id"],"target_path":r["target_path"]})
 except Exception as e:warnings.append(f"Working Memory audit was unavailable: {e}")
 try:record_event("review_bridge",f"Review bridge: {r['status']}",f"Aether created review-to-self-modification bridge {r['id']}.","high" if r["status"] in {"blocked","failed"} else "normal")
 except Exception as e:warnings.append(f"Timeline audit was unavailable: {e}")
 try:
  for s,rel,t in [("Aether","created_review_bridge",r["id"]),(r["id"],"from_code_review",r["review_report_id"]),(r["id"],"from_finding",r["finding_id"]),(r["id"],"has_status",r["status"])]:add_edge(s,rel,t)
  if r["target_path"]:add_edge(r["id"],"targets_file",r["target_path"])
  if r["session_id"]:add_edge(r["id"],"created_self_modification_session",r["session_id"])
  if r["proposal_id"]:add_edge(r["id"],"created_patch_proposal",r["proposal_id"])
 except Exception as e:warnings.append(f"Graph audit was unavailable: {e}")
 try:record_mutation("manual_note","Review finding bridged to self-modification","Aether created a guarded self-modification session from a restricted code review finding.",milestone="Milestone 27 — Review-to-Self-Modification Bridge",target_path=r["target_path"],risk_level="medium",status=r["status"])
 except Exception as e:warnings.append(f"Mutation Log integration was unavailable: {e}")
 return warnings
def create_bridge_from_finding(report_id,finding_id,proposed_excerpt,original_excerpt=None,proposed_change_summary=None,reason=None,create_approval_if_required=False,metadata=None):
 report=get_code_review(report_id);finding=next((f for f in (report or {}).get("findings",[]) if f["id"]==finding_id),None);t=now_iso();r={"id":f"review_bridge_{uuid.uuid4().hex}","created":t,"updated":t,"timezone":get_timezone(),"status":"blocked","review_report_id":report_id,"finding_id":finding_id,"finding_severity":finding.get("severity") if finding else None,"finding_category":finding.get("category") if finding else None,"finding_title":finding.get("title") if finding else None,"target_path":finding.get("target_path") if finding else None,"proposed_goal":None,"proposed_change_summary":proposed_change_summary,"proposed_excerpt":proposed_excerpt[:8000],"original_excerpt":original_excerpt[:4000] if original_excerpt else None,"reason":reason,"session_id":None,"proposal_id":None,"risk_level":None,"requires_user_approval":False,"current_step":"finding_selected","next_recommended_step":"Human should review the generated patch proposal before any dry-run or apply.","warnings":[],"metadata":metadata or {}}
 if not report:r["warnings"].append("Code review report not found.")
 elif not finding:r["warnings"].append("Code review finding not found.")
 elif not finding.get("target_path"):r["warnings"].append("Finding has no target path.")
 elif not proposed_excerpt:r["warnings"].append("A proposed excerpt is required.")
 else:
  r["proposed_goal"]=f"Address code review finding: {finding['title']}";r["proposed_change_summary"]=proposed_change_summary or f"{finding['category']}: {finding['recommendation']}";r["reason"]=reason or f"Generated from restricted code review {report_id}, finding {finding_id}."
  try:
   s=create_self_modification_session(r["proposed_goal"],finding["target_path"],r["proposed_change_summary"],proposed_excerpt,r["reason"],original_excerpt,create_approval_if_required,{**(metadata or {}),"source":"review_bridge","review_report_id":report_id,"finding_id":finding_id});r.update({"status":"session_created","session_id":s["id"],"proposal_id":s["proposal_id"],"risk_level":s["risk_level"],"requires_user_approval":s["requires_user_approval"],"current_step":"session_created"})
  except Exception as e:r["status"]="failed";r["warnings"].append(str(e))
 r["warnings"]+=_audit_review_bridge_record(r);d=load_review_bridge_records();d["records"].append(r);save_review_bridge_records(d);return r
def get_review_bridge_record(i):return next((r for r in load_review_bridge_records()["records"] if r["id"]==i),None)
def list_review_bridge_records(status=None,review_report_id=None,limit=50):return [r for r in load_review_bridge_records()["records"] if (not status or r["status"]==status) and (not review_report_id or r["review_report_id"]==review_report_id)][-limit:][::-1]
def review_bridge_status():return {"review_bridge_path":str(get_review_bridge_path()),"record_count":len(load_review_bridge_records()["records"])}
def summarize_review_bridge_record(i):
 r=get_review_bridge_record(i);return {k:r.get(k) for k in ("id","status","review_report_id","finding_id","session_id","proposal_id","target_path","next_recommended_step","warnings")} if r else None
