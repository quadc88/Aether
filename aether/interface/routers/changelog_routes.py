"""Changelog router extracted in 82AP Build.

All 4 changelog routes moved from aether/interface/api_server.py.
route -> action -> response boundary preserved.
"""

from fastapi import APIRouter

from aether.interface.api_models import (
    ChangelogExportRequest,
    MilestoneReportExportRequest,
)

from aether.action.changelog_exporter import export_public_changelog,export_milestone_report,export_private_changelog_report,changelog_export_status


changelog_router = APIRouter()

@changelog_router.post("/action/changelog/export-public")
def export_public_changelog_action(request:ChangelogExportRequest):return export_public_changelog(request.output_path,request.milestone,request.limit,request.metadata)
@changelog_router.post("/action/changelog/export-milestone")
def export_milestone_changelog_action(request:MilestoneReportExportRequest):return export_milestone_report(request.milestone,request.output_dir,request.metadata)
@changelog_router.post("/action/changelog/export-private")
def export_private_changelog_action(request:ChangelogExportRequest):return export_private_changelog_report(request.milestone,request.limit,request.metadata)
@changelog_router.get("/action/changelog/status")
def get_changelog_status():return changelog_export_status()
