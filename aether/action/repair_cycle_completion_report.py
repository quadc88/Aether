"""Sanitized public and private completion reports for guarded repair cycles."""
from pathlib import Path
import json, uuid, yaml
from aether.action.post_apply_verification_gate import get_post_apply_verification_gate_record
from aether.action.final_real_apply_executor import get_final_real_apply_executor_record
from aether.action.patch_apply import get_patch_apply
from aether.action.patch_rollback import get_patch_rollback
from aether.action.mutation_log import record_mutation
from aether.memory.timeline.recorder import record_event
from aether.memory.graph.store import add_edge
from aether.time.clock import get_timezone, now_iso

def load_aether_config(path="config/aether.yaml"):
 p=Path(path);return yaml.safe_load(p.read_text(encoding="utf-8")) or {} if p.exists() else {}
def get_repair_cycle_completion_dir():return Path(load_aether_config().get("paths",{}).get("private_dir","private"))/"repair_cycle_completion"
def get_repair_cycle_completion_path():return get_repair_cycle_completion_dir()/"repair_cycle_completion_records.json"
def get_public_repair_cycle_dir():return Path("docs/history/repair_cycles")
def get_public_repair_cycle_index_path():return get_public_repair_cycle_dir()/"INDEX.md"
def load_repair_cycle_completion_records():
 p=get_repair_cycle_completion_path()
 try:d=json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
 except json.JSONDecodeError:d={}
 t=now_iso();d.setdefault("type","repair_cycle_completion_records");d.setdefault("version","0.1.0");d.setdefault("created",t);d.setdefault("updated",d["created"]);d.setdefault("timezone",get_timezone());d.setdefault("records",[]);return d
def save_repair_cycle_completion_records(d):
 p=get_repair_cycle_completion_path();p.parent.mkdir(parents=True,exist_ok=True);d["updated"]=now_iso();d["timezone"]=get_timezone();p.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding="utf-8")
def sanitize_target_path(path):
 s=str(path or "").replace("\\","/");x="C:/Aether/";return s[len(x):] if s.lower().startswith(x.lower()) else (s if s and not (":" in s or "aetherdata" in s.lower()) else None)
def shorten_id(value,keep=12):return (str(value)[:keep]+"…") if value and len(str(value))>keep else value
def sanitize_completion_record_for_public(r):
 keys=("id","created","status","source_type","post_apply_verification_id","final_real_apply_executor_id","proposal_id","real_patch_apply_id","rollback_record_id","verification_decision","rollback_detected","rollback_available","target_path","cycle_status","final_state","stage_chain","public_report_path","public_index_path","next_recommended_step")
 x={k:r.get(k) for k in keys};x["id"]=shorten_id(x["id"]);x["target_path"]=sanitize_target_path(x["target_path"]);x["warnings_count"]=len(r.get("warnings",[]));x["stage_chain"]=[{**s,"id":shorten_id(s.get("id"))} for s in r.get("stage_chain",[])];return x
def _save(r):
 d=load_repair_cycle_completion_records()
 for i,x in enumerate(d["records"]):
  if x["id"]==r["id"]:d["records"][i]=r;break
 else:d["records"].append(r)
 save_repair_cycle_completion_records(d);return r
def _stage(stage,id,status=None,decision=None):return {"stage":stage,"id":id,"status":status,"decision":decision,"safe_summary":f"{stage.replace('_',' ')} recorded."}
def _audit(r):
 w=[]
 try:
  from aether.core.runtime import runtime
  runtime.working_memory.add_event(role="aether",content=f"Repair cycle completion report created: {r['cycle_status']}",event_type="repair_cycle_completion_report_created",metadata={k:r.get(k) for k in ("id","source_type","source_id","proposal_id","cycle_status","final_state","verification_decision")}|{"record_id":r["id"]})
 except Exception:w.append("Working Memory audit was unavailable.")
 try:record_event("repair_cycle_completion",f"Repair cycle completion: {r['cycle_status']}",f"Aether created a repair cycle completion report {r['id']}.","high")
 except Exception:w.append("Timeline audit was unavailable.")
 try:
  add_edge("Aether","created_repair_cycle_completion_report",r["id"]);add_edge(r["id"],"has_cycle_status",r["cycle_status"]);add_edge(r["id"],"has_final_state",r["final_state"])
  if r.get("proposal_id"):add_edge(r["id"],"documents_proposal",r["proposal_id"])
  if r.get("real_patch_apply_id"):add_edge(r["id"],"documents_real_apply",r["real_patch_apply_id"])
  if r.get("post_apply_verification_id"):add_edge(r["id"],"documents_post_apply_verification",r["post_apply_verification_id"])
  if r.get("rollback_detected") and r.get("rollback_record_id"):add_edge(r["id"],"documents_rollback",r["rollback_record_id"])
 except Exception:w.append("Graph audit was unavailable.")
 try:record_mutation("manual_note","Repair cycle completion report created","Aether generated a sanitized completion report for a guarded repair cycle.",milestone="Milestone 40 — Repair Cycle Completion Report",target_path=r.get("target_path"),risk_level="low",status=r["status"],reversible=bool(r.get("public_report_path")),rollback_available=False)
 except Exception:w.append("Mutation Log integration was unavailable.")
 return w
