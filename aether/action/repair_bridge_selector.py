"""Explicit selection of a repair-plan bridge candidate; never applies changes."""
from pathlib import Path
import json,uuid,yaml
from aether.action.repair_planner import get_repair_plan
from aether.action.review_bridge import create_bridge_from_finding
from aether.time.clock import get_timezone,now_iso
from aether.memory.timeline.recorder import record_event
from aether.memory.graph.store import add_edge
from aether.action.mutation_log import record_mutation
def load_aether_config(path="config/aether.yaml"):
 p=Path(path);return yaml.safe_load(p.read_text(encoding="utf-8")) or {} if p.exists() else {}
def get_repair_bridge_selection_dir():return Path(load_aether_config().get("paths",{}).get("private_dir","private"))/"repair_bridge_selections"
def get_repair_bridge_selection_path():return get_repair_bridge_selection_dir()/"repair_bridge_selections.json"
def load_repair_bridge_selections():
 p=get_repair_bridge_selection_path()
 try:d=json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
 except json.JSONDecodeError:d={}
 t=now_iso();d.setdefault("type","repair_bridge_selections");d.setdefault("version","0.1.0");d.setdefault("created",t);d.setdefault("updated",t);d.setdefault("timezone",get_timezone());d.setdefault("records",[]);return d
def save_repair_bridge_selections(d):
 p=get_repair_bridge_selection_path();p.parent.mkdir(parents=True,exist_ok=True);d["updated"]=now_iso();p.write_text(json.dumps(d,indent=2),encoding="utf-8")
def _audit_repair_bridge_selection(r):
 warnings=[]
 try:
  from aether.core.runtime import runtime
  runtime.working_memory.add_event(role="aether",content=f"Repair bridge selection created: {r['id']} ({r['status']}).",event_type="repair_bridge_selection_created",metadata={k:r.get(k) for k in ("id","repair_plan_id","review_report_id","finding_id","status","bridge_record_id","session_id","proposal_id")}|{"record_id":r["id"]})
 except Exception as e:warnings.append(f"Working Memory audit was unavailable: {e}")
 try:record_event("repair_bridge_selection",f"Repair bridge selection: {r['status']}",f"Aether selected repair-plan finding {r['finding_id']} for review bridge.","high" if r["status"] in {"blocked","failed"} else "normal")
 except Exception as e:warnings.append(f"Timeline audit was unavailable: {e}")
 try:
  add_edge("Aether","created_repair_bridge_selection",r["id"]);add_edge(r["id"],"from_repair_plan",r["repair_plan_id"]);add_edge(r["id"],"selected_finding",r["finding_id"]);add_edge(r["id"],"has_status",r["status"])
  if r.get("bridge_record_id"):add_edge(r["id"],"created_review_bridge",r["bridge_record_id"])
  if r.get("session_id"):add_edge(r["id"],"created_self_modification_session",r["session_id"])
  if r.get("proposal_id"):add_edge(r["id"],"created_patch_proposal",r["proposal_id"])
  if r.get("target_path"):add_edge(r["id"],"targets_file",r["target_path"])
 except Exception as e:warnings.append(f"Graph audit was unavailable: {e}")
 try:record_mutation("manual_note","Repair plan bridge candidate selected","Aether selected a repair-plan bridge candidate and created a guarded review bridge.",milestone="Milestone 29 — Repair Plan to Review Bridge Selection",target_path=r.get("target_path"),risk_level="medium",status=r["status"],reversible=False,rollback_available=False)
 except Exception as e:warnings.append(f"Mutation Log integration was unavailable: {e}")
 return warnings
def create_bridge_from_repair_plan(repair_plan_id,finding_id,proposed_excerpt,original_excerpt=None,proposed_change_summary=None,reason=None,create_approval_if_required=False,metadata=None):
 p=get_repair_plan(repair_plan_id);t=now_iso();r={"id":f"repair_bridge_selection_{uuid.uuid4().hex}","created":t,"updated":t,"timezone":get_timezone(),"status":"blocked","repair_plan_id":repair_plan_id,"review_report_id":p.get("review_report_id") if p else None,"finding_id":finding_id,"finding_priority_level":None,"finding_priority_score":None,"finding_title":None,"target_path":None,"proposed_excerpt":proposed_excerpt[:8000],"original_excerpt":original_excerpt[:4000] if original_excerpt else None,"proposed_change_summary":proposed_change_summary,"reason":reason,"bridge_record_id":None,"session_id":None,"proposal_id":None,"current_step":"candidate_validation","next_recommended_step":"Human should review the generated patch proposal before any dry-run or apply.","warnings":[],"metadata":metadata or {}}
 if not p:r["warnings"].append("Repair plan not found.")
 elif finding_id not in p.get("bridge_candidates",[]):r["warnings"].append("Finding is not an approved bridge candidate.")
 elif not proposed_excerpt:r["warnings"].append("A proposed excerpt is required.")
 else:
  f=next((x for x in p["prioritized_findings"] if x["finding_id"]==finding_id),None)
  if not f:r["warnings"].append("Prioritized finding not found.")
  else:
   r.update({"finding_priority_level":f["priority_level"],"finding_priority_score":f["priority_score"],"finding_title":f["title"],"target_path":f["target_path"],"reason":reason or f"Generated from repair plan {repair_plan_id}, bridge candidate {finding_id}."})
   b=create_bridge_from_finding(p["review_report_id"],finding_id,proposed_excerpt,original_excerpt,proposed_change_summary or f["recommended_action"],r["reason"],create_approval_if_required,{**(metadata or {}),"source":"repair_bridge_selector","repair_plan_id":repair_plan_id});r.update({"bridge_record_id":b["id"],"session_id":b.get("session_id"),"proposal_id":b.get("proposal_id"),"status":"bridge_created" if b["status"]=="session_created" else "blocked","current_step":"bridge_created"})
 r["warnings"]+=_audit_repair_bridge_selection(r);d=load_repair_bridge_selections();d["records"].append(r);save_repair_bridge_selections(d);return r
def get_repair_bridge_selection(i):return next((r for r in load_repair_bridge_selections()["records"] if r["id"]==i),None)
def list_repair_bridge_selections(status=None,repair_plan_id=None,limit=50):return [r for r in load_repair_bridge_selections()["records"] if (not status or r["status"]==status) and (not repair_plan_id or r["repair_plan_id"]==repair_plan_id)][-limit:][::-1]
def repair_bridge_selection_status():return {"repair_bridge_selection_path":str(get_repair_bridge_selection_path()),"record_count":len(load_repair_bridge_selections()["records"])}
def summarize_repair_bridge_selection(i):
 r=get_repair_bridge_selection(i);return {k:r.get(k) for k in ("id","status","repair_plan_id","finding_id","bridge_record_id","session_id","proposal_id","target_path","next_recommended_step","warnings")} if r else None
