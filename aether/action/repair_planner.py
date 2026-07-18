"""Deterministic, private repair planning from restricted code-review findings."""
from pathlib import Path
import json,uuid,yaml
from aether.action.code_reviewer import get_code_review
from aether.time.clock import get_timezone,now_iso
from aether.memory.timeline.recorder import record_event
from aether.memory.graph.store import add_edge
from aether.action.mutation_log import record_mutation
SCORES={"critical":100,"high":80,"medium":55,"low":30,"info":10};ADJ={"safety_boundary":20,"data_privacy":20,"unsafe_path_handling":15,"tool_policy":15,"missing_validation":10,"error_handling":8,"possible_bug":8,"test_gap":3,"documentation_gap":-5,"architecture_alignment":5}
def load_aether_config(path="config/aether.yaml"):
 p=Path(path);return yaml.safe_load(p.read_text(encoding="utf-8")) or {} if p.exists() else {}
def get_repair_plan_dir():return Path(load_aether_config().get("paths",{}).get("private_dir","private"))/"repair_plans"
def get_repair_plan_path():return get_repair_plan_dir()/"repair_plans.json"
def load_repair_plans():
 p=get_repair_plan_path()
 try:d=json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
 except json.JSONDecodeError:d={}
 t=now_iso();d.setdefault("type","repair_plans");d.setdefault("version","0.1.0");d.setdefault("created",t);d.setdefault("updated",t);d.setdefault("timezone",get_timezone());d.setdefault("plans",[]);return d
def save_repair_plans(d):
 p=get_repair_plan_path();p.parent.mkdir(parents=True,exist_ok=True);d["updated"]=now_iso();p.write_text(json.dumps(d,indent=2),encoding="utf-8")
def _audit_repair_plan(p):
 warnings=[]; urgent=sum(x["priority_level"]=="urgent" for x in p["prioritized_findings"]); high=sum(x["priority_level"]=="high" for x in p["prioritized_findings"])
 try:
  from aether.core.runtime import runtime
  runtime.working_memory.add_event(role="aether",content=f"Repair plan created: {p['id']}",event_type="repair_plan_created",metadata={"plan_id":p["id"],"review_report_id":p["review_report_id"],"status":p["status"],"finding_count":p["finding_count"],"urgent_count":urgent,"high_count":high,"bridge_candidate_count":len(p["bridge_candidates"])})
 except Exception as e:warnings.append(f"Working Memory audit was unavailable: {e}")
 try:record_event("repair_plan",f"Repair plan created: {p['review_report_id']}",f"Aether created repair plan {p['id']} from code review {p['review_report_id']}.","high" if urgent or high else "normal")
 except Exception as e:warnings.append(f"Timeline audit was unavailable: {e}")
 try:
  add_edge("Aether","created_repair_plan",p["id"]);add_edge(p["id"],"from_code_review",p["review_report_id"]);add_edge(p["id"],"has_status",p["status"])
  for f in p["prioritized_findings"]:add_edge(p["id"],"prioritizes_finding",f["finding_id"])
  for f in p["bridge_candidates"]:add_edge(p["id"],"suggests_bridge_candidate",f)
 except Exception as e:warnings.append(f"Graph audit was unavailable: {e}")
 try:record_mutation("manual_note","Repair plan created from code review","Aether prioritized restricted code review findings into a safe repair plan.",milestone="Milestone 28 — Review Finding Prioritization / Repair Planning",risk_level="medium",status=p["status"])
 except Exception as e:warnings.append(f"Mutation Log integration was unavailable: {e}")
 return warnings
def create_repair_plan(review_report_id,scope=None,include_deferred=True,max_findings=50,metadata=None):
 r=get_code_review(review_report_id);t=now_iso()
 if not r:return {"id":f"repair_plan_{uuid.uuid4().hex}","status":"blocked","review_report_id":review_report_id,"warnings":["Code review report not found."]}
 if not r.get("findings"):
  p={"id":f"repair_plan_{uuid.uuid4().hex}","created":t,"updated":t,"timezone":get_timezone(),"status":"partial","review_report_id":review_report_id,"scope":scope or r.get("scope", ""),"finding_count":0,"prioritized_findings":[],"repair_groups":[],"bridge_candidates":[],"summary":"No findings were available for prioritization.","risk_summary":{},"recommended_order":[],"defer_list":[],"blocked_findings":[],"warnings":["No findings available in the selected code review report."],"metadata":metadata or {}};p["warnings"]+=_audit_repair_plan(p);d=load_repair_plans();d["plans"].append(p);save_repair_plans(d);return p
 items=[]
 for f in r["findings"][:max_findings]:
  score=SCORES.get(f.get("severity"),10)+ADJ.get(f.get("category"),0);path=f.get("target_path","").replace("\\","/").lower();score+=20 if path.endswith("tool_executor.py") or path.endswith("patch_apply.py") else 18 if path.endswith("self_modification_cycle.py") else 14 if path.endswith("api_server.py") else -8 if path.endswith("readme.md") else 0;level="urgent" if score>=95 else "high" if score>=75 else "medium" if score>=50 else "low" if score>=25 else "defer";suitable=bool(f.get("target_path")) and f.get("severity")!="info" and f.get("category")!="documentation_gap";items.append({"finding_id":f["id"],"severity":f["severity"],"category":f["category"],"title":f["title"],"target_path":f.get("target_path"),"priority_score":score,"priority_level":level,"rationale":"Deterministic severity, category, and target-risk scoring.","recommended_action":f.get("recommendation"),"bridge_suitable":suitable,"bridge_reason":"Concrete non-info finding with a target file." if suitable else "Requires human design or is informational.","requires_human_design":not suitable,"estimated_complexity":"small" if score<75 else "medium"})
 items.sort(key=lambda x:x["priority_score"],reverse=True);items=[x for x in items if include_deferred or x["priority_level"]!="defer"];p={"id":f"repair_plan_{uuid.uuid4().hex}","created":t,"updated":t,"timezone":get_timezone(),"status":"completed","review_report_id":review_report_id,"scope":scope or r["scope"],"finding_count":len(items),"prioritized_findings":items,"repair_groups":[],"bridge_candidates":[x["finding_id"] for x in items if x["bridge_suitable"]],"summary":f"Prioritized {len(items)} findings without creating sessions or proposals.","risk_summary":{},"recommended_order":[x["finding_id"] for x in items],"defer_list":[x["finding_id"] for x in items if x["priority_level"]=="defer"],"blocked_findings":[],"warnings":[],"metadata":metadata or {}};p["warnings"]+=_audit_repair_plan(p);d=load_repair_plans();d["plans"].append(p);save_repair_plans(d);return p
def get_repair_plan(i):return next((p for p in load_repair_plans()["plans"] if p["id"]==i),None)
def list_repair_plans(status=None,review_report_id=None,limit=50):return [p for p in load_repair_plans()["plans"] if (not status or p["status"]==status) and (not review_report_id or p["review_report_id"]==review_report_id)][-limit:][::-1]
def repair_plan_status():return {"repair_plan_path":str(get_repair_plan_path()),"plan_count":len(load_repair_plans()["plans"])}
def summarize_repair_plan(i):
 p=get_repair_plan(i);return {"id":p["id"],"status":p["status"],"finding_count":p["finding_count"],"bridge_candidate_count":len(p["bridge_candidates"]),"recommended_order":p["recommended_order"]} if p else None
