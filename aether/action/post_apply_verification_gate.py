"""Safe human verification records for completed real patch applies; never changes files."""
from pathlib import Path
import json, uuid, yaml
from aether.action.final_real_apply_executor import get_final_real_apply_executor_record
from aether.action.patch_apply import get_patch_apply
from aether.action.patch_rollback import get_patch_rollback, list_patch_rollbacks
from aether.action.patch_proposal import get_patch_proposal
from aether.action.mutation_log import record_mutation
from aether.memory.timeline.recorder import record_event
from aether.memory.graph.store import add_edge
from aether.time.clock import get_timezone, now_iso

SOURCE_TYPES={"final_real_apply_executor","patch_apply","patch_rollback"}
DECISIONS={"verify_success","verify_failed","rollback_recommended","needs_investigation","already_rolled_back"}

def load_aether_config(path="config/aether.yaml"):
 p=Path(path);return yaml.safe_load(p.read_text(encoding="utf-8")) or {} if p.exists() else {}
def get_post_apply_verification_gate_dir():return Path(load_aether_config().get("paths",{}).get("private_dir","private"))/"post_apply_verification_gate"
def get_post_apply_verification_gate_path():return get_post_apply_verification_gate_dir()/"post_apply_verification_gate_records.json"
def load_post_apply_verification_gate_records():
 p=get_post_apply_verification_gate_path()
 try:d=json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
 except json.JSONDecodeError:d={}
 t=now_iso();d.setdefault("type","post_apply_verification_gate_records");d.setdefault("version","0.1.0");d.setdefault("created",t);d.setdefault("updated",d["created"]);d.setdefault("timezone",get_timezone());d.setdefault("records",[]);return d
def save_post_apply_verification_gate_records(d):
 p=get_post_apply_verification_gate_path();p.parent.mkdir(parents=True,exist_ok=True);d["updated"]=now_iso();d["timezone"]=get_timezone();p.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding="utf-8")
def _target(v):
 s=str(v or "").replace("\\","/");x="C:/Aether/";return s[len(x):] if s.lower().startswith(x.lower()) else None
def _metadata(m):
 bad=("c:/aetherdata","backup","original_excerpt","proposed_excerpt","diff","token","secret","password","key",".env")
 return {str(k)[:80]:str(v)[:160] for k,v in (m or {}).items() if not any(x in str(k).lower() or x in str(v).lower().replace("\\","/") for x in bad)} if isinstance(m,dict) else {}
def _save(r):
 d=load_post_apply_verification_gate_records()
 for i,x in enumerate(d["records"]):
  if x["id"]==r["id"]:d["records"][i]=r;break
 else:d["records"].append(r)
 save_post_apply_verification_gate_records(d);return r
def _rollback(apply_id):
 records=list_patch_rollbacks(apply_id,200)
 record=next((r for r in records if r.get("status")=="success"),None)
 return record
def _audit(r,event):
 w=[]
 try:
  from aether.core.runtime import runtime
  runtime.working_memory.add_event(role="aether",content=f"Post-apply verification {event}: {r['status']}",event_type="post_apply_verification_gate_opened" if event=="opened" else "post_apply_verification_submitted",metadata={"record_id":r["id"],"source_type":r.get("source_type"),"source_id":r.get("source_id"),"proposal_id":r.get("proposal_id"),"real_patch_apply_id":r.get("real_patch_apply_id"),"verification_decision":r.get("verification_decision"),"status":r["status"]})
 except Exception:w.append("Working Memory audit was unavailable.")
 try:
  if event=="opened":record_event("post_apply_verification_gate",f"Post-apply verification gate opened: {r['status']}",f"Aether opened post-apply verification for proposal {r.get('proposal_id') or 'unknown'}.","high")
  else:record_event("post_apply_verification",f"Post-apply verification submitted: {r.get('verification_decision')}",f"Human verification was submitted for real apply {r.get('real_patch_apply_id') or 'unknown'}.","high")
 except Exception:w.append("Timeline audit was unavailable.")
 try:
  if event=="opened":
   add_edge("Aether","opened_post_apply_verification_gate",r["id"]);add_edge(r["id"],"from_source",r["source_id"]);add_edge(r["id"],"has_status",r["status"])
   if r.get("proposal_id"):add_edge(r["id"],"for_proposal",r["proposal_id"])
   if r.get("real_patch_apply_id"):add_edge(r["id"],"reviews_real_apply",r["real_patch_apply_id"])
   if r.get("rollback_detected"):add_edge(r["id"],"detected_rollback",r["rollback_record_id"])
  else:add_edge(r["id"],"post_apply_verification_decision",r.get("verification_decision") or "unknown")
 except Exception:w.append("Graph audit was unavailable.")
 try:record_mutation("manual_note","Post-apply verification gate opened" if event=="opened" else "Post-apply verification submitted","Aether opened a human verification gate for a completed real apply." if event=="opened" else "A human submitted a post-apply verification decision.",milestone="Milestone 39 — Post-Apply Verification Gate",target_path=r.get("target_path") if event!="opened" else None,risk_level="medium",status=r["status"],reversible=False,rollback_available=bool(r.get("rollback_available")))
 except Exception:w.append("Mutation Log integration was unavailable.")
 return w