def create_repair_cycle_completion_report(source_type,source_id,export_public=True,export_index=True,export_private=True,metadata=None):
 t=now_iso();r={"id":f"repair_cycle_completion_{uuid.uuid4().hex}","created":t,"updated":t,"timezone":get_timezone(),"status":"blocked","source_type":source_type,"source_id":source_id,"post_apply_verification_id":None,"final_real_apply_executor_id":None,"real_apply_approval_gate_id":None,"dry_run_review_gate_id":None,"approved_dry_run_gate_id":None,"proposal_review_console_id":None,"proposal_revision_console_id":None,"revised_proposal_review_loop_id":None,"repair_workflow_report_id":None,"proposal_id":None,"real_patch_apply_id":None,"rollback_record_id":None,"verification_decision":None,"rollback_detected":False,"rollback_available":False,"target_path":None,"cycle_status":"blocked","final_state":"unknown","stage_chain":[],"public_report_path":None,"public_index_path":None,"private_export_path":None,"next_recommended_step":"Only post-apply verification records can complete a repair cycle.","warnings":[],"metadata":{str(k)[:80]:str(v)[:160] for k,v in (metadata or {}).items() if "aetherdata" not in str(v).lower()}}
 if source_type!="post_apply_verification_gate":r["warnings"].append("Unsupported repair cycle completion source type.")
 else:
  v=get_post_apply_verification_gate_record(source_id)
  if not v:r["warnings"].append("Post-apply verification record was not found.")
  else:
   r.update({"post_apply_verification_id":source_id,"final_real_apply_executor_id":v.get("final_real_apply_executor_id"),"proposal_id":v.get("proposal_id"),"real_patch_apply_id":v.get("real_patch_apply_id"),"rollback_record_id":v.get("rollback_record_id"),"verification_decision":v.get("verification_decision"),"rollback_detected":bool(v.get("rollback_detected")),"rollback_available":bool(v.get("rollback_available")),"target_path":sanitize_target_path(v.get("target_path"))})
   e=get_final_real_apply_executor_record(r["final_real_apply_executor_id"]) if r["final_real_apply_executor_id"] else None
   if e:r["real_apply_approval_gate_id"]=e.get("real_apply_approval_gate_id")
   chain=[_stage("post_apply_verification",source_id,v.get("status"),v.get("verification_decision")),_stage("final_real_apply_executor",r["final_real_apply_executor_id"],(e or {}).get("status")),_stage("real_apply",r["real_patch_apply_id"],v.get("real_apply_status"))]
   if r["rollback_detected"]:chain.append(_stage("rollback",r["rollback_record_id"],"completed"))
   r["stage_chain"]=[x for x in chain if x.get("id")]
   dec=r["verification_decision"]
   if dec=="verify_success":r.update({"status":"completed","cycle_status":"completed","final_state":"verified_success"})
   elif dec=="already_rolled_back" or r["rollback_detected"]:r.update({"status":"completed","cycle_status":"completed_with_rollback","final_state":"rolled_back_verified"})
   elif dec in {"verify_failed","rollback_recommended"}:r.update({"status":"completed","cycle_status":"completed","final_state":"failed_needs_attention"})
   elif dec=="needs_investigation":r.update({"status":"partial","cycle_status":"completed","final_state":"needs_investigation"})
   else:r.update({"status":"partial","cycle_status":"incomplete"})
   r["next_recommended_step"]="Record milestone completion and continue with future improvements." if r["final_state"] in {"verified_success","rolled_back_verified"} else "Inspect the repair cycle before continuing."
 _save(r)
 if export_public:export_repair_cycle_report(r["id"])
 if export_index:
  index_result=export_repair_cycle_index();r=get_repair_cycle_completion_record(r["id"]);r["public_index_path"]=index_result.get("public_index_path");_save(r)
 if export_private:export_private_repair_cycle_record(r["id"])
 r=get_repair_cycle_completion_record(r["id"]);r["warnings"]+=_audit(r);return _save(r)
