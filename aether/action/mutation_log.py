"""Private structured history of Aether project mutations."""
from pathlib import Path
import json,uuid,yaml
from aether.time.clock import get_timezone,now_iso
from aether.memory.timeline.recorder import record_event
from aether.memory.graph.store import add_edge
def load_aether_config(path="config/aether.yaml"):
 p=Path(path);return yaml.safe_load(p.read_text(encoding="utf-8")) or {} if p.exists() else {}
def get_mutation_log_dir():return Path(load_aether_config().get("paths",{}).get("private_dir","private"))/"mutation_log"
def get_mutation_log_path():return get_mutation_log_dir()/"mutations.json"
def load_mutation_log():
 p=get_mutation_log_path()
 try:d=json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
 except json.JSONDecodeError:d={}
 t=now_iso();d.setdefault("type","project_mutation_log");d.setdefault("version","0.1.0");d.setdefault("created",t);d.setdefault("updated",d["created"]);d.setdefault("timezone",get_timezone());d.setdefault("mutations",[]);return d
def save_mutation_log(d):
 p=get_mutation_log_path();p.parent.mkdir(parents=True,exist_ok=True);d["updated"]=now_iso();p.write_text(json.dumps(d,indent=2),encoding="utf-8")
def record_mutation(mutation_type,title,summary,milestone=None,target_path=None,related_proposal_id=None,related_review_id=None,related_apply_id=None,related_rollback_id=None,related_approval_id=None,risk_level="medium",status="recorded",reversible=False,rollback_available=False,rollback_id=None,source="system",metadata=None,warnings=None):
 t=now_iso();m=locals().copy();m.pop('t');m.pop('warnings');m.update({"id":f"mutation_{uuid.uuid4().hex}","created":t,"updated":t,"timezone":get_timezone(),"warnings":warnings or {}});d=load_mutation_log();d["mutations"].append(m);save_mutation_log(d);record_event("project_mutation",f"Project mutation recorded: {mutation_type}",f"Aether recorded project mutation {m['id']}: {title}.","high" if risk_level=="high" or mutation_type in {"patch_applied","patch_rolled_back"} else "normal")
 try:
  for s,r,target in [("Aether","recorded_mutation",m['id']),(m['id'],"has_type",mutation_type),(m['id'],"has_status",status)]:add_edge(s,r,target)
  if target_path:add_edge(m['id'],"targets_file",target_path)
 except Exception as e:m["warnings"].append(str(e))
 return m
def list_mutations(mutation_type=None,milestone=None,target_path=None,limit=50):return [m for m in load_mutation_log()["mutations"] if (not mutation_type or m["mutation_type"]==mutation_type) and (not milestone or m["milestone"]==milestone) and (not target_path or m["target_path"]==target_path)][-limit:][::-1]
def get_mutation(i):return next((m for m in load_mutation_log()["mutations"] if m["id"]==i),None)
def mutation_log_status():d=load_mutation_log();return {"mutation_log_path":str(get_mutation_log_path()),"mutation_count":len(d["mutations"])}
def summarize_mutations(limit=100):
 items=list_mutations(limit=limit);return {"total_mutation_count":len(items),"counts_by_type":{t:sum(x["mutation_type"]==t for x in items) for t in {x["mutation_type"] for x in items}},"recent_mutations":items,"reversible_count":sum(x["reversible"] for x in items),"rollback_available_count":sum(x["rollback_available"] for x in items)}
def record_milestone_completed(milestone,summary,metadata=None):return record_mutation("milestone_completed",milestone,summary,milestone=milestone,source="system",metadata=metadata)
def record_patch_proposal_mutation(p):return record_mutation("patch_proposal_created","Patch proposal created",p.get("proposed_change_summary",""),target_path=p.get("target_path"),related_proposal_id=p.get("id"),risk_level=p.get("risk_level","medium"))
def record_patch_review_mutation(r):return record_mutation("patch_review_created","Patch review created",r.get("review_reason",""),target_path=r.get("target_path"),related_proposal_id=r.get("proposal_id"),related_review_id=r.get("id"),risk_level=r.get("risk_level","medium"))
def record_patch_apply_mutation(a):return record_mutation("patch_applied","Patch applied","Approved patch applied.",target_path=a.get("target_path"),related_proposal_id=a.get("proposal_id"),related_apply_id=a.get("id"),risk_level=a.get("risk_level","medium"),reversible=True,rollback_available=bool(a.get("backup_path")))
def record_patch_rollback_mutation(r):return record_mutation("patch_rolled_back","Patch rolled back","Patch backup restored.",target_path=r.get("target_path"),related_apply_id=r.get("apply_id"),related_rollback_id=r.get("id"),reversible=bool(r.get("pre_rollback_backup_path")),rollback_available=bool(r.get("pre_rollback_backup_path")))
