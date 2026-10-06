# Architecture and threat model

Client -> authenticated gateway -> model alias -> demo or Ollama.
Document ingestion -> SQLite chunks -> lexical retrieval -> untrusted model context.
Gateway -> JSON operational logs / Prometheus counters / stored evaluations.

ADR-001: standard library only makes the first lab reproducible without dependency
installation. Replace HTTPServer with an ASGI server behind TLS for production.
ADR-002: SQLite provides durable local state; one replica is a deliberate constraint.
ADR-003: lexical retrieval is deterministic and inspectable, but not semantic RAG.
ADR-004: no automatic fallback from real inference to mock output. Backend failure
returns 502 so the caller cannot mistake fabricated output for real inference.

Threats: stolen API key, malicious uploaded instructions, model-generated PII,
resource exhaustion and document contamination. Implemented mitigations reduce
some risk but regex guards can be bypassed, do not identify every language or
PII category, and may reject legitimate prompts. No confidential documents should
be uploaded to this demo. There is one shared administrative credential, no tenant
isolation, TLS or role separation. Keep the endpoint bound to localhost.

Production sequence:
1. ASGI gateway + OIDC/JWT + tenant roles and request/time/concurrency limits.
2. PostgreSQL/pgvector + real embeddings + tenant-scoped retrieval and migrations.
3. Redis rate limits and quotas; tokenizer-native usage and billing ledger.
4. Versioned prompts/models and actual groundedness/retrieval/regression datasets.
5. OpenTelemetry traces, histogram latency metrics and alert dashboards.
6. GPU inference pool, capacity tests, HPA, progressive rollout and rollback gate.
7. Signed images, admission policies, immutable digests and audited releases.

Do not autoscale this release: separate gateway state from replicas first.