def export_repair_cycle_report(completion_record_id,output_dir="docs/history/repair_cycles",metadata=None):
 r=get_repair_cycle_completion_record(completion_record_id)
 if not r:return {"status":"blocked","warnings":["Completion record was not found."]}
 d=Path(output_dir);d.mkdir(parents=True,exist_ok=True);p=d/f"{r['id']}.md";x=sanitize_completion_record_for_public(r)
 lines=["# Repair Cycle Completion Report","","## Summary",f"- Completion: {x['id']}",f"- Cycle status: {x['cycle_status']}",f"- Final state: {x['final_state']}",f"- Target: {x['target_path'] or 'unavailable'}",f"- Verification decision: {x['verification_decision'] or 'unavailable'}",f"- Rollback detected: {'yes' if x['rollback_detected'] else 'no'}",f"- Rollback available: {'yes' if x['rollback_available'] else 'no'}",f"- Next step: {x['next_recommended_step']}","","## Stage Chain",""]
 lines += [f"{i}. {s['stage'].replace('_',' ').title()} — {s['id']} — {s.get('status') or s.get('decision') or 'recorded'}" for i,s in enumerate(x["stage_chain"],1)]
 lines += ["","## Safety Notes","","- Raw excerpts are excluded.","- Backup paths are excluded.","- Private runtime paths are excluded.","- This report is a sanitized public summary.",""]
 p.write_text("\n".join(lines),encoding="utf-8");r["public_report_path"]=str(p).replace("\\","/");_save(r);return {"status":"success","public_report_path":r["public_report_path"]}
def export_repair_cycle_index(output_path="docs/history/repair_cycles/INDEX.md",limit=100,metadata=None):
 p=Path(output_path);p.parent.mkdir(parents=True,exist_ok=True);records=list_repair_cycle_completion_records(limit=limit);lines=["# Aether Repair Cycle Dashboard","","This dashboard is generated from sanitized repair cycle completion records.","","## Summary","",f"- Generated: {now_iso()}",f"- Reports included: {len(records)}","","## Repair Cycles","","| Created | Completion | Target | Cycle Status | Final State | Verification | Next Step |","|---|---|---|---|---|---|---|"]
 for r in records:
  x=sanitize_completion_record_for_public(r);lines.append(f"| {x['created'][:10]} | {x['id']} | {x['target_path'] or 'unavailable'} | {x['cycle_status']} | {x['final_state']} | {x['verification_decision'] or 'unavailable'} | {x['next_recommended_step']} |")
 p.write_text("\n".join(lines)+"\n",encoding="utf-8");return {"status":"success","public_index_path":str(p).replace("\\","/")}
def export_private_repair_cycle_record(completion_record_id,metadata=None):
 r=get_repair_cycle_completion_record(completion_record_id)
 if not r:return {"status":"blocked","warnings":["Completion record was not found."]}
 p=get_repair_cycle_completion_dir()/"exports"/f"{r['id']}.json";p.parent.mkdir(parents=True,exist_ok=True);safe={k:v for k,v in r.items() if k not in {"metadata"}};p.write_text(json.dumps(safe,indent=2,ensure_ascii=False),encoding="utf-8");r["private_export_path"]="private completion export written";_save(r);return {"status":"success","private_export_written":True}
def get_repair_cycle_completion_record(i):return next((r for r in load_repair_cycle_completion_records()["records"] if r["id"]==i),None)
def list_repair_cycle_completion_records(status=None,proposal_id=None,limit=50):return [r for r in load_repair_cycle_completion_records()["records"] if (not status or r.get("status")==status) and (not proposal_id or r.get("proposal_id")==proposal_id)][-max(0,limit):][::-1]
def repair_cycle_completion_status():
 d=load_repair_cycle_completion_records();return {"record_count":len(d["records"]),"created":d["created"],"updated":d["updated"],"timezone":d["timezone"],"policy":"Creates sanitized repair-cycle reports only; never applies or rolls back patches."}
def summarize_repair_cycle_completion(i):
 r=get_repair_cycle_completion_record(i)
 if not r:return None
 x=sanitize_completion_record_for_public(r);return {k:x.get(k) for k in ("id","status","source_type","source_id","post_apply_verification_id","final_real_apply_executor_id","proposal_id","real_patch_apply_id","rollback_record_id","verification_decision","rollback_detected","rollback_available","target_path","cycle_status","final_state","public_report_path","public_index_path","next_recommended_step","warnings_count")}
