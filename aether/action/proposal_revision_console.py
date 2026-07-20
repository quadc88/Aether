"""Safe revision console for proposals with explicitly requested changes."""
from pathlib import Path
import json, uuid, yaml
from aether.action.proposal_review_console import get_proposal_review_console_record
from aether.action.patch_review import get_patch_review
from aether.action.patch_proposal import get_patch_proposal, create_patch_proposal
from aether.action.mutation_log import record_mutation
from aether.memory.timeline.recorder import record_event
from aether.memory.graph.store import add_edge
from aether.time.clock import get_timezone, now_iso

SOURCE_TYPES={"proposal_review_console","patch_review","patch_proposal"}
SENSITIVE=("c:/aetherdata","backup_path","pre_rollback","original_excerpt","proposed_excerpt","patch_text","diff_preview","token","secret","password","api_key","private_key","id_rsa","id_ed25519",".env")
def load_aether_config(path="config/aether.yaml"):
 p=Path(path);return yaml.safe_load(p.read_text(encoding="utf-8")) or {} if p.exists() else {}
def get_proposal_revision_console_dir():return Path(load_aether_config().get("paths",{}).get("private_dir","private"))/"proposal_revision_console"
def get_proposal_revision_console_path():return get_proposal_revision_console_dir()/"proposal_revision_console_records.json"
def load_proposal_revision_console_records():
 p=get_proposal_revision_console_path()
 try:d=json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
 except json.JSONDecodeError:d={}
 t=now_iso();d.setdefault("type","proposal_revision_console_records");d.setdefault("version","0.1.0");d.setdefault("created",t);d.setdefault("updated",d["created"]);d.setdefault("timezone",get_timezone());d.setdefault("records",[]);return d
def save_proposal_revision_console_records(d):
 p=get_proposal_revision_console_path();p.parent.mkdir(parents=True,exist_ok=True);d["updated"]=now_iso();d["timezone"]=get_timezone();p.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding="utf-8")
def _safe(v,limit=300):
 t=str(v or "")[:limit];return "[redacted]" if any(x in t.lower().replace("\\","/") for x in SENSITIVE) else t
def _target(path):
 t=str(path or "").replace("\\","/");prefix="C:/Aether/";return t[len(prefix):] if t.lower().startswith(prefix.lower()) else None
def _metadata(m):return {str(k)[:80]:_safe(v,160) for k,v in (m or {}).items() if not any(x in str(k).lower() for x in SENSITIVE)} if isinstance(m,dict) else {}
def _save(r):
 d=load_proposal_revision_console_records()
 for n,x in enumerate(d["records"]):
  if x["id"]==r["id"]:d["records"][n]=r;break
 else:d["records"].append(r)
 save_proposal_revision_console_records(d);return r
def _audit(r,event):
 w=[]
 try:
  from aether.core.runtime import runtime
  runtime.working_memory.add_event(role="aether",content=f"Proposal revision {event}: {r['status']}",event_type="proposal_revision_console_opened" if event=="opened" else "proposal_revision_created",metadata={k:r.get(k) for k in ("id","source_type","source_id","original_proposal_id","revised_proposal_id","status")}|{"record_id":r["id"]})
 except Exception:w.append("Working Memory audit was unavailable.")
 try:record_event("proposal_revision_console" if event=="opened" else "proposal_revision",f"Proposal revision console opened: {r['status']}" if event=="opened" else "Proposal revision created",f"Aether opened a revision console for proposal {r.get('original_proposal_id') or 'unknown'}." if event=="opened" else f"Aether created a revised proposal from {r.get('original_proposal_id') or 'unknown'}.","normal")
 except Exception:w.append("Timeline audit was unavailable.")
 try:
  if event=="opened":
   add_edge("Aether","opened_proposal_revision_console",r["id"]);add_edge(r["id"],"from_source",r["source_id"]);add_edge(r["id"],"has_status",r["status"])
   if r.get("original_proposal_id"):add_edge(r["id"],"revises_proposal",r["original_proposal_id"])
   if r.get("self_modification_session_id"):add_edge(r["id"],"for_self_modification_session",r["self_modification_session_id"])
   if r.get("patch_review_id"):add_edge(r["id"],"from_patch_review",r["patch_review_id"])
  else:
   add_edge(r["id"],"created_revised_proposal",r["revised_proposal_id"]);add_edge(r["revised_proposal_id"],"revises",r["original_proposal_id"]);add_edge(r["id"],"has_status",r["status"])
 except Exception:w.append("Graph audit was unavailable.")
 try:record_mutation("manual_note","Proposal revision console opened" if event=="opened" else "Proposal revision created","Aether opened a safe proposal revision console for a proposal with requested changes." if event=="opened" else "Aether created a revised patch proposal using a caller-provided revised excerpt.",milestone="Milestone 33 — Proposal Revision Console / Change Request Handler",target_path=r.get("target_path") if event!="opened" else None,risk_level="low" if event=="opened" else "medium",status=r["status"],reversible=False,rollback_available=False)
 except Exception:w.append("Mutation Log integration was unavailable.")
 return w
