# Insighta Labs - Intelligence Query Engine

A high-performance demographic query engine built with FastAPI, Python, and Supabase, hosted on Vercel.

## Public API Base URL
`https://your-vercel-deployment-url.vercel.app` *(Remember to update this!)*

## Endpoints

### 1. Advanced Filtering (`GET /api/profiles`)
Retrieves profiles matching specific conditions. Supports combinable filters, sorting, and pagination.

**Example:**
`/api/profiles?gender=male&country_id=NG&min_age=25&sort_by=age&order=desc&page=1&limit=10`

### 2. Natural Language Query (`GET /api/profiles/search`)
Translates plain English queries into structured demographic filters using rule-based parsing.

**Example:**
`/api/profiles/search?q=young males from nigeria`

---

## Natural Language Parsing Approach

Per the system requirements, **no AI or LLMs** were used. The natural language engine is strictly rule-based, utilizing Python's string matching and Regular Expressions (Regex) to ensure deterministic outputs and low latency.

### Keyword Mappings & Logic:
The parser evaluates the query string (converted to lowercase) sequentially:
1. **Gender:** Matches `"male" / "males"` -> `gender=male` and `"female" / "females"` -> `gender=female`.
2. **Age Groups (Stored):** Matches `"child"`, `"teenager"`, `"adult"`, `"senior"` and maps them to the `age_group` column.
3. **Age Aliases (Virtual):** The keyword `"young"` explicitly maps to `min_age=16` and `max_age=24`.
4. **Numeric Extractions:** Uses Regex `above (\d+)` to extract `min_age`, and `below|under (\d+)` to extract `max_age`.
5. **Country Mapping:** Uses Regex `from ([a-z\s]+)` to extract the country name, then cross-references an internal dictionary to map string names (e.g., "nigeria") to ISO codes (`country_id="NG"`).

---

## Limitations & Edge Cases

Because the parser is purely rule-based, it comes with specific limitations:
1. **Strict "AND" Logic Only:** The parser assumes all extracted criteria should be combined with `AND`. It does not support complex `OR` logic (e.g., "males from nigeria OR females from kenya").
2. **Spelling Sensitivity:** There is no fuzzy matching. Typographical errors in country names or keywords (e.g., "femaels", "negeria") will not trigger the rules and may result in an "Unable to interpret query" error.
3. **Single Country Constraint:** The parser's regex for locations extracts the first matched string after the word "from" and stops. It cannot interpret multiple locations (e.g., "from nigeria and angola").
4. **Hardcoded Country Dictionary:** The country mapping relies on a predefined internal dictionary. If a user queries a country that exists in the dataset but was not explicitly added to the dictionary map, it will be ignored.

## Setup & Local Development
1. Clone the repository.
2. Create a virtual environment: `python -m venv venv` and activate it.
3. Install dependencies: `pip install -r requirements.txt`
4. Add your `.env` file with `SUPABASE_URL` and `SUPABASE_KEY`.
5. Run locally: `uvicorn app.main:app --reload`
