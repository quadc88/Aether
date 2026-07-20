"""Connector from a revised proposal to the existing human review console."""
from pathlib import Path
import json,uuid,yaml
from aether.action.proposal_revision_console import get_proposal_revision_console_record
from aether.action.proposal_review_console import open_proposal_review_console,submit_proposal_review
from aether.action.patch_proposal import get_patch_proposal
from aether.action.mutation_log import record_mutation
from aether.memory.timeline.recorder import record_event
from aether.memory.graph.store import add_edge
from aether.time.clock import get_timezone,now_iso
SENSITIVE=("c:/aetherdata","backup_path","pre_rollback","original_excerpt","proposed_excerpt","token","secret","password","api_key","private_key","id_rsa","id_ed25519",".env")
def load_aether_config(path="config/aether.yaml"):
 p=Path(path);return yaml.safe_load(p.read_text(encoding="utf-8")) or {} if p.exists() else {}
def get_revised_proposal_review_loop_dir():return Path(load_aether_config().get("paths",{}).get("private_dir","private"))/"revised_proposal_review_loop"
def get_revised_proposal_review_loop_path():return get_revised_proposal_review_loop_dir()/"revised_proposal_review_loop_records.json"
def load_revised_proposal_review_loop_records():
 p=get_revised_proposal_review_loop_path()
 try:d=json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
 except json.JSONDecodeError:d={}
 t=now_iso();d.setdefault("type","revised_proposal_review_loop_records");d.setdefault("version","0.1.0");d.setdefault("created",t);d.setdefault("updated",d["created"]);d.setdefault("timezone",get_timezone());d.setdefault("records",[]);return d
def save_revised_proposal_review_loop_records(d):
 p=get_revised_proposal_review_loop_path();p.parent.mkdir(parents=True,exist_ok=True);d["updated"]=now_iso();d["timezone"]=get_timezone();p.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding="utf-8")
def _target(p):
 t=str(p or "").replace("\\","/");x="C:/Aether/";return t[len(x):] if t.lower().startswith(x.lower()) else None
def _safe(v,n=300):
 t=str(v or "")[:n];return "[redacted]" if any(x in t.lower().replace("\\","/") for x in SENSITIVE) else t
def _save(r):
 d=load_revised_proposal_review_loop_records()
 for i,x in enumerate(d["records"]):
  if x["id"]==r["id"]:d["records"][i]=r;break
 else:d["records"].append(r)
 save_revised_proposal_review_loop_records(d);return r
def _audit(r,event):
 w=[]
 try:
  from aether.core.runtime import runtime
  runtime.working_memory.add_event(role="aether",content=f"Revised proposal review {event}: {r['status']}",event_type="revised_proposal_review_opened" if event=="opened" else "revised_proposal_review_submitted",metadata={k:r.get(k) for k in ("id","proposal_revision_console_id","revised_proposal_id","proposal_review_console_id","patch_review_id","review_decision","status")}|{"record_id":r["id"]})
 except Exception:w.append("Working Memory audit was unavailable.")
 try:record_event("revised_proposal_review_loop" if event=="opened" else "revised_proposal_review",f"Revised proposal review opened: {r['status']}" if event=="opened" else f"Revised proposal review submitted: {r.get('review_decision')}",f"Aether opened human review for revised proposal {r.get('revised_proposal_id') or 'unknown'}." if event=="opened" else f"Human review was submitted for revised proposal {r.get('revised_proposal_id') or 'unknown'}.","high" if r.get("review_decision") in {"approve","reject"} else "normal")
 except Exception:w.append("Timeline audit was unavailable.")
 try:
  if event=="opened":
   for s,rel,t in [("Aether","opened_revised_proposal_review_loop",r["id"]),(r["id"],"from_revision_console",r["proposal_revision_console_id"]),(r["id"],"reviews_revised_proposal",r["revised_proposal_id"]),(r["id"],"opened_review_console",r.get("proposal_review_console_id") or "unknown"),(r["id"],"has_status",r["status"])]:add_edge(s,rel,t)
   if r.get("original_proposal_id"):add_edge(r["id"],"revision_of",r["original_proposal_id"])
   if r.get("self_modification_session_id"):add_edge(r["id"],"for_self_modification_session",r["self_modification_session_id"])
  else:
   if r.get("patch_review_id"):add_edge(r["id"],"created_patch_review",r["patch_review_id"])
   if r.get("review_decision"):add_edge(r["id"],"review_decision",r["review_decision"])
 except Exception:w.append("Graph audit was unavailable.")
 try:record_mutation("manual_note","Revised proposal review opened" if event=="opened" else "Revised proposal review submitted","Aether opened a human review console for a revised patch proposal." if event=="opened" else "A human submitted a review decision for a revised patch proposal.",milestone="Milestone 34 — Revised Proposal Review Loop",target_path=r.get("target_path") if event!="opened" else None,risk_level="low" if event=="opened" else "medium",status=r["status"],reversible=False,rollback_available=False)
 except Exception:w.append("Mutation Log integration was unavailable.")
 return w