def open_proposal_revision_console(source_type,source_id,metadata=None):
 t=now_iso();r={"id":f"proposal_revision_console_{uuid.uuid4().hex}","created":t,"updated":t,"timezone":get_timezone(),"status":"opened","source_type":source_type,"source_id":source_id,"proposal_review_console_id":None,"patch_review_id":None,"original_proposal_id":None,"revised_proposal_id":None,"self_modification_session_id":None,"review_decision":None,"original_proposal_status":None,"revised_proposal_status":None,"target_path":None,"revision_summary":None,"human_revision_note":None,"current_step":"revision_console_opened","next_recommended_step":"Provide a caller-authored revised proposed excerpt.","warnings":[],"metadata":_metadata(metadata)}
 proposal=None
 if source_type not in SOURCE_TYPES:r.update({"status":"blocked","current_step":"source_validation","next_recommended_step":"Use a supported revision console source type."});r["warnings"].append("Unsupported revision console source type.")
 elif source_type=="proposal_review_console":
  c=get_proposal_review_console_record(source_id)
  if not c:r["status"]="blocked";r["warnings"].append("Proposal review console record was not found.")
  else:r.update({"proposal_review_console_id":source_id,"patch_review_id":c.get("patch_review_id"),"original_proposal_id":c.get("proposal_id"),"self_modification_session_id":c.get("self_modification_session_id"),"review_decision":c.get("review_decision")});proposal=get_patch_proposal(r["original_proposal_id"])
 elif source_type=="patch_review":
  review=get_patch_review(source_id)
  if not review:r["status"]="blocked";r["warnings"].append("Patch review record was not found.")
  else:r.update({"patch_review_id":source_id,"original_proposal_id":review.get("proposal_id"),"review_decision":review.get("review_decision")});proposal=get_patch_proposal(r["original_proposal_id"])
 else:r["original_proposal_id"]=source_id;proposal=get_patch_proposal(source_id)
 if r["status"]=="opened" and not proposal:r["status"]="blocked";r["warnings"].append("Original patch proposal was not found.")
 if proposal:
  r["original_proposal_status"]=proposal.get("status");r["target_path"]=_target(proposal.get("target_path") or proposal.get("normalized_path"));r["revision_summary"]=_safe(proposal.get("proposed_change_summary"))
  if r.get("review_decision")!="request_changes" and proposal.get("status")!="changes_requested":r.update({"status":"blocked","current_step":"changes_requested_validation","next_recommended_step":"Only proposals with requested changes can be revised through this console."});r["warnings"].append("Proposal does not have requested changes.")
 r["warnings"]+=_audit(r,"opened");return _save(r)
def create_proposal_revision(revision_record_id,revised_proposed_excerpt,revised_change_summary=None,human_revision_note=None,create_approval_if_required=False,metadata=None):
 r=get_proposal_revision_console_record(revision_record_id)
 if not r:return {"id":revision_record_id,"status":"blocked","warnings":["Proposal revision console record was not found."]}
 if r.get("status")=="revision_created" and not (metadata or {}).get("force_revision"):r["status"]="blocked";r["warnings"].append("Revision has already been created for this console record.")
 elif r.get("status")!="opened":r["status"]="blocked";r["warnings"].append("Revision console record is not open.")
 elif not revised_proposed_excerpt:r["status"]="blocked";r["warnings"].append("A revised proposed excerpt is required.")
 else:
  old=get_patch_proposal(r.get("original_proposal_id"))
  if not old or not old.get("original_excerpt"):r["status"]="blocked";r["warnings"].append("Original proposal excerpt is unavailable for revision.")
  else:
   summary=revised_change_summary or old.get("proposed_change_summary") or "Revised patch proposal."
   proposal=create_patch_proposal(old.get("target_path"),old.get("request_text") or "Revise requested changes.",summary,revised_proposed_excerpt,f"Revision requested for proposal {old['id']}.",old.get("original_excerpt"),create_approval_if_required,{**_metadata(metadata),"source":"proposal_revision_console","revision_record_id":revision_record_id,"original_proposal_id":old["id"],"previous_patch_review_id":r.get("patch_review_id")})
   r.update({"revised_proposal_id":proposal.get("id"),"revised_proposal_status":proposal.get("status"),"status":"revision_created" if proposal.get("status") in {"draft","approval_required"} else "failed","revision_summary":_safe(summary),"human_revision_note":_safe(human_revision_note),"current_step":"revision_proposal_created","next_recommended_step":"Open the human proposal review console for the revised proposal."});r["warnings"] += [_safe(x,240) for x in proposal.get("warnings",[])]
 r["updated"]=now_iso()
 if r.get("revised_proposal_id"):r["warnings"]+=_audit(r,"created")
 return _save(r)
def get_proposal_revision_console_record(i):return next((r for r in load_proposal_revision_console_records()["records"] if r["id"]==i),None)
def list_proposal_revision_console_records(status=None,original_proposal_id=None,limit=50):return [r for r in load_proposal_revision_console_records()["records"] if (not status or r["status"]==status) and (not original_proposal_id or r.get("original_proposal_id")==original_proposal_id)][-max(0,limit):][::-1]
def proposal_revision_console_status():
 d=load_proposal_revision_console_records();return {"record_count":len(d["records"]),"created":d["created"],"updated":d["updated"],"timezone":d["timezone"],"policy":"Console requires requested changes and caller-provided text; it never applies patches."}
def summarize_proposal_revision_console(i):
 r=get_proposal_revision_console_record(i);return {k:r.get(k) for k in ("id","status","source_type","source_id","original_proposal_id","revised_proposal_id","patch_review_id","self_modification_session_id","review_decision","original_proposal_status","revised_proposal_status","target_path","revision_summary","current_step","next_recommended_step","warnings")} if r else None
