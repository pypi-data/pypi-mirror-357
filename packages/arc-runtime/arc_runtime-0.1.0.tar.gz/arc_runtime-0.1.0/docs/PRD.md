# Arc Runtime PRD

## Product Vision
Arc Runtime is a lightweight Python interceptor that prevents AI agent failures in real-time by applying learned fixes before requests reach the LLM.

## Core Functionality

### 1. **Request Interception**
- Intercept all outgoing LLM API calls (OpenAI, Anthropic, etc.)
- Zero-config detection via monkey-patching or explicit wrapper
- Preserve original request format and headers

### 2. **Pattern Matching**
- Match requests against known failure patterns (<1ms)
- Use Bloom filters for O(1) lookup performance
- Support exact and fuzzy pattern matching

### 3. **Fix Application**
- Apply LoRA adapter or prompt modification
- Cache fixes locally for zero-latency remediation
- Fallback to original request if confidence < threshold

### 4. **Telemetry Streaming**
- Async stream all requests/responses to Arc Core via gRPC
- Include: original request, applied fix (if any), response, latency
- Non-blocking - never delay the request

### 5. **Model Management**
- Pull latest LoRA adapters from CDN
- Hot-reload models without restart
- Version management with rollback capability

## Technical Requirements

### Performance
- **Interception overhead**: <5ms (P99)
- **Pattern matching**: <1ms for 1M patterns
- **Memory footprint**: <100MB base, <500MB with models
- **CPU usage**: <5% during steady state

### Compatibility
- **Python versions**: 3.8+
- **LLM libraries**: OpenAI, Anthropic, LangChain, LlamaIndex
- **Frameworks**: Works with FastAPI, Flask, Django
- **Async support**: Both sync and async clients

### Security
- **No data persistence**: Everything in-memory
- **Encrypted telemetry**: TLS 1.3 for gRPC
- **No credential access**: Never touch API keys

## MVP Scope - Hello World (Week 1)

### In Scope
```python
from arc_runtime import Arc

# Initialize - this is it!
arc = Arc(endpoint="grpc://arc.company.com")

# Auto-intercepts all LLM calls in the process
response = openai.chat.completions.create(...)  # Automatically protected
```

### Features for MVP
1. OpenAI + Anthropic interception only
2. Exact pattern matching (dictionary lookup to start)
3. Prompt prefix/suffix modifications (no LoRA yet)
4. Basic telemetry streaming
5. Single hardcoded fix for demo
6. `ARC_DISABLE=1` env var for debugging
7. Basic `/metrics` endpoint (requests_intercepted, fixes_applied)
8. Golden-request unit tests (3-5 examples)
9. Thread-safety with `threading.local()`

### Out of Scope - Defer to V2
- LoRA adapter loading
- Multi-model routing
- Response streaming support
- Langchain/LlamaIndex integration
- Custom pattern definitions
- Circuit breaker
- Replay harness
- Hierarchical Bloom cascade
- WAL buffer
- Dynamic sampling
- Side-car mode

## Success Metrics

### Hello World Success Criteria
```python
# This works and logs to Arc Core:
import openai
from arc_runtime import Arc

Arc()  # Auto-patches

# This request gets intercepted, logged, and fixed
response = openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "..."}],
    temperature=0.95  # Gets fixed to 0.7
)
```

### Production Phase Metrics
- **66% failure reduction** (matching main Arc goal)
- **99.99% uptime** (no impact on availability)
- **<1% CPU overhead** at 1K QPS

## API Design

```python
# Minimal configuration
arc = Arc(
    endpoint="grpc://arc.company.com",
    api_key="arc_key_xxx",  # Optional
    cache_dir="~/.arc/cache",  # Optional
    log_level="INFO"  # Optional
)

# Manual pattern registration (optional)
arc.register_pattern(
    pattern={"model": "gpt-4", "temperature": {">": 0.9}},
    fix={"temperature": 0.7}
)

# Explicit wrapping (if auto-intercept fails)
protected_client = arc.wrap(openai.Client())
```

## Non-Goals
- **NOT** a full observability platform
- **NOT** modifying response content (only requests)
- **NOT** storing any customer data locally
- **NOT** requiring code changes (zero-config default)

## Dependencies
- `grpcio` - for telemetry streaming
- `pybloom_live` - for Bloom filters (V2)
- `wrapt` - for monkey-patching
- No ML frameworks (torch, tensorflow) in runtime

## Production Checklist (Required before v1.0)

**Note**: Create `PRODUCTION_CHECKLIST.md` in the repo and reference these items. They are NOT blocking hello world but required before v1.0 release.

### 1. Instrumentation & Health
- **Self-metrics endpoint** (`/arc/runtime/metrics` Prometheus scrape): latency histogram, cache hit %, Bloom-filter FPR, gRPC back-pressure
- **Circuit-breaker flag** – if pattern lookup > X ms or telemetry queue > N records, flip to *passthrough* mode and raise an alert; never strand prod traffic

### 2. Deterministic Safety Nets
- **Replay harness** – record-and-replay fixture so every PR runs the same intercepted calls against the same patterns; catches silent regressions in monkey-patch code
- **Golden-request unit tests** – YAML bundle of canonical failing requests ⇒ expected fixes; shipped with the library so users can verify their env

### 3. Concurrency & Isolation
- **Thread/async safety audit** – use `contextvars`/`asyncio.current_task()` to track call provenance; prevents cross-request pattern bleed in high-QPS async apps
- **Side-car option** – env var toggle to run interception over a local Unix-socket proxy instead of in-process patching (helps polyglot stacks)

### 4. Advanced Pattern Store (still < 1 ms)
- **Hierarchical Bloom cascade** – coarse hash → exact hash → optional trie; keeps O(1) but slashes false positives at 1 M+ patterns
- **Inline TTL** – each pattern stores an expiry so stale fixes age out without a registry push

### 5. Telemetry Robustness
- **Local write-ahead buffer** (SQLite WAL or memory-mapped file) when gRPC unavailable; flush on reconnect—guarantees trace completeness during network blips
- **Dynamic sampling knob** – default 100%, but drop to p = 0.1 when QPS spikes to avoid saturating collector in stress tests

### 6. Quick-win Dev-UX
- `ARC_DISABLE=1` env var – immediate off-switch for debugging ✅ (MVP)
- `doctor` CLI – prints current adapter version, patch status, last telemetry flush