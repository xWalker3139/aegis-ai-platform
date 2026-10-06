# Build evidence before adding to CV

Suggested honest initial CV bullet:
Built a containerized AI gateway with authenticated inference routing, persistent
document retrieval, deterministic safety checks, Prometheus metrics and CI tests;
integrated optional local Ollama inference and authored Kubernetes deployment manifests.

Only say Kubernetes-deployed after actually deploying it. Only say real model
serving after running the local backend and recording results. Do not describe
this version as enterprise production-ready or senior experience.

Evidence checklist:
- Test output and CI run link.
- Demo recording: ingest -> retrieve -> inference -> sources.
- Unauthorized/PII/injection/rate-limit failure demonstrations.
- Backend outage and recovery timeline.
- Persistence test after container restart.
- Resource measurements and real-inference latency on your hardware.
- ADR documenting distributed-state migration before scaling.

For interview differentiation, implement the production milestones in architecture.md
one at a time and maintain real commits, measurements and postmortems.
