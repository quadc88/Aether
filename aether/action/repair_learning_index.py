"""Deterministic, sanitized lessons from completed Aether repair cycles."""
from pathlib import Path
import json,uuid,yaml
from aether.action.repair_cycle_completion_report import get_repair_cycle_completion_record
from aether.time.clock import get_timezone,now_iso
from aether.memory.timeline.recorder import record_event
from aether.memory.graph.store import add_edge
from aether.action.mutation_log import record_mutation
def load_aether_config(path="config/aether.yaml"):
 p=Path(path);return yaml.safe_load(p.read_text(encoding="utf-8")) or {} if p.exists() else {}
def get_repair_learning_dir():return Path(load_aether_config().get("paths",{}).get("private_dir","private"))/"repair_learning"
def get_repair_learning_path():return get_repair_learning_dir()/"repair_learning_records.json"
def get_public_repair_learning_dir():return Path("docs/history/repair_learning")
def get_public_repair_learning_index_path():return get_public_repair_learning_dir()/"INDEX.md"
def load_repair_learning_records():
 p=get_repair_learning_path()
 try:d=json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
 except json.JSONDecodeError:d={}
 t=now_iso();d.setdefault("type","repair_learning_records");d.setdefault("version","0.1.0");d.setdefault("created",t);d.setdefault("updated",d["created"]);d.setdefault("timezone",get_timezone());d.setdefault("records",[]);return d
def save_repair_learning_records(d):
 p=get_repair_learning_path();p.parent.mkdir(parents=True,exist_ok=True);d["updated"]=now_iso();d["timezone"]=get_timezone();p.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding="utf-8")
def sanitize_target_path(p):
 s=str(p or "").replace("\\","/");x="C:/Aether/";return s[len(x):] if s.lower().startswith(x.lower()) else (s if s and ":" not in s else None)
def shorten_id(v,keep=12):return (str(v)[:keep]+"…") if v and len(str(v))>keep else v
def sanitize_learning_record_for_public(r):
 keys=("id","created","status","completion_record_id","proposal_id","target_path","cycle_status","final_state","verification_decision","rollback_detected","rollback_available","learning_category","risk_category","lesson_summary","future_guidance","recommended_future_gate","confidence","evidence_chain","public_report_path","public_index_path")
 x={k:r.get(k) for k in keys};x["id"]=shorten_id(x["id"]);x["target_path"]=sanitize_target_path(x["target_path"]);x["warnings_count"]=len(r.get("warnings",[]));x["evidence_chain"]=[{**e,"id":shorten_id(e.get("id"))} for e in r.get("evidence_chain",[])];return x
def _save(r):
 d=load_repair_learning_records()
 for i,x in enumerate(d["records"]):
  if x["id"]==r["id"]:d["records"][i]=r;break
 else:d["records"].append(r)
 save_repair_learning_records(d);return r
def _audit(r):
 try:
  from aether.core.runtime import runtime;runtime.working_memory.add_event(role="aether",content=f"Repair learning recorded: {r['learning_category']}",event_type="repair_learning_record_created",metadata={k:r.get(k) for k in ("id","source_type","source_id","completion_record_id","learning_category","risk_category","recommended_future_gate","confidence")}|{"record_id":r["id"]})
 except Exception:r["warnings"].append("Working Memory audit was unavailable.")
 try:record_event("repair_learning",f"Repair learning recorded: {r['learning_category']}",f"Aether recorded a safe lesson from repair cycle {r.get('completion_record_id') or 'unknown'}.","medium")
 except Exception:r["warnings"].append("Timeline audit was unavailable.")
 try:
  add_edge("Aether","created_repair_learning_record",r["id"]);add_edge(r["id"],"learned_from_completion",r.get("completion_record_id") or "unknown");add_edge(r["id"],"has_learning_category",r["learning_category"]);add_edge(r["id"],"has_risk_category",r["risk_category"]);add_edge(r["id"],"recommends_future_gate",r["recommended_future_gate"])
 except Exception:r["warnings"].append("Graph audit was unavailable.")
 try:record_mutation("manual_note","Repair learning record created","Aether created a sanitized learning record from a completed repair cycle.",milestone="Milestone 41 — Self-Repair Cycle Learning Index",target_path=r.get("target_path"),risk_level="low",status=r["status"],reversible=bool(r.get("public_report_path")),rollback_available=False)
 except Exception:r["warnings"].append("Mutation Log integration was unavailable.")
