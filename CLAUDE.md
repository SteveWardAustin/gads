# Google Ads Search Term Analyzer

Steve Ward Media — internal tool for periodic search term maintenance on client accounts.

## Workflow

1. Download Search Terms report from Google Ads UI (Last 7 days recommended)
2. Upload CSV to Claude
3. Run the client's `analyze.py` — produces two output files:
   - `*_analysis.csv` — full analysis with RECOMMENDATION, NEG LEVEL, REASON columns
   - `*_upload.csv` — Google Ads Editor bulk import file (negatives only, deduped)
4. Review the analysis CSV, then import the upload CSV via Google Ads Editor

## Repository Structure

```
gads/
  clients/
    future_stars/
      analyze.py      # Future Stars analyzer
      rules.py        # Signal lists + rationale for all judgment calls
      fs_analysis.csv         # Latest analysis output
      fs_analysis_upload.csv  # Latest upload file
    tulu_travel/
      analyze.py      # Tulu Travel analyzer
      rules.py        # Signal lists + rationale for all judgment calls
      tulu_analysis.csv         # Latest analysis output
      tulu_analysis_upload.csv  # Latest upload file
```

## Running an Analysis

```bash
# Future Stars
cd clients/future_stars
python analyze.py path/to/search_terms.csv --out fs_analysis.csv

# Tulu Travel
cd clients/tulu_travel
python analyze.py path/to/search_terms.csv --out tulu_analysis.csv

# With keywords file (enables ad group theme matching)
python analyze.py search_terms.csv --keywords keywords.csv --out analysis.csv
```

## Input CSV Format

Google Ads Search Terms report exported from the UI. Has 2 header rows before the column row — the parser skips them automatically. Must include columns: `Search term`, `Campaign`, `Ad group`, `Match type`, `Added/Excluded`, `Clicks`, `Impr.`, `Cost`, `Conversions`.

## Output: RECOMMENDATION Values

| Value | Meaning |
|---|---|
| `ADD NEGATIVE` | Add as negative keyword at the level shown in NEG LEVEL |
| `REVIEW` | Ambiguous — human judgment needed before negating |
| `OK` | Appears relevant, leave it alone |
| `ALREADY EXCLUDED` | Already in the negative list, no action needed |

## Output: NEG LEVEL Values

| Value | Meaning |
|---|---|
| `CAMPAIGN` | Add as campaign-level negative |
| `AD GROUP` | Add as ad group-level negative (off-theme for that specific ad group) |
| `ACCOUNT` | Add as account-level negative (universally bad intent) — Future Stars only |

## Google Ads Editor Upload Format

The `_upload.csv` file uses these columns:
- `Campaign` — campaign name
- `Ad group` — ad group name (empty for campaign-level negatives)
- `Keyword` — the search term
- `Type` — `Campaign negative` or `Negative` (ad group level)
- `Keyword match type` — always `Exact`

## Converted Terms Protection

On each run, the analyzer does a first pass to find every search term with `Conversions > 0`. Those terms are protected from negation regardless of any rule — they return `OK / Has converted - protected from negation`. This is intentional: a term that has converted is proven, even if it superficially matches a negative signal.

## Clients

### Future Stars Summer Camps (fscamps.com)
Youth sports day camps on Long Island NY and Portland ME. Campaigns: Branded, Competitor, pMax Portland, Nonbranded (Geo Priorities + Other Geos). See `clients/future_stars/rules.py` for full rationale on all signal lists.

### Tulu Travel
Luxury Costa Rica travel packages for US buyers. One main lead-gen campaign + small brand campaign. Target: high-end, multi-day, guided packages. See `clients/tulu_travel/rules.py` for full rationale.

## Adding a New Client

1. `mkdir clients/new_client`
2. Copy `analyze.py` from the closest existing client as a starting point
3. Create `rules.py` with signal lists appropriate to the client's business
4. Update campaign routing logic in `analyze_term()` to match that account's campaign structure
5. Test on a real search terms export and tune rules based on results