def open_post_apply_verification_gate(source_type,source_id,metadata=None):
 t=now_iso();r={"id":f"post_apply_verification_gate_{uuid.uuid4().hex}","created":t,"updated":t,"timezone":get_timezone(),"status":"blocked","source_type":source_type,"source_id":source_id,"final_real_apply_executor_id":None,"proposal_id":None,"real_patch_apply_id":None,"real_apply_status":None,"rollback_available":False,"rollback_detected":False,"rollback_record_id":None,"backup_created":False,"proposal_status":None,"target_path":None,"verification_decision":None,"verification_comment":None,"verifier":None,"current_step":"real_apply_validation","next_recommended_step":"Only completed real apply records can enter post-apply verification.","warnings":[],"metadata":_metadata(metadata)}
 apply=None;rollback=None
 if source_type not in SOURCE_TYPES:r["warnings"].append("Unsupported post-apply verification source type.")
 elif source_type=="final_real_apply_executor":
  x=get_final_real_apply_executor_record(source_id)
  if x:r.update({"final_real_apply_executor_id":source_id,"proposal_id":x.get("proposal_id"),"real_patch_apply_id":x.get("real_patch_apply_id"),"real_apply_status":x.get("real_apply_status"),"rollback_available":bool(x.get("rollback_available")),"backup_created":bool(x.get("backup_created"))});apply=get_patch_apply(r["real_patch_apply_id"])
  else:r["warnings"].append("Final real apply executor record was not found.")
 elif source_type=="patch_apply":
  apply=get_patch_apply(source_id)
  if apply:r.update({"proposal_id":apply.get("proposal_id"),"real_patch_apply_id":source_id,"real_apply_status":apply.get("status"),"rollback_available":bool(apply.get("backup_path")) and bool(apply.get("applied")),"backup_created":bool(apply.get("backup_path"))})
 else:
  rollback=get_patch_rollback(source_id)
  if rollback:r.update({"proposal_id":rollback.get("proposal_id"),"real_patch_apply_id":rollback.get("apply_id"),"rollback_detected":True,"rollback_record_id":source_id,"rollback_available":True,"real_apply_status":"rolled_back"});apply=get_patch_apply(r["real_patch_apply_id"])
  else:r["warnings"].append("Patch rollback record was not found.")
 if apply:
  if not r.get("proposal_id"):r["proposal_id"]=apply.get("proposal_id")
  if not r.get("real_apply_status"):r["real_apply_status"]=apply.get("status")
  rollback=rollback or _rollback(r.get("real_patch_apply_id"))
  if rollback:r.update({"rollback_detected":True,"rollback_record_id":rollback.get("id")})
 proposal=get_patch_proposal(r.get("proposal_id"))
 if proposal:r.update({"proposal_status":proposal.get("status"),"target_path":_target(proposal.get("target_path") or proposal.get("normalized_path"))})
 valid=bool((apply and not apply.get("dry_run") and apply.get("status")=="success" and apply.get("applied")) or (rollback and rollback.get("status")=="success"))
 if valid:r.update({"status":"opened","current_step":"rollback_detected" if r["rollback_detected"] else "post_apply_review_ready","next_recommended_step":"Record post-rollback verification or inspect mutation log." if r["rollback_detected"] else "Human should verify the applied change."})
 else:r["warnings"].append("Completed real apply record was not found.")
 r["warnings"]+=_audit(r,"opened");return _save(r)
def submit_post_apply_verification(verification_record_id,decision,comment=None,verifier="human",metadata=None):
 r=get_post_apply_verification_gate_record(verification_record_id)
 if not r:return {"id":verification_record_id,"status":"blocked","warnings":["Post-apply verification record was not found."]}
 if r.get("status")!="opened" and not (metadata or {}).get("force_verification"):return {"id":verification_record_id,"status":"blocked","warnings":["Post-apply verification is not open."]}
 if decision not in DECISIONS:return {"id":verification_record_id,"status":"blocked","warnings":["Invalid post-apply verification decision."]}
 steps={"verify_success":"Record milestone completion and export workflow/changelog.","verify_failed":"Consider rollback through the existing rollback flow.","rollback_recommended":"Open rollback workflow through the existing rollback flow; this gate does not rollback.","needs_investigation":"Inspect applied behavior before deciding.","already_rolled_back":"Record rollback verification and inspect mutation history."}
 r.update({"status":"verified","verification_decision":decision,"verification_comment":str(comment or "")[:300],"verifier":verifier or "human","current_step":"post_apply_verification_completed","next_recommended_step":steps[decision],"updated":now_iso()});r["warnings"]+=_audit(r,"submitted");return _save(r)
def get_post_apply_verification_gate_record(i):return next((r for r in load_post_apply_verification_gate_records()["records"] if r["id"]==i),None)
def list_post_apply_verification_gate_records(status=None,proposal_id=None,limit=50):return [r for r in load_post_apply_verification_gate_records()["records"] if (not status or r.get("status")==status) and (not proposal_id or r.get("proposal_id")==proposal_id)][-max(0,limit):][::-1]
def post_apply_verification_gate_status():
 d=load_post_apply_verification_gate_records();return {"record_count":len(d["records"]),"created":d["created"],"updated":d["updated"],"timezone":d["timezone"],"policy":"Records post-apply verification only; never applies or rolls back patches."}
def summarize_post_apply_verification_gate(i):
 r=get_post_apply_verification_gate_record(i);keys=("id","status","source_type","source_id","final_real_apply_executor_id","proposal_id","real_patch_apply_id","real_apply_status","rollback_available","rollback_detected","rollback_record_id","backup_created","proposal_status","target_path","verification_decision","verifier","current_step","next_recommended_step","warnings");return {k:r.get(k) for k in keys} if r else None
