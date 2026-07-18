"""Private review records for patch proposals; never applies a patch."""
from pathlib import Path
import json, uuid, yaml
from aether.action.approval_queue import get_approval_item
from aether.action.patch_proposal import get_patch_proposal, mark_patch_proposal_status
from aether.action.tool_registry import get_tool, register_tool
from aether.memory.timeline.recorder import record_event
from aether.memory.graph.store import add_edge
from aether.time.clock import get_timezone, now_iso
from aether.action.mutation_log import record_patch_review_mutation

DECISIONS={"approve":"approved","reject":"rejected","request_changes":"changes_requested","supersede":"superseded","mark_draft":"draft"}
def load_aether_config(path="config/aether.yaml"):
 p=Path(path); return yaml.safe_load(p.read_text(encoding="utf-8")) or {} if p.exists() else {}
def get_patch_review_dir(): return Path(load_aether_config().get("paths",{}).get("private_dir","private"))/"patch_reviews"
def get_patch_review_path(): return get_patch_review_dir()/"patch_reviews.json"
def load_patch_reviews():
 p=get_patch_review_path()
 try: d=json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
 except json.JSONDecodeError: d={}
 t=now_iso(); d.setdefault("type","patch_reviews");d.setdefault("version","0.1.0");d.setdefault("created",t);d.setdefault("updated",d["created"]);d.setdefault("timezone",get_timezone());d.setdefault("reviews",[]);return d
def save_patch_reviews(d):
 p=get_patch_review_path();p.parent.mkdir(parents=True,exist_ok=True);d["updated"]=now_iso();d["timezone"]=get_timezone();p.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding="utf-8")
def review_patch_proposal(proposal_id, decision, review_reason="", reviewer="user", metadata=None):
 p=get_patch_proposal(proposal_id); warnings=[]; checks=[]; before=p.get("status") if p else None
 if not p: return {"status":"failed","proposal_id":proposal_id,"warnings":["Patch proposal not found."],"checks":[]}
 if decision not in DECISIONS: return {"status":"failed","proposal_id":proposal_id,"warnings":["Invalid review decision."],"checks":[]}
 diff=bool(p.get("diff_preview") or p.get("patch_text")); checks.append({"name":"has_diff","passed":diff,"details":"Diff preview checked."})
 approval=get_approval_item(p["approval_id"]) if p.get("approval_id") else None; approval_status=approval.get("status") if approval else None
 blocked=p.get("status") in {"rejected","blocked"} or not p.get("original_excerpt","") and p.get("status") in {"rejected","blocked"}
 status="success"; after=before
 if decision=="approve" and (not diff or blocked): status="blocked";warnings.append("Proposal is not safe to approve.")
 elif decision=="approve" and p.get("requires_user_approval") and approval_status!="approved": status="blocked";warnings.append("Approval queue item is not approved.")
 else: after=DECISIONS[decision]; mark_patch_proposal_status(proposal_id,after,review_reason)
 r={"id":f"patch_review_{uuid.uuid4().hex}","created":now_iso(),"updated":now_iso(),"timezone":get_timezone(),"status":status,"proposal_id":proposal_id,"proposal_status_before":before,"proposal_status_after":after,"review_decision":decision,"reviewer":reviewer,"review_reason":review_reason,"risk_level":p.get("risk_level"),"requires_user_approval":p.get("requires_user_approval"),"approval_id":p.get("approval_id"),"approval_status":approval_status,"target_path":p.get("target_path"),"diff_summary":{"has_diff":diff,"diff_length":len(p.get("diff_preview") or p.get("patch_text", ""))},"checks":checks,"warnings":warnings,"metadata":metadata or {}}
 d=load_patch_reviews();d["reviews"].append(r);save_patch_reviews(d);record_event("patch_review",f"Patch review: {decision}",f"Aether recorded patch review {r['id']} for proposal {proposal_id} with status {status}.","high" if r["risk_level"]=="high" or status!="success" else "normal")
 try:
  for s,rel,t in [("Aether","created_patch_review",r["id"]),(r["id"],"reviews_proposal",proposal_id),(r["id"],"has_decision",decision),(r["id"],"has_status",status)]:add_edge(s,rel,t)
  if after=="approved":add_edge(proposal_id,"review_status","approved")
 except Exception as e:r["warnings"].append(f"Graph Memory integration was unavailable: {e}")
 try: record_patch_review_mutation(r)
 except Exception as e:r["warnings"].append(f"Mutation Log integration was unavailable: {e}")
 return r
def list_patch_reviews(proposal_id=None,limit=50): return sorted([r for r in load_patch_reviews()["reviews"] if not proposal_id or r["proposal_id"]==proposal_id],key=lambda r:r["created"],reverse=True)[:max(0,limit)]
def get_patch_review(review_id): return next((r for r in load_patch_reviews()["reviews"] if r["id"]==review_id),None)
def patch_review_status():
 d=load_patch_reviews();return {"patch_review_path":str(get_patch_review_path()),"review_count":len(d["reviews"]),"created":d["created"],"updated":d["updated"],"timezone":d["timezone"]}
def seed_patch_review_tool():
 old=get_tool("file.patch_review");tool=register_tool("file.patch_review","File Patch Review","Review a patch proposal without applying it.","file","medium",True,True,False,False);return {"tool":tool,"created":old is None}
