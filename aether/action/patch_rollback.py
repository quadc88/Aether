"""Restricted restoration of a Milestone 21 patch backup."""
from pathlib import Path
import hashlib,json,uuid,yaml
from aether.action.patch_apply import get_patch_apply
from aether.action.restricted_file_reader import read_restricted_file
from aether.action.tool_registry import get_tool,register_tool
from aether.time.clock import get_timezone,now_iso
from aether.memory.timeline.recorder import record_event
from aether.memory.graph.store import add_edge
from aether.action.mutation_log import record_patch_rollback_mutation
GOV=("identity/identity_seed.md","docs/constitution.md","docs/architecture.md")
def load_aether_config(path="config/aether.yaml"):
 p=Path(path);return yaml.safe_load(p.read_text(encoding="utf-8")) or {} if p.exists() else {}
def _private():return Path(load_aether_config().get("paths",{}).get("private_dir","private"))
def get_patch_rollback_dir():return _private()/"patch_rollbacks"
def get_patch_rollback_path():return get_patch_rollback_dir()/"patch_rollbacks.json"
def get_patch_backup_dir():return _private()/"patch_backups"
def load_patch_rollbacks():
 p=get_patch_rollback_path()
 try:d=json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
 except json.JSONDecodeError:d={}
 t=now_iso();d.setdefault("type","patch_rollbacks");d.setdefault("version","0.1.0");d.setdefault("created",t);d.setdefault("updated",d["created"]);d.setdefault("timezone",get_timezone());d.setdefault("rollbacks",[]);return d
def save_patch_rollbacks(d):
 p=get_patch_rollback_path();p.parent.mkdir(parents=True,exist_ok=True);d["updated"]=now_iso();p.write_text(json.dumps(d,indent=2),encoding="utf-8")
def sha256_text(t):return hashlib.sha256(t.encode()).hexdigest()
def sha256_file(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def is_backup_path_allowed(path):
 p=Path(path).resolve(strict=False);root=get_patch_backup_dir().resolve(strict=False);return {"allowed":p.is_relative_to(root) and p.is_file() and p.stat().st_size<=65536,"path":str(p)}
def create_pre_rollback_backup(target_path,apply_id):
 p=Path(target_path);d=get_patch_backup_dir();d.mkdir(parents=True,exist_ok=True);out=d/f"pre_rollback_{apply_id}_{now_iso().replace(':','-')}_{p.name}";out.write_bytes(p.read_bytes());return {"backup_path":str(out)}
def rollback_patch_apply(apply_id,dry_run=True,metadata=None):
 a=get_patch_apply(apply_id);t=now_iso();r={"id":f"patch_rollback_{uuid.uuid4().hex}","created":t,"updated":t,"timezone":get_timezone(),"status":"failed","apply_id":apply_id,"proposal_id":a.get("proposal_id") if a else None,"target_path":a.get("target_path") if a else None,"normalized_path":a.get("normalized_path") if a else None,"backup_path":a.get("backup_path") if a else None,"pre_rollback_backup_path":None,"current_hash_before":None,"backup_hash":None,"hash_after":None,"dry_run":dry_run,"rolled_back":False,"changed":False,"checks":[],"warnings":[],"metadata":metadata or {}}
 def done():
  d=load_patch_rollbacks();d["rollbacks"].append(r);save_patch_rollbacks(d)
  record_event("patch_rollback",f"Patch rollback attempt: {r['status']}",f"Aether attempted to roll back patch apply {apply_id} with status {r['status']}.","high")
  try:
   for s,rel,target in [("Aether","attempted_patch_rollback",r["id"]),(r["id"],"rolls_back_apply",apply_id),(r["id"],"targets_file",r["normalized_path"] or "unknown"),(r["id"],"has_status",r["status"])]:add_edge(s,rel,target)
  except Exception as e:r["warnings"].append(f"Graph Memory integration was unavailable: {e}")
  if r["status"]=="success" and r["rolled_back"]:
   try: record_patch_rollback_mutation(r)
   except Exception as e:r["warnings"].append(f"Mutation Log integration was unavailable: {e}")
  return r
 if not a:r["warnings"].append("Patch apply record not found.");return done()
 if a.get("status")!="success" or not a.get("applied") or not a.get("backup_path"):r["status"]="blocked";r["warnings"].append("Patch apply record is not eligible for rollback.");return done()
 if any(a["normalized_path"].replace("\\","/").lower().endswith(x) for x in GOV):r["status"]="blocked";r["warnings"].append("Critical identity/governance files cannot be rolled back by Milestone 22.");return done()
 access=read_restricted_file(a["target_path"],65536,{"source":"patch_rollback"});check=is_backup_path_allowed(a["backup_path"])
 if access["status"]!="success" or not check["allowed"]:r["status"]="blocked";r["warnings"].append(access["reason"] if access["status"]!="success" else "Patch backup path is not allowed.");return done()
 current=access["content"];backup=Path(check["path"]).read_text(encoding="utf-8");r["current_hash_before"]=sha256_text(current);r["backup_hash"]=sha256_text(backup);r["hash_after"]=r["backup_hash"];r["changed"]=current!=backup;r["checks"].append({"name":"apply_record_eligible","passed":True,"details":"Patch apply record was successful and has backup."})
 if dry_run:r["status"]="dry_run";return done()
 try:r["pre_rollback_backup_path"]=create_pre_rollback_backup(access["normalized_path"],apply_id)["backup_path"];Path(access["normalized_path"]).write_text(backup,encoding="utf-8");r["hash_after"]=sha256_file(access["normalized_path"]);r["status"]="success";r["rolled_back"]=r["hash_after"]==r["backup_hash"]
 except OSError as e:r["status"]="failed";r["warnings"].append(str(e))
 return done()
def list_patch_rollbacks(apply_id=None,limit=50):return [r for r in load_patch_rollbacks()["rollbacks"] if not apply_id or r["apply_id"]==apply_id][:limit]
def get_patch_rollback(i):return next((r for r in load_patch_rollbacks()["rollbacks"] if r["id"]==i),None)
def patch_rollback_status():return {"patch_rollback_path":str(get_patch_rollback_path()),"rollback_count":len(load_patch_rollbacks()["rollbacks"])}
def seed_patch_rollback_tool():
 old=get_tool("file.patch_rollback");tool=register_tool("file.patch_rollback","Restricted Patch Rollback","Restore a verified patch backup.","file","high",True,True,True,False);return {"tool":tool,"created":old is None}
