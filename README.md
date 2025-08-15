# 🌾 Farmora

Farmora is a **smart assistant for farmers** that understands natural questions about farming, finds the most relevant data, and gives **clear, practical advice** while keeping expensive AI calls to a minimum.

Unlike typical AI chatbots that send your whole question to the cloud immediately, FarmerAI works **offline-first**.  
It processes, filters, and enriches the question locally, then calls an AI only for the final, human-friendly answer.

---

## 🧠 What it Does

1. **Understands the farmer’s intent**  
   Detects if the question is about weather, soil health, crop choice, pest control, market prices, etc. using a **local model** (no API cost).

2. **Finds the right data**  
   Pulls from trusted sources:
   - Weather APIs
   - Soil and crop databases
   - Historical farming advice
   - Your own previous queries

3. **Summarizes and cleans data**  
   Compresses the relevant info so the AI only sees **what matters** and saves compute by not processing 10 pages of raw data.

4. **Normalizes language**  
   Translates domain jargon and supports multiple languages so the farmer gets the answer in their preferred format.

5. **Synthesizes a clear recommendation**  
   Uses an LLM **once** to combine all relevant context into a concise, farmer-friendly answer.

6. **Learns from each query**  
   Stores useful context in a **vector database**, making future answers faster and more relevant.

---

## 💡 Example Query

**Farmer:**  
> "I’m in Tamil Nadu, what crops should I plant next week?"

**FarmerAI Pipeline:**
1. Classifies intent → *Crop Planning*
2. Fetches weather forecast for next week  
3. Looks up suitable crops for soil type in Tamil Nadu  
4. Checks recent rainfall data  
5. Sends only the most relevant facts to the LLM  
6. Returns:  
   > "Given next week’s temperature (28–32°C) and predicted light rainfall, you can plant short-duration crops like mung beans or okra. Avoid paddy this week due to low water availability."

---

## 🚀 Why It’s Different
- **Token-efficient**: Only one LLM call per query
- **Offline-first**: Local NLP handles most of the work
- **Context-aware**: Uses your past questions to improve answers
- **Farmer-focused**: Gives actionable, jargon-free advice

---

## 🛠 How It Works (Architecture)
```text
[Farmer Question]
   ↓
[Local Classifier] — detect topic & tools needed
   ↓
[Tool Calls] — weather APIs, soil DBs, historical data
   ↓
[Context Builder] — summarize, deduplicate, store in vector DB
   ↓
[Language Normalizer] — optional translation/jargon simplification
   ↓
[LLM] — final synthesis
   ↓
[Actionable Advice]
