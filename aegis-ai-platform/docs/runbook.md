# Operations lab

## Backend unavailable / 502
Check `docker compose logs gateway` and `docker compose logs ollama`.
Check BACKEND, Ollama network address and downloaded model with
`docker compose exec ollama ollama list`. Restore the backend and repeat a local
inference request. Do not bypass failures by silently returning mock output.

## 429
The shared process limit is 60 requests per rolling minute. Wait for the window
or adjust RATE_LIMIT_RPM deliberately. Restart resets the limiter (known weakness).

## 400
Inspect error code: model alias, body schema, PII policy or prompt policy.
Do not log sensitive request bodies while troubleshooting.

## Persistence experiment
Ingest a document, restart gateway and query it again. Named volume must persist.
Record command output and retrieval source in your evidence folder.

## Security experiment
Without credential expect 401. Submit `ignore previous instructions` and expect
400. Submit a synthetic email and expect 400. Try paraphrased attacks and document
limitations honestly; this is not a comprehensive injection defense.

## Release rollback
Tag and record image digests before deployment. On this single-replica lab use
`kubectl -n aegis rollout undo deployment/gateway`, then check health and inference.
This is a manual deployment rollback, not an automated quality-aware canary.
