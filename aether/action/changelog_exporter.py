"""Sanitized public changelog exports from Aether's private mutation log."""
from pathlib import Path
import re,uuid
from aether.action.mutation_log import list_mutations,record_mutation
from aether.time.clock import now_iso
from aether.memory.timeline.recorder import record_event
from aether.memory.graph.store import add_edge
def _audit_changelog_export(result,export_type):
 warnings=[]
 try:
  from aether.core.runtime import runtime
  runtime.working_memory.add_event(role="aether",content=f"Changelog exported: {export_type}",event_type="changelog_exported",metadata={k:result.get(k) for k in ("output_path","milestone","mutation_count","public","status")}|{"export_type":export_type})
 except Exception as e:warnings.append(f"Working Memory audit was unavailable: {e}")
 try:
  importance="high" if result.get("public") else "normal";record_event("changelog_export",f"Changelog export: {export_type}",f"Aether exported a {export_type} changelog.",importance)
 except Exception as e:warnings.append(f"Timeline audit was unavailable: {e}")
 try:
  eid=result.get("id", "changelog_export");add_edge("Aether","exported_changelog",eid);add_edge(eid,"has_type",export_type);add_edge(eid,"has_status",result.get("status","unknown"))
  if result.get("milestone"):add_edge(eid,"documents_milestone",result["milestone"])
  if result.get("public") and sanitize_target_path(result.get("output_path")):add_edge(eid,"writes_file",sanitize_target_path(result["output_path"]))
 except Exception as e:warnings.append(f"Graph audit was unavailable: {e}")
 return warnings
def load_aether_config(path="config/aether.yaml"):
 import yaml;p=Path(path);return yaml.safe_load(p.read_text(encoding="utf-8")) or {} if p.exists() else {}
def get_private_export_dir():return Path(load_aether_config().get("paths",{}).get("private_dir","private"))/"changelog_exports"
def get_public_history_dir():return Path("docs/history")
def get_public_milestone_dir():return get_public_history_dir()/"milestones"
def sanitize_target_path(path):
 if not path:return None
 text=str(path).replace("\\","/");return text.split("C:/Aether/",1)[1] if text.startswith("C:/Aether/") else None
def shorten_id(value,keep=12):return value[:keep]+"..." if value and len(value)>keep else value
def sanitize_mutation_for_public(r):return {"id":shorten_id(r.get("id")),"date":r.get("created","")[:10],"mutation_type":r.get("mutation_type"),"milestone":r.get("milestone"),"title":r.get("title"),"summary":r.get("summary"),"target_path":sanitize_target_path(r.get("target_path")),"status":r.get("status"),"risk_level":r.get("risk_level"),"reversible":r.get("reversible"),"rollback_available":r.get("rollback_available"),"warnings_count":len(r.get("warnings",[]))}
def build_changelog_markdown(milestone=None,limit=200,public=True):
 items=[sanitize_mutation_for_public(x) for x in list_mutations(milestone=milestone,limit=limit)];lines=["# Aether Changelog","","This changelog is generated from Aether's private mutation log.","","Private runtime data, raw patches, approval details, backups, and file contents are intentionally excluded.","","## Summary","",f"- Generated: {now_iso()}",f"- Mutation count included: {len(items)}",f"- Milestone filter: {milestone or 'All'}","","## Changes",""]
 for x in items:lines += [f"### {x['date']} — {x['milestone'] or 'Unassigned'}","",f"- Type: {x['mutation_type']}",f"- Title: {x['title']}",f"- Summary: {x['summary']}"]+([f"- Target: {x['target_path']}"] if x['target_path'] else [])+[f"- Risk: {x['risk_level']}",f"- Status: {x['status']}",f"- Reversible: {'yes' if x['reversible'] else 'no'}",f"- Rollback available: {'yes' if x['rollback_available'] else 'no'}",""]
 return "\n".join(lines)
def export_public_changelog(output_path="docs/history/CHANGELOG.md",milestone=None,limit=200,metadata=None):
 p=Path(output_path);p.parent.mkdir(parents=True,exist_ok=True);text=build_changelog_markdown(milestone,limit);p.write_text(text,encoding="utf-8");record_mutation("manual_note","Human-readable changelog exported","Aether exported a sanitized human-readable changelog from private mutation history.",milestone="Milestone 25 — Human-Readable Changelog Export",target_path=str(p.resolve()),risk_level="medium",status="exported",reversible=True);r={"id":f"changelog_{uuid.uuid4().hex}","status":"success","output_path":str(p),"milestone":milestone,"mutation_count":len(list_mutations(milestone=milestone,limit=limit)),"public":True};r["audit_warnings"]=_audit_changelog_export(r,"public");return r
def export_milestone_report(milestone,output_dir="docs/history/milestones",metadata=None):
 slug=re.sub(r"[^a-z0-9]+","-",milestone.lower()).strip("-");return export_public_changelog(str(Path(output_dir)/f"{slug}.md"),milestone,200,metadata)
def export_private_changelog_report(milestone=None,limit=500,metadata=None):
 p=get_private_export_dir();p.mkdir(parents=True,exist_ok=True);out=p/f"changelog_{uuid.uuid4().hex}.md";out.write_text(build_changelog_markdown(milestone,limit),encoding="utf-8");r={"id":f"changelog_{uuid.uuid4().hex}","status":"success","output_path":str(out),"milestone":milestone,"mutation_count":len(list_mutations(milestone=milestone,limit=limit)),"public":False};r["audit_warnings"]=_audit_changelog_export(r,"private");return r
def changelog_export_status():return {"mutation_log_available":True,"public_history_dir":str(get_public_history_dir()),"private_export_dir":str(get_private_export_dir()),"policy":"Exports exclude private paths, backups, metadata, excerpts, and file contents."}
