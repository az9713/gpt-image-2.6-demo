# Image 2.6 experiment

This completed feature tour contains 22 API outputs and used $1.163287 in usage-priced costs against a $4.00 experiment allocation. Open the root `index.html` for the illustrated guide or `image_26_experiment/index.html` for the raw comparison gallery.

## Comparisons

- 01 versus 02: Flare versus Sunburst, identical low-quality prompt and low complexity. One trial each; this cannot establish a general speed advantage.
- 02 through 06: Sunburst quality ladder, fixed prompt, size and complexity.
- 07 through 09: complexity ladder, fixed Sunburst model, high quality, exact infographic constraints.
- 03 → 10 → 11 → 12: successive consistency edits.
- 13 and 14: professional product ad and poster layouts.
- 15: render the locally drawn owl sketch; 16: six-pose sprite sheet using the rendered character.
- 17 versus 18: independent edits of source 03, identical prompt/model/quality/complexity. Only 18 includes a separate transparent PNG markup overlay. The original is not flattened with the markup. Inspect the annotated input preview as well as results.
- 19 versus 20: native SVG output from each model. Derived recolored SVGs and scale comparisons cost no additional API credits.
- 21 and 22: native API GIFs, six requested frames. Frame extraction is saved for inspection. Separately, output 16 is split and stitched locally to expose the explicit sprite-sheet workflow.

## Cost records

`ledger.jsonl` preserves each attempt, latency, returned token usage and usage-priced cost. `responses/` retains response metadata and usage; base64 bodies are decoded into files. `requests/` contains exact prompts and parameters plus source hashes. `comparison.csv` supports spreadsheet comparison. No Authorization headers or keys are logged.

Published Standard rates: $5/million text input tokens, $8/million image input tokens, $30/million image output tokens. SVG author usage is charged separately at its model's published rate. Costs computed from returned token usage are not an invoice. No cache discounts are assumed. `summary.json` identifies invoice reconciliation status and any unknown-cost requests.

Requests are sequential with no automatic retries. An uncertain timeout or missing usage stops the run. Conservative pre-request reserves stop new requests near the limit; these are not provider-enforced per-request price caps. The API has no documented dollar cap field. Outputs and cost records must be inspected between phases. Never rerun an uncertain request without reconciling its billing.

## Sources

- https://developers.openai.com/api/docs/guides/image-generation
- https://developers.openai.com/api/reference/resources/images/methods/generate
- https://developers.openai.com/api/reference/resources/images/methods/edit
- https://developers.openai.com/api/docs/pricing

## Reading the results

Use exact-count, label, color and connection checks for the infographic. For editing, inspect target correctness, logo legibility, geometry, reflections, background drift and unintended edits. Pixel equality is not expected of generative edits. Single-trial comparisons include sampling variation. GIF checks include returned frame count, timing, fixed-camera consistency, motion and loop seam. A correct file format does not establish visual quality.


## Public records

Account and request identifiers, exact activity timestamps, local machine paths and personal setup notes are omitted from this public copy. Generated artwork, prompts, settings, elapsed timings, usage counts, per-component costs and artifact hashes are retained. The account credit balance and raw saved launch page/transcript are not included.
