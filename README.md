# FitFindr

FitFindr is an AI agent that helps you find secondhand fashion listings and seamlessly pairs them with your existing wardrobe to generate outfit ideas and social media "fit cards."

## Setup

**macOS / Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows:**
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Set your Groq API key in a `.env` file (get a free key at [console.groq.com](https://console.groq.com)):
```
GROQ_API_KEY=your_key_here
```

To run the Gradio interface:
```bash
python app.py
```

## Tool Inventory

- **`search_listings`**
  - **Inputs:** `description: str`, `size: str | None = None`, `max_price: float | None = None`
  - **Outputs:** `list[dict]`
  - **Purpose:** Searches the mock `listings.json` file, filters by size and price, and scores relevance by matching keywords from the description to listing title, description, and style tags.
- **`suggest_outfit`**
  - **Inputs:** `new_item: dict`, `wardrobe: dict`
  - **Outputs:** `str`
  - **Purpose:** Uses a Groq LLM to suggest 1-2 specific outfit combinations by pairing the newly selected item with existing pieces in the user's wardrobe.
- **`create_fit_card`**
  - **Inputs:** `outfit: str`, `new_item: dict`
  - **Outputs:** `str`
  - **Purpose:** Uses a Groq LLM to generate a casual, 2-4 sentence social media caption for the outfit, mentioning the item's name, price, and platform exactly once.

## Planning Loop Explanation

The planning loop is a sequential pipeline implemented in `run_agent()`. When a user query arrives, the agent first uses an LLM to parse the query into structured JSON (`description`, `size`, and `max_price`). It passes these parameters into `search_listings`. If no results are found, the loop immediately halts and returns an error without proceeding. If results are found, it extracts the top item and passes it alongside the user's wardrobe into `suggest_outfit`. The resulting styling advice is then passed to `create_fit_card` to generate the final social media caption.

## State Management Approach

State is managed sequentially through a single Python dictionary called `session`. Initialized via `_new_session()`, this dictionary collects the outputs of each step. The search results go into `session["search_results"]`, the top pick is saved to `session["selected_item"]`, the styling advice to `session["outfit_suggestion"]`, and the final caption to `session["fit_card"]`. The pipeline accesses data purely by pulling it from this dict (e.g., `create_fit_card` reads `session["outfit_suggestion"]`), avoiding implicit global variables.

## Interaction Walkthrough

**User query:** "looking for a vintage graphic tee under $30"

**Step 1 — Parse Query:**
- **Tool:** LLM JSON Parser (in-line in `agent.py`)
- **Input:** User query string
- **Why this tool:** To extract structured filtering parameters.
- **Output:** `{"description": "vintage graphic tee", "size": null, "max_price": 30.0}`

**Step 2 — Search Listings:**
- **Tool:** `search_listings`
- **Input:** `description="vintage graphic tee"`, `size=None`, `max_price=30.0`
- **Why this tool:** To find a matching thrift item from the dataset.
- **Output:** Returns a list of matching dictionaries. The top item (Y2K Baby Tee — Butterfly Print) is saved to the session.

**Step 3 — Suggest Outfit:**
- **Tool:** `suggest_outfit`
- **Input:** The Y2K Baby Tee dictionary, and the user's wardrobe dictionary.
- **Why this tool:** To generate outfit ideas pairing the new tee with the user's existing clothes.
- **Output:** "First, let's go for a casual vibe - pair your new tee with those baggy straight-leg jeans..."

**Step 4 — Create Fit Card:**
- **Tool:** `create_fit_card`
- **Input:** The outfit suggestion string, and the Y2K Baby Tee dictionary.
- **Why this tool:** To convert the outfit idea into an engaging social media caption.
- **Output:** "I'm obsessed with my new Y2K Baby Tee - Butterfly Print, scored for just $18.0 on depop. I've been styling it with baggy jeans..."

## Error Handling and Fail Points

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| `search_listings` | No listings match parameters (e.g., "designer ballgown size XXS under $5") | Tool returns an empty list `[]`. The `agent.py` planning loop detects this, halts immediately without calling further tools, and sets the error key to a helpful message. |
| `suggest_outfit` | Wardrobe is empty (`wardrobe["items"] == []`) | Tool detects empty items and automatically modifies the LLM prompt to offer *general* styling advice instead of pairing logic. |
| `create_fit_card` | Outfit string is empty or missing | Tool safely returns a hardcoded string `"Error: Cannot generate fit card because outfit data is missing."` rather than confusing the LLM or crashing. |

## Spec Reflection

**One way planning.md helped during implementation:**
Drafting `planning.md` made writing the code incredibly straightforward because every tool's exact inputs, outputs, and failure behaviors were already mapped out. It removed the guesswork from state management since I already knew what keys the `session` dictionary needed to hold.

**One divergence from your spec, and why:**
During the `agent.py` implementation, I realized that simple string parsing wouldn't accurately extract `description`, `size`, and `max_price` from free-form text. I diverged from a pure script-based approach by adding an initial LLM call with `response_format={"type": "json_object"}` to robustly extract those parameters dynamically.

## AI Usage

1. **Generating Tool Implementations**: I provided the AI with the exact Tool Spec sections from `planning.md` (detailing inputs, outputs, and failure modes). The AI produced the Python functions for `search_listings`, `suggest_outfit`, and `create_fit_card`. I explicitly enforced that the `search_listings` function ensure uniform lowercasing across all strings before keyword matching to avoid case-sensitivity bugs.
2. **Generating the Test Suite**: I provided the AI with the Tool Specs and asked for a Pytest suite that explicitly tested the happy path and failure mode of each tool. The AI generated `tests/test_tools.py`. I ensured the `search_listings` assertions correctly evaluated the threshold and price filters to verify the data loading step.
