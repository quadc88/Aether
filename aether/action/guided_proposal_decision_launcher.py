"""Guarded human proposal-decision launcher; never advances to dry run."""
from pathlib import Path
import json, uuid, yaml
from aether.time.clock import get_timezone, now_iso

def load_aether_config(path="config/aether.yaml"):
 p=Path(path);return yaml.safe_load(p.read_text(encoding="utf-8")) or {} if p.exists() else {}
def get_guided_proposal_decision_launcher_dir():return Path(load_aether_config().get("paths",{}).get("private_dir","private"))/"proposal_decision_launcher"
def get_guided_proposal_decision_launcher_path():return get_guided_proposal_decision_launcher_dir()/"guided_proposal_decision_launcher_records.json"
def load_guided_proposal_decision_launcher_records():
 p=get_guided_proposal_decision_launcher_path()
 try:d=json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
 except json.JSONDecodeError:d={}
 t=now_iso();d.setdefault("type","guided_proposal_decision_launcher_records");d.setdefault("version","0.1.0");d.setdefault("created",t);d.setdefault("updated",d["created"]);d.setdefault("timezone",get_timezone());d.setdefault("records",[]);return d
def save_guided_proposal_decision_launcher_records(d):
 p=get_guided_proposal_decision_launcher_path();p.parent.mkdir(parents=True,exist_ok=True);d["updated"]=now_iso();d["timezone"]=get_timezone();p.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding="utf-8")
def sanitize_target_path(path):
 v=str(path or "").replace("\\","/");x="C:/Aether/";return v[len(x):] if v.lower().startswith(x.lower()) else (v if v and ":" not in v else None)
def shorten_id(v,keep=12):return f"{str(v)[:keep]}..." if v and len(str(v))>keep else v
def _save(r):
 d=load_guided_proposal_decision_launcher_records();d["records"]=[x for x in d["records"] if x.get("id")!=r["id"]]+[r];save_guided_proposal_decision_launcher_records(d);return r

def submit_guided_proposal_decision(proposal_review_launcher_record_id,decision,reviewer="human",comment=None,metadata=None):
 from aether.action.guided_proposal_review_launcher import get_guided_proposal_review_launcher_record
 p=get_guided_proposal_review_launcher_record(proposal_review_launcher_record_id);t=now_iso();r={"id":f"guided_proposal_decision_launcher_{uuid.uuid4().hex}","created":t,"updated":t,"timezone":get_timezone(),"status":"blocked","proposal_review_launcher_record_id":proposal_review_launcher_record_id,"proposal_review_console_id":None,"bridge_launcher_record_id":None,"proposal_id":None,"target_path":None,"decision":decision,"reviewer":reviewer or "human","comment_supplied":bool(comment),"patch_review_id":None,"patch_review_decision":None,"proposal_status_after_decision":None,"next_recommended_step":"Open guided proposal review first.","warnings":[],"metadata":metadata or {}}
 if not p:return _save(r)
 for k in ("proposal_review_console_id","bridge_launcher_record_id","proposal_id"):r[k]=p.get(k)
 r["target_path"]=sanitize_target_path(p.get("target_path"))
 if p.get("status")!="opened":r["next_recommended_step"]="Guided proposal review must be opened before submitting a decision."
 elif not r["proposal_review_console_id"]:r["next_recommended_step"]="Proposal review console is required before submitting a decision."
 elif decision not in {"approve","request_changes","reject"}:r["next_recommended_step"]="Submit one explicit human decision: approve, request_changes, or reject."
 else:
  try:
   from aether.action.proposal_review_console import submit_proposal_review
   result=submit_proposal_review(r["proposal_review_console_id"],decision,comment,r["reviewer"],False,{"source":"guided_proposal_decision_launcher","proposal_review_launcher_record_id":proposal_review_launcher_record_id})
   r["patch_review_id"]=result.get("patch_review_id");r["patch_review_decision"]=result.get("review_decision");r["proposal_status_after_decision"]=result.get("proposal_status");
   if result.get("status")=="reviewed":
    r["status"]="decided";r["next_recommended_step"]={"approve":"Open approved dry-run gate in a future step.","request_changes":"Open proposal revision flow in a future step.","reject":"Stop this repair branch or open a new guided intake."}[decision]
   else:r["warnings"].append("Proposal review console did not accept the decision.")
  except Exception as e:r["status"]="failed";r["warnings"].append(f"Proposal review console was unavailable: {type(e).__name__}.")
 return _save(r)
def get_guided_proposal_decision_launcher_record(i):return next((r for r in load_guided_proposal_decision_launcher_records()["records"] if r.get("id")==i),None)
def list_guided_proposal_decision_launcher_records(status=None,proposal_review_launcher_record_id=None,proposal_id=None,decision=None,target_path=None,limit=50):return [r for r in load_guided_proposal_decision_launcher_records()["records"] if (not status or r.get("status")==status) and (not proposal_review_launcher_record_id or r.get("proposal_review_launcher_record_id")==proposal_review_launcher_record_id) and (not proposal_id or r.get("proposal_id")==proposal_id) and (not decision or r.get("decision")==decision) and (not target_path or r.get("target_path")==sanitize_target_path(target_path))][-max(0,limit):][::-1]
def guided_proposal_decision_launcher_status():return {"record_count":len(load_guided_proposal_decision_launcher_records()["records"]),"policy":"Submits an explicit human decision and stops before dry run."}
def summarize_guided_proposal_decision_launcher(i):
 r=get_guided_proposal_decision_launcher_record(i)
 if not r:return None
 keys=("id","status","proposal_review_launcher_record_id","proposal_review_console_id","proposal_id","target_path","decision","reviewer","comment_supplied","patch_review_id","patch_review_decision","proposal_status_after_decision","next_recommended_step","warnings");s={k:r.get(k) for k in keys}
 for k in ("id","proposal_review_launcher_record_id","proposal_review_console_id","proposal_id","patch_review_id"):s[k]=shorten_id(s[k])
 s["target_path"]=sanitize_target_path(s["target_path"]);return s
