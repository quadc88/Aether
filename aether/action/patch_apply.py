"""Restricted, approval-gated excerpt replacement for approved patch proposals."""
from pathlib import Path
import hashlib,json,uuid,yaml
from aether.action.patch_proposal import get_patch_proposal
from aether.action.approval_queue import get_approval_item
from aether.action.restricted_file_reader import read_restricted_file
from aether.action.tool_registry import get_tool, register_tool
from aether.memory.timeline.recorder import record_event
from aether.memory.graph.store import add_edge
from aether.time.clock import get_timezone,now_iso

GOVERNANCE=("identity/identity_seed.md","docs/constitution.md","docs/architecture.md")
def load_aether_config(path="config/aether.yaml"):
 p=Path(path);return yaml.safe_load(p.read_text(encoding="utf-8")) or {} if p.exists() else {}
def _private():return Path(load_aether_config().get("paths",{}).get("private_dir","private"))
def get_patch_apply_dir():return _private()/"patch_applies"
def get_patch_apply_path():return get_patch_apply_dir()/"patch_applies.json"
def get_patch_backup_dir():return _private()/"patch_backups"
def load_patch_applies():
 p=get_patch_apply_path()
 try:d=json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
 except json.JSONDecodeError:d={}
 t=now_iso();d.setdefault("type","patch_applies");d.setdefault("version","0.1.0");d.setdefault("created",t);d.setdefault("updated",d["created"]);d.setdefault("timezone",get_timezone());d.setdefault("applies",[]);return d
def save_patch_applies(d):
 p=get_patch_apply_path();p.parent.mkdir(parents=True,exist_ok=True);d["updated"]=now_iso();d["timezone"]=get_timezone();p.write_text(json.dumps(d,indent=2),encoding="utf-8")
def sha256_text(text):return hashlib.sha256(text.encode("utf-8")).hexdigest()
def sha256_file(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def create_backup(path,proposal_id):
 p=Path(path);d=get_patch_backup_dir();d.mkdir(parents=True,exist_ok=True);out=d/f"{proposal_id}_{now_iso().replace(':','-')}_{p.name}";out.write_bytes(p.read_bytes());return {"backup_path":str(out),"created":now_iso()}
def apply_patch_proposal(proposal_id,dry_run=True,metadata=None):
 p=get_patch_proposal(proposal_id);t=now_iso();r={"id":f"patch_apply_{uuid.uuid4().hex}","created":t,"updated":t,"timezone":get_timezone(),"status":"failed","proposal_id":proposal_id,"target_path":p.get("target_path") if p else None,"normalized_path":p.get("normalized_path") if p else None,"proposal_status":p.get("status") if p else None,"risk_level":p.get("risk_level") if p else None,"approval_id":p.get("approval_id") if p else None,"approval_status":None,"original_hash_before":None,"original_hash_after":None,"backup_path":None,"dry_run":dry_run,"applied":False,"apply_method":"excerpt_replacement","changed":False,"checks":[],"warnings":[],"metadata":metadata or {}}
 def done():
  d=load_patch_applies();d["applies"].append(r);save_patch_applies(d)
  record_event("patch_apply",f"Patch apply attempt: {r['status']}",f"Aether attempted to apply patch proposal {proposal_id} with status {r['status']}.","high")
  try:
   for s,rel,target in [("Aether","attempted_patch_apply",r["id"]),(r["id"],"applies_proposal",proposal_id),(r["id"],"targets_file",r["normalized_path"] or "unknown"),(r["id"],"has_status",r["status"])]: add_edge(s,rel,target)
  except Exception as error:r["warnings"].append(f"Graph Memory integration was unavailable: {error}")
  return r
 if not p:r["warnings"].append("Patch proposal not found.");return done()
 if p["status"]!="approved":r["status"]="blocked";r["warnings"].append("Patch proposal is not approved.");return done()
 approval=get_approval_item(p["approval_id"]) if p.get("approval_id") else None;r["approval_status"]=approval.get("status") if approval else None
 if p.get("requires_user_approval") and r["approval_status"]!="approved":r["status"]="blocked";r["warnings"].append("Required approval queue item is not approved.");return done()
 if any(p["normalized_path"].replace("\\","/").lower().endswith(x) for x in GOVERNANCE):r["status"]="blocked";r["warnings"].append("Critical identity/governance files cannot be patched by Milestone 21.");return done()
 access=read_restricted_file(p["target_path"],65536,{"source":"patch_apply"})
 if access["status"]!="success":r["status"]="blocked";r["warnings"].append(access["reason"]);return done()
 old,new=p.get("original_excerpt",""),p.get("proposed_excerpt","");content=access["content"];count=content.count(old)
 if not old or not new or count!=1:r["status"]="blocked";r["warnings"].append("Original excerpt not found in current target file." if count==0 else "Original excerpt appears multiple times; apply is ambiguous.");return done()
 updated=content.replace(old,new,1);r["original_hash_before"]=sha256_text(content);r["original_hash_after"]=sha256_text(updated);r["changed"]=updated!=content;r["checks"].append({"name":"proposal_approved","passed":True,"details":"Patch proposal is approved."})
 if dry_run:r["status"]="dry_run";return done()
 try:r["backup_path"]=create_backup(access["normalized_path"],proposal_id)["backup_path"];Path(access["normalized_path"]).write_text(updated,encoding="utf-8");r["original_hash_after"]=sha256_file(access["normalized_path"]);r["status"]="success";r["applied"]=True
 except OSError as e:r["status"]="failed";r["warnings"].append(str(e))
 return done()
def list_patch_applies(proposal_id=None,limit=50):return sorted([x for x in load_patch_applies()["applies"] if not proposal_id or x["proposal_id"]==proposal_id],key=lambda x:x["created"],reverse=True)[:limit]
def get_patch_apply(apply_id):return next((x for x in load_patch_applies()["applies"] if x["id"]==apply_id),None)
def patch_apply_status():d=load_patch_applies();return {"patch_apply_path":str(get_patch_apply_path()),"apply_count":len(d["applies"])}
def seed_patch_apply_tool():
 old=get_tool("file.patch_apply");tool=register_tool("file.patch_apply","Restricted Patch Apply","Apply one approved excerpt replacement with backup.","file","high",True,True,True,False);return {"tool":tool,"created":old is None}
