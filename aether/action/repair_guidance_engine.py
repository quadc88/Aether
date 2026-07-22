"""Deterministic, non-mutating repair guidance derived from safe learning records."""
from pathlib import Path
import json,uuid,yaml
from aether.action.repair_learning_index import get_repair_learning_record,list_repair_learning_records
from aether.time.clock import get_timezone,now_iso
from aether.memory.timeline.recorder import record_event
from aether.memory.graph.store import add_edge
from aether.action.mutation_log import record_mutation
FULL=["repair_guidance_engine","repair_plan","repair_bridge_selection","review_bridge","patch_proposal","proposal_review_console","approved_dry_run_gate","dry_run_review_gate","real_apply_approval_gate","final_real_apply_executor","post_apply_verification_gate","repair_cycle_completion_report","repair_learning_index"]
SAFETY=["explicit human proposal review","dry-run before real apply","dry-run human acceptance","final real apply approval","approval queue item must be manually approved","final executor must revalidate approval","backup and rollback availability must be preserved","post-apply verification is required","completion report is required","learning record should be generated after completion"]
def load_aether_config(path="config/aether.yaml"):
 p=Path(path);return yaml.safe_load(p.read_text(encoding="utf-8")) or {} if p.exists() else {}
def get_repair_guidance_dir():return Path(load_aether_config().get("paths",{}).get("private_dir","private"))/"repair_guidance"
def get_repair_guidance_path():return get_repair_guidance_dir()/"repair_guidance_records.json"
def get_public_repair_guidance_dir():return Path("docs/history/repair_guidance")
def get_public_repair_guidance_index_path():return get_public_repair_guidance_dir()/"INDEX.md"
def load_repair_guidance_records():
 p=get_repair_guidance_path()
 try:d=json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
 except json.JSONDecodeError:d={}
 t=now_iso();d.setdefault("type","repair_guidance_records");d.setdefault("version","0.1.0");d.setdefault("created",t);d.setdefault("updated",d["created"]);d.setdefault("timezone",get_timezone());d.setdefault("records",[]);return d
def save_repair_guidance_records(d):
 p=get_repair_guidance_path();p.parent.mkdir(parents=True,exist_ok=True);d["updated"]=now_iso();p.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding="utf-8")
def sanitize_target_path(p):
 s=str(p or "").replace("\\","/");x="C:/Aether/";return s[len(x):] if s.lower().startswith(x.lower()) else (s if s and ":" not in s else None)
def shorten_id(v,keep=12):return str(v)[:keep]+"…" if v and len(str(v))>keep else v
def _save(r):
 d=load_repair_guidance_records();d["records"]=[x for x in d["records"] if x["id"]!=r["id"]]+[r];save_repair_guidance_records(d);return r
def _matches(target):
 records=list_repair_learning_records(status="learned",limit=50);target=sanitize_target_path(target)
 exact=[r for r in records if target and r.get("target_path")==target];same=[r for r in records if target and r.get("target_path","").rsplit("/",1)[0]==target.rsplit("/",1)[0]]
 return (exact or same or records)[:5]
