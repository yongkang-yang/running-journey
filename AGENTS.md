# Agent instructions

## Plane work-item completion

Use the workspace and project UUID in `plane-projects.json`. PR references and completion are agent-owned. After the related PR has merged and acceptance is verified, explicitly mark the dedicated Plane work item Done; open, rejected, draft or unmerged closed PRs do not complete it. Persistent Trackers remain open across implementation PRs. Do not rely on automatic PR association or issue closing.
