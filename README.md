# 🌾 Farmora

Farmora is a **smart assistant for farmers** that understands natural questions about farming, finds the most relevant data, and gives **clear, practical advice** while keeping expensive AI calls to a minimum.

Unlike typical AI chatbots that answer your query without surrounding context, Farmora uses all the tools in its arsenal to produce the best result possible.
It processes, filters, and enriches the question, and then calls an LLM only for the final, human-friendly answer.

---

## 🧠 What it Does

1. **Understands the farmer’s intent**  
   Detects if the question is about weather, soil health, crop choice, pest control, market prices, etc. using intent classification.

2. **Finds the right data**  
   Pulls from trusted sources:
   - Weather APIs
   - Soil and crop databases
   - Mandi Price Datset
   - Government Scheme Dataset
   - Your own previous queries

3. **Summarizes and cleans data**  
   Compresses the relevant info so the AI only sees **what matters** and saves cost by shaving tokens required per query.

4. **Normalizes language**  
   Translates domain jargon and supports multiple languages so the farmer gets the answer in their preferred format.

5. **Synthesizes a clear recommendation**  
   Uses an LLM to combine all relevant context into a concise, farmer-friendly answer.

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
