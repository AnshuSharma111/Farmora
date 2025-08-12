# 🌾 Farmora

Farmora is a **token-efficient, offline-first AI architecture** built to process agricultural queries and provide **farmer-friendly recommendations**.  
The system minimizes expensive LLM calls by performing classification, data gathering, summarization, and rule-based checks **locally**, only using LLMs at the final synthesis stage.

---

## 🚀 Features
- **Offline-first processing** — local models for classification and summarization
- **Token-efficient architecture** — single LLM call per query
- **Tool integration** — weather APIs, soil data, crop databases
- **Vector database** — fast context retrieval for historical queries
- **Middleware hooks** — assertions, checks, and token budgeting
- **Language normalization** — domain jargon translation & multilingual support

---

## 🏗 Architecture
```text
[User Query]
   ↓
[Query Classifier] - local model
   ↓
[Tool Calls / Data Fetch] - APIs & offline DBs
   ↓
[Context Generator] - summarization, vector storage
   ↓
[Middleware Hooks] - data checks, token budgeting
   ↓
[Language Uniformer] - optional normalization/translation
   ↓
[LLM Call] - semantic synthesis & farmer advice
   ↓
[Final Response]