def open_revised_proposal_review(proposal_revision_console_id,metadata=None):
 t=now_iso();r={"id":f"revised_proposal_review_loop_{uuid.uuid4().hex}","created":t,"updated":t,"timezone":get_timezone(),"status":"blocked","proposal_revision_console_id":proposal_revision_console_id,"original_proposal_id":None,"revised_proposal_id":None,"proposal_review_console_id":None,"patch_review_id":None,"self_modification_session_id":None,"revised_proposal_status":None,"review_decision":None,"review_comment":None,"target_path":None,"current_step":"revision_validation","next_recommended_step":"Inspect the revision console record.","warnings":[],"metadata":metadata or {}}
 rev=get_proposal_revision_console_record(proposal_revision_console_id)
 if not rev:r["warnings"].append("Proposal revision console record was not found.")
 elif not rev.get("revised_proposal_id"):r["warnings"].append("Revision record has no revised proposal.")
 else:
  p=get_patch_proposal(rev["revised_proposal_id"]);r.update({"original_proposal_id":rev.get("original_proposal_id"),"revised_proposal_id":rev.get("revised_proposal_id"),"self_modification_session_id":rev.get("self_modification_session_id"),"revised_proposal_status":p.get("status") if p else None,"target_path":_target((p or {}).get("target_path") or (p or {}).get("normalized_path"))})
  if not p:r["warnings"].append("Revised patch proposal was not found.")
  else:
   c=open_proposal_review_console("patch_proposal",p["id"],{"source":"revised_proposal_review_loop","review_loop_record_id":r["id"],"proposal_revision_console_id":proposal_revision_console_id});r["proposal_review_console_id"]=c.get("id");r["status"]="opened" if c.get("status")=="opened" else "blocked";r["current_step"]="review_console_opened";r["next_recommended_step"]="Human should submit an explicit review decision for the revised proposal.";r["warnings"] += [_safe(x,240) for x in c.get("warnings",[])]
 r["warnings"]+=_audit(r,"opened");return _save(r)
def submit_revised_proposal_review(review_loop_record_id,decision,comment=None,reviewer="human",create_approval_if_required=False,metadata=None):
 r=get_revised_proposal_review_loop_record(review_loop_record_id)
 if not r:return {"id":review_loop_record_id,"status":"blocked","warnings":["Revised proposal review loop record was not found."]}
 if r.get("status")=="reviewed" and not (metadata or {}).get("force_review"):r["status"]="blocked";r["warnings"].append("Revised proposal has already been reviewed.")
 elif not r.get("proposal_review_console_id"):r["status"]="blocked";r["warnings"].append("Review loop has no proposal review console.")
 else:
  x=submit_proposal_review(r["proposal_review_console_id"],decision,comment,reviewer,create_approval_if_required,{**(metadata or {}),"source":"revised_proposal_review_loop","review_loop_record_id":review_loop_record_id});r.update({"patch_review_id":x.get("patch_review_id"),"review_decision":decision,"review_comment":_safe(comment),"revised_proposal_status":x.get("proposal_status") or r.get("revised_proposal_status"),"status":"reviewed" if x.get("status")=="reviewed" else "blocked","current_step":"human_review_completed"});r["warnings"] += [_safe(q,240) for q in x.get("warnings",[])]
  r["next_recommended_step"]={"approve":"Run a dry-run apply before any real apply.","request_changes":"Open proposal revision console again for another revision.","reject":"Stop this revised proposal or create a new revision if appropriate."}.get(decision,"Inspect proposal status before continuing.")
 r["updated"]=now_iso();r["warnings"]+=_audit(r,"submitted");return _save(r)
def get_revised_proposal_review_loop_record(i):return next((r for r in load_revised_proposal_review_loop_records()["records"] if r["id"]==i),None)
def list_revised_proposal_review_loop_records(status=None,revised_proposal_id=None,limit=50):return [r for r in load_revised_proposal_review_loop_records()["records"] if (not status or r["status"]==status) and (not revised_proposal_id or r.get("revised_proposal_id")==revised_proposal_id)][-limit:][::-1]
def revised_proposal_review_loop_status():
 d=load_revised_proposal_review_loop_records();return {"record_count":len(d["records"]),"created":d["created"],"updated":d["updated"],"timezone":d["timezone"],"policy":"Loop opens existing review consoles and never applies patches."}
def summarize_revised_proposal_review_loop(i):
 r=get_revised_proposal_review_loop_record(i);return {k:r.get(k) for k in ("id","status","proposal_revision_console_id","original_proposal_id","revised_proposal_id","proposal_review_console_id","patch_review_id","self_modification_session_id","revised_proposal_status","review_decision","target_path","current_step","next_recommended_step","warnings")} if r else None
