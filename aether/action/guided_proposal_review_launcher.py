"""Guarded launcher for opening human proposal review from a guided bridge."""
from pathlib import Path
import json, uuid, yaml
from aether.time.clock import get_timezone, now_iso

def load_aether_config(path="config/aether.yaml"):
    p=Path(path); return yaml.safe_load(p.read_text(encoding="utf-8")) or {} if p.exists() else {}
def get_guided_proposal_review_launcher_dir(): return Path(load_aether_config().get("paths",{}).get("private_dir","private"))/"proposal_review_launcher"
def get_guided_proposal_review_launcher_path(): return get_guided_proposal_review_launcher_dir()/"guided_proposal_review_launcher_records.json"
def load_guided_proposal_review_launcher_records():
    p=get_guided_proposal_review_launcher_path()
    try:d=json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    except json.JSONDecodeError:d={}
    t=now_iso(); d.setdefault("type","guided_proposal_review_launcher_records"); d.setdefault("version","0.1.0"); d.setdefault("created",t); d.setdefault("updated",d["created"]); d.setdefault("timezone",get_timezone()); d.setdefault("records",[]); return d
def save_guided_proposal_review_launcher_records(d):
    p=get_guided_proposal_review_launcher_path(); p.parent.mkdir(parents=True,exist_ok=True); d["updated"]=now_iso(); d["timezone"]=get_timezone(); p.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding="utf-8")
def sanitize_target_path(path):
    v=str(path or "").replace("\\","/"); prefix="C:/Aether/"; return v[len(prefix):] if v.lower().startswith(prefix.lower()) else (v if v and ":" not in v else None)
def shorten_id(value,keep=12): return f"{str(value)[:keep]}..." if value and len(str(value))>keep else value
def _save(r):
    d=load_guided_proposal_review_launcher_records(); d["records"]=[x for x in d["records"] if x.get("id")!=r["id"]]+[r]; save_guided_proposal_review_launcher_records(d); return r

def open_guided_proposal_review(bridge_launcher_record_id,metadata=None):
 from aether.action.guided_bridge_selection_launcher import get_guided_bridge_selection_launcher_record
 b=get_guided_bridge_selection_launcher_record(bridge_launcher_record_id); t=now_iso(); r={"id":f"guided_proposal_review_launcher_{uuid.uuid4().hex}","created":t,"updated":t,"timezone":get_timezone(),"status":"blocked","bridge_launcher_record_id":bridge_launcher_record_id,"plan_launcher_record_id":None,"repair_plan_id":None,"finding_id":None,"target_path":None,"bridge_selection_id":None,"review_bridge_id":None,"self_modification_session_id":None,"proposal_id":None,"proposal_review_console_id":None,"console_status":None,"next_recommended_step":"Launch guided bridge selection first.","warnings":[],"metadata":metadata or {}}
 if not b:return _save(r)
 for k in ("plan_launcher_record_id","repair_plan_id","finding_id","bridge_selection_id","review_bridge_id","self_modification_session_id","proposal_id"):r[k]=b.get(k)
 r["target_path"]=sanitize_target_path(b.get("target_path"))
 if b.get("status")!="launched":r["next_recommended_step"]="Guided bridge selection must be launched before proposal review."
 elif not r["proposal_id"]:r["next_recommended_step"]="A generated proposal is required before proposal review."
 else:
  try:
   from aether.action.proposal_review_console import open_proposal_review_console
   c=open_proposal_review_console("patch_proposal",r["proposal_id"],{"source":"guided_proposal_review_launcher","bridge_launcher_record_id":bridge_launcher_record_id});r["proposal_review_console_id"]=c.get("id");r["console_status"]=c.get("status")
   if c.get("status")=="opened":r["status"]="opened";r["next_recommended_step"]="Human must review the proposal and explicitly approve, reject, or request changes."
   else:r["warnings"].append("Proposal review console did not open.")
  except Exception as e:r["status"]="failed";r["warnings"].append(f"Proposal review console was unavailable: {type(e).__name__}.")
 return _save(r)
def get_guided_proposal_review_launcher_record(i):return next((r for r in load_guided_proposal_review_launcher_records()["records"] if r.get("id")==i),None)
def list_guided_proposal_review_launcher_records(status=None,bridge_launcher_record_id=None,proposal_id=None,target_path=None,limit=50):return [r for r in load_guided_proposal_review_launcher_records()["records"] if (not status or r.get("status")==status) and (not bridge_launcher_record_id or r.get("bridge_launcher_record_id")==bridge_launcher_record_id) and (not proposal_id or r.get("proposal_id")==proposal_id) and (not target_path or r.get("target_path")==sanitize_target_path(target_path))][-max(0,limit):][::-1]
def guided_proposal_review_launcher_status():return {"record_count":len(load_guided_proposal_review_launcher_records()["records"]),"policy":"Opens human proposal review only; never submits a decision."}
def summarize_guided_proposal_review_launcher(i):
 r=get_guided_proposal_review_launcher_record(i)
 if not r:return None
 keys=("id","status","bridge_launcher_record_id","repair_plan_id","finding_id","target_path","proposal_id","proposal_review_console_id","console_status","next_recommended_step","warnings");s={k:r.get(k) for k in keys}
 for k in ("id","bridge_launcher_record_id","repair_plan_id","proposal_id","proposal_review_console_id"):s[k]=shorten_id(s[k])
 s["target_path"]=sanitize_target_path(s["target_path"]);return s