def create_repair_guidance(request_type,requested_scope,target_path=None,source_type=None,source_id=None,export_public=True,export_index=True,export_private=True,metadata=None):
 t=now_iso();target=sanitize_target_path(target_path);m=_matches(target);high=bool(target and ("aether/action/" in target or "aether/interface/" in target)) or "real apply" in (requested_scope or "").lower() or any(x.get("learning_category")=="rollback_pattern" or x.get("risk_category")=="high" for x in m)
 warning=[]
 if not m:warning.append("No matching learning record found; using conservative full gate chain.")
 r={"id":f"repair_guidance_{uuid.uuid4().hex}","created":t,"updated":t,"timezone":get_timezone(),"status":"generated","request_type":request_type,"requested_scope":requested_scope[:240],"target_path":target,"source_type":source_type,"source_id":source_id,"matched_learning_ids":[x["id"] for x in m],"matched_learning_categories":[x.get("learning_category") for x in m],"inferred_risk_category":"high" if high else "medium","guidance_decision":"proceed_with_full_gate_chain" if high or not m else "proceed_with_standard_review","recommended_gate_chain":FULL if high or not m else FULL[:6]+["approved_dry_run_gate","dry_run_review_gate"],"required_safety_checks":SAFETY if high or not m else ["human proposal review","dry-run recommended","safe public output scan","private/runtime path scan"],"proceed_allowed":True,"human_review_required":True,"recommended_next_action":"Create a repair plan or proposal only after human review.","confidence":max([x.get("confidence",0) for x in m],default=0.5),"reasoning_summary":"A matching high-risk rollback learning pattern requires the full guarded gate chain." if high and m else "No matching learning record found; conservative full gate chain selected.","public_report_path":None,"public_index_path":None,"private_export_path":None,"warnings":warning,"metadata":{}}
 _save(r)
 if export_public:export_repair_guidance_report(r["id"])
 if export_index:
  q=export_repair_guidance_index();r=get_repair_guidance_record(r["id"]);r["public_index_path"]=q["public_index_path"];_save(r)
 if export_private:export_private_repair_guidance_record(r["id"])
 try:
  record_event("repair_guidance",f"Repair guidance generated: {r['guidance_decision']}",f"Aether generated repair guidance for {target or requested_scope}.","medium");add_edge("Aether","created_repair_guidance",r["id"]);add_edge(r["id"],"has_guidance_decision",r["guidance_decision"]);add_edge(r["id"],"has_inferred_risk_category",r["inferred_risk_category"]);record_mutation("manual_note","Repair guidance created","Aether generated sanitized guidance from repair learning records.",milestone="Milestone 42 — Repair Guidance Engine",target_path=target,risk_level="low",status="generated",reversible=True,rollback_available=False)
 except Exception:r["warnings"].append("Audit integration was unavailable.")
 return _save(r)
def get_repair_guidance_record(i):return next((r for r in load_repair_guidance_records()["records"] if r["id"]==i),None)
def list_repair_guidance_records(status=None,guidance_decision=None,target_path=None,limit=50):return [r for r in load_repair_guidance_records()["records"] if (not status or r["status"]==status) and (not guidance_decision or r["guidance_decision"]==guidance_decision) and (not target_path or r["target_path"]==target_path)][-limit:][::-1]
def export_repair_guidance_report(i,output_dir="docs/history/repair_guidance",metadata=None):
 r=get_repair_guidance_record(i);d=Path(output_dir);d.mkdir(parents=True,exist_ok=True);p=d/f"{i}.md";p.write_text(f"# Repair Guidance Record\n\n- Guidance: {shorten_id(i)}\n- Target: {r['target_path']}\n- Risk: {r['inferred_risk_category']}\n- Decision: {r['guidance_decision']}\n- Human review required: yes\n\n## Recommended Gate Chain\n\n"+"\n".join(f"{n}. {x}" for n,x in enumerate(r['recommended_gate_chain'],1))+"\n\n## Safety Notes\n\n- Raw excerpts are excluded.\n- Backup paths are excluded.\n- Private runtime paths are excluded.\n",encoding="utf-8");r["public_report_path"]=str(p).replace("\\","/");_save(r);return {"public_report_path":r["public_report_path"]}
def export_repair_guidance_index(output_path="docs/history/repair_guidance/INDEX.md",limit=100,metadata=None):
 p=Path(output_path);p.parent.mkdir(parents=True,exist_ok=True);p.write_text("# Aether Repair Guidance Index\n\nThis index is generated from sanitized repair guidance records.\n",encoding="utf-8");return {"public_index_path":str(p).replace("\\","/")}
def export_private_repair_guidance_record(i,metadata=None):
 r=get_repair_guidance_record(i);p=get_repair_guidance_dir()/"exports"/f"{i}.json";p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps({k:v for k,v in r.items() if k not in {"metadata"}},indent=2),encoding="utf-8");r["private_export_path"]="private guidance export written";_save(r);return {"status":"success"}
def repair_guidance_engine_status():return {"record_count":len(load_repair_guidance_records()["records"]),"policy":"Deterministic guidance only; no model or patch actions."}
def summarize_repair_guidance(i):
 r=get_repair_guidance_record(i);return {k:r.get(k) for k in ("id","status","target_path","matched_learning_ids","inferred_risk_category","guidance_decision","recommended_gate_chain","required_safety_checks","proceed_allowed","human_review_required","confidence","public_report_path","public_index_path","warnings")} if r else None