def create_repair_learning_record(source_type,source_id,export_public=True,export_index=True,export_private=True,metadata=None):
 t=now_iso();r={"id":f"repair_learning_{uuid.uuid4().hex}","created":t,"updated":t,"timezone":get_timezone(),"status":"blocked","source_type":source_type,"source_id":source_id,"completion_record_id":None,"proposal_id":None,"target_path":None,"cycle_status":None,"final_state":None,"verification_decision":None,"rollback_detected":False,"rollback_available":False,"learning_category":"unknown_pattern","risk_category":"unknown","lesson_summary":"No safe repair-cycle lesson could be derived.","future_guidance":"Inspect the source record before reuse.","recommended_future_gate":"human_investigation","confidence":0.25,"evidence_chain":[],"public_report_path":None,"public_index_path":None,"private_export_path":None,"warnings":[],"metadata":{}}
 c=get_repair_cycle_completion_record(source_id) if source_type=="repair_cycle_completion" else None
 if not c:r["warnings"].append("Repair cycle completion record was not found.")
 else:
  r.update({"status":"learned","completion_record_id":source_id,"proposal_id":c.get("proposal_id"),"target_path":sanitize_target_path(c.get("target_path")),"cycle_status":c.get("cycle_status"),"final_state":c.get("final_state"),"verification_decision":c.get("verification_decision"),"rollback_detected":bool(c.get("rollback_detected")),"rollback_available":bool(c.get("rollback_available"))})
  rollback=r["rollback_detected"] or r["final_state"]=="rolled_back_verified"
  r.update({"learning_category":"rollback_pattern" if rollback else "successful_pattern" if r["final_state"]=="verified_success" else "failed_pattern" if r["final_state"]=="failed_needs_attention" else "investigation_pattern" if r["final_state"]=="needs_investigation" else "unknown_pattern","risk_category":"high" if r["proposal_id"] and (r["rollback_detected"] or c.get("real_patch_apply_id")) else "low","confidence":0.9 if all([r["proposal_id"],c.get("real_patch_apply_id"),r["verification_decision"],r["rollback_detected"]]) else 0.75})
  if rollback:r.update({"lesson_summary":"The repair cycle demonstrated that Aether can execute a fully approved real apply, preserve rollback availability, perform rollback through the existing rollback flow, and record post-apply verification without exposing private data.","future_guidance":"Future high-risk self-modification should preserve the same gate chain: proposal review, dry-run, dry-run review, final real apply approval, final executor validation, rollback availability, post-apply verification, and completion reporting.","recommended_future_gate":"post_apply_verification_gate"})
  r["evidence_chain"]=[{"type":"repair_cycle_completion","id":source_id,"status":r["cycle_status"],"decision":r["final_state"],"safe_note":"Sanitized completion record."},{"type":"real_apply","id":c.get("real_patch_apply_id"),"status":"success","decision":None,"safe_note":"Real apply was recorded."},{"type":"rollback","id":c.get("rollback_record_id"),"status":"completed","decision":None,"safe_note":"Rollback was detected."}]
 _save(r)
 if export_public:export_repair_learning_report(r["id"])
 if export_index:
  q=export_repair_learning_index();r=get_repair_learning_record(r["id"]);r["public_index_path"]=q.get("public_index_path");_save(r)
 if export_private:export_private_repair_learning_record(r["id"])
 r=get_repair_learning_record(r["id"]);_audit(r);return _save(r)
def export_repair_learning_report(i,output_dir="docs/history/repair_learning",metadata=None):
 r=get_repair_learning_record(i)
 if not r:return {"status":"blocked"}
 d=Path(output_dir);d.mkdir(parents=True,exist_ok=True);p=d/f"{r['id']}.md";x=sanitize_learning_record_for_public(r);lines=["# Repair Learning Record","","## Summary",f"- Learning: {x['id']}",f"- Source completion: {shorten_id(x['completion_record_id'])}",f"- Category: {x['learning_category']}",f"- Risk: {x['risk_category']}",f"- Target: {x['target_path']}",f"- Final state: {x['final_state']}",f"- Verification decision: {x['verification_decision']}",f"- Confidence: {x['confidence']}",f"- Recommended future gate: {x['recommended_future_gate']}","","## Lesson","",x["lesson_summary"],"","## Future Guidance","",x["future_guidance"],"","## Safety Notes","","- Raw excerpts are excluded.","- Backup paths are excluded.","- Private runtime paths are excluded."]
 p.write_text("\n".join(lines)+"\n",encoding="utf-8");r["public_report_path"]=str(p).replace("\\","/");_save(r);return {"status":"success","public_report_path":r["public_report_path"]}
def export_repair_learning_index(output_path="docs/history/repair_learning/INDEX.md",limit=100,metadata=None):
 p=Path(output_path);p.parent.mkdir(parents=True,exist_ok=True);rows=list_repair_learning_records(limit=limit);lines=["# Aether Repair Learning Index","","This index is generated from sanitized self-repair learning records.","",f"- Generated: {now_iso()}",f"- Records included: {len(rows)}","","| Created | Learning | Target | Category | Risk | Final State | Recommended Gate | Confidence |","|---|---|---|---|---|---|---|---|"]
 for r in rows:
  x=sanitize_learning_record_for_public(r);lines.append(f"| {x['created'][:10]} | {x['id']} | {x['target_path']} | {x['learning_category']} | {x['risk_category']} | {x['final_state']} | {x['recommended_future_gate']} | {x['confidence']} |")
 p.write_text("\n".join(lines)+"\n",encoding="utf-8");return {"status":"success","public_index_path":str(p).replace("\\","/")}
def export_private_repair_learning_record(i,metadata=None):
 r=get_repair_learning_record(i)
 if not r:return {"status":"blocked"}
 p=get_repair_learning_dir()/"exports"/f"{r['id']}.json";p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps({k:v for k,v in r.items() if k!="metadata"},indent=2),encoding="utf-8");r["private_export_path"]="private learning export written";_save(r);return {"status":"success"}
def get_repair_learning_record(i):return next((r for r in load_repair_learning_records()["records"] if r["id"]==i),None)
def list_repair_learning_records(status=None,learning_category=None,target_path=None,limit=50):return [r for r in load_repair_learning_records()["records"] if (not status or r["status"]==status) and (not learning_category or r["learning_category"]==learning_category) and (not target_path or r.get("target_path")==target_path)][-limit:][::-1]
def repair_learning_index_status():return {"record_count":len(load_repair_learning_records()["records"]),"policy":"Deterministic sanitized learning only; no model calls or patch actions."}
def summarize_repair_learning_record(i):
 r=get_repair_learning_record(i);return sanitize_learning_record_for_public(r) if r else None
