"""Read-only, restricted code review reports for Aether project files."""
from pathlib import Path
import json,uuid,re,yaml
from aether.action.restricted_file_reader import read_restricted_file
from aether.time.clock import get_timezone,now_iso
from aether.memory.timeline.recorder import record_event
from aether.memory.graph.store import add_edge
from aether.action.mutation_log import record_mutation
SENSITIVE=("c:/aetherdata","backup_path","pre_rollback_backup_path","original_excerpt","proposed_excerpt","token","secret","password","api_key","private_key","id_rsa","id_ed25519",".env")
def load_aether_config(path="config/aether.yaml"):
 p=Path(path);return yaml.safe_load(p.read_text(encoding="utf-8")) or {} if p.exists() else {}
def get_code_review_dir():return Path(load_aether_config().get("paths",{}).get("private_dir","private"))/"code_reviews"
def get_code_review_path():return get_code_review_dir()/"code_review_reports.json"
def load_code_reviews():
 p=get_code_review_path()
 try:d=json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
 except json.JSONDecodeError:d={}
 t=now_iso();d.setdefault("type","code_review_reports");d.setdefault("version","0.1.0");d.setdefault("created",t);d.setdefault("updated",t);d.setdefault("timezone",get_timezone());d.setdefault("reports",[]);return d
def save_code_reviews(d):
 p=get_code_review_path();p.parent.mkdir(parents=True,exist_ok=True);d["updated"]=now_iso();p.write_text(json.dumps(d,indent=2),encoding="utf-8")
def is_sensitive_excerpt(t):return any(x in t.lower() for x in SENSITIVE)
def redact_sensitive_text(t):return "[redacted]" if is_sensitive_excerpt(t) else t
def safe_excerpt(t,max_chars=500):return redact_sensitive_text(t[:max_chars])
def _audit_code_review(r):
 warnings=[]
 try:
  from aether.core.runtime import runtime
  runtime.working_memory.add_event(role="aether",content=f"Code review created: {r['scope']}",event_type="code_review_created",metadata={"report_id":r["id"],"status":r["status"],"scope":r["scope"],"reviewed_file_count":len(r["reviewed_files"]),"finding_count":len(r["findings"]),"high_risk_count":r["risk_summary"]["high_risk_count"]})
 except Exception as e:warnings.append(f"Working Memory audit was unavailable: {e}")
 try:record_event("code_review",f"Code review completed: {r['scope']}",f"Aether completed restricted code review {r['id']}.","high" if r["risk_summary"]["high_risk_count"] else "normal")
 except Exception as e:warnings.append(f"Timeline audit was unavailable: {e}")
 try:
  add_edge("Aether","created_code_review",r["id"]);add_edge(r["id"],"has_status",r["status"]);add_edge(r["id"],"has_scope",r["scope"])
  for p in r["reviewed_files"]:add_edge(r["id"],"reviewed_file",p.replace("C:\\Aether\\",""))
 except Exception as e:warnings.append(f"Graph audit was unavailable: {e}")
 try:record_mutation("manual_note","Restricted code review completed","Aether completed a read-only restricted code review.",milestone="Milestone 26 — Restricted Code Review Assistant",risk_level="medium",status=r["status"])
 except Exception as e:warnings.append(f"Mutation Log integration was unavailable: {e}")
 return warnings
def create_code_review(scope,target_paths=None,max_files=20,max_chars_per_file=12000,include_tests=True,metadata=None):
 paths=target_paths or ["C:/Aether/aether/action/self_modification_cycle.py","C:/Aether/aether/action/changelog_exporter.py"];reviewed=[];blocked=[];findings=[]
 for path in paths[:max_files]:
  a=read_restricted_file(path,max_chars_per_file,{"source":"code_review"})
  if a["status"]!="success":blocked.append({"path":path,"reason":a["reason"]});continue
  reviewed.append(a["normalized_path"]);content=a["content"]
  for n,line in enumerate(content.splitlines(),1):
   if "TODO" in line or "FIXME" in line:findings.append({"id":f"finding_{uuid.uuid4().hex}","severity":"low","category":"code_quality","title":"Outstanding TODO/FIXME","description":"Review this deferred work.","target_path":a["normalized_path"],"line_hint":n,"evidence_excerpt":safe_excerpt(line,200),"recommendation":"Resolve or track explicitly.","suggested_action":"Consider a patch proposal."})
   if "except Exception" in line:findings.append({"id":f"finding_{uuid.uuid4().hex}","severity":"info","category":"error_handling","title":"Broad exception handling","description":"Confirm failure is surfaced safely.","target_path":a["normalized_path"],"line_hint":n,"evidence_excerpt":safe_excerpt(line,200),"recommendation":"Preserve warnings.","suggested_action":"Review error propagation."})
 status="completed" if reviewed and not blocked else "partial" if reviewed else "blocked";t=now_iso();r={"id":f"code_review_{uuid.uuid4().hex}","created":t,"updated":t,"timezone":get_timezone(),"status":status,"title":scope,"scope":scope,"target_paths":paths,"reviewed_files":reviewed,"blocked_files":blocked,"findings":findings,"summary":f"Reviewed {len(reviewed)} files with {len(findings)} findings.","risk_summary":{"high_risk_count":0,"finding_count":len(findings)},"recommendations":["Create a patch proposal only after human review."] if findings else [],"suggested_patch_needed":bool(findings),"suggested_patch_targets":reviewed if findings else [],"safety_notes":["Restricted reader only; no source writes."],"warnings":[],"metadata":metadata or {}};r["warnings"]+=_audit_code_review(r);d=load_code_reviews();d["reports"].append(r);save_code_reviews(d);return r
def get_code_review(i):return next((r for r in load_code_reviews()["reports"] if r["id"]==i),None)
def list_code_reviews(status=None,limit=50):return [r for r in load_code_reviews()["reports"] if not status or r["status"]==status][-limit:][::-1]
def code_review_status():return {"code_review_path":str(get_code_review_path()),"report_count":len(load_code_reviews()["reports"]),"policy":"Restricted-reader-only; private paths and sensitive excerpts are blocked."}
def summarize_code_review(i):
 r=get_code_review(i);return {"id":r["id"],"status":r["status"],"summary":r["summary"],"finding_count":len(r["findings"]),"blocked_file_count":len(r["blocked_files"])} if r else None
