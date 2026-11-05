# Night Lab: Image 2.6 results

Experiment completed on November 4, 2026. Public records omit account identifiers and exact activity timestamps.

**22 successful API outputs: 18 PNG stills, 2 native SVGs, 2 native GIFs. Usage-priced total: $1.163287. Authorized limit: $4.00. Unused allowance: $2.836713.**

There were 23 requests: 22 successes and one HTTP 400 parameter-validation rejection for missing `svg.model`. The rejection returned no usage and is recorded at $0. The corrected request and initial rejection are both retained. There were no automatic retries, no unknown-cost requests and no additional paid generations after the 22 requested outputs.

Costs are calculated from actual returned token usage at the saved official Standard rates, including separate SVG author usage. This is not a billing-invoice reconciliation; no claim is made about the account's current credit balance or unrelated account activity.

## Cost by experiment

| Experiment | Outputs | Usage-priced cost (USD) |
|---|---:|---:|
| Flare/Sunburst low-quality comparison | 2 | 0.050990 |
| Other four quality levels | 4 | 0.403630 |
| Three complexity levels | 3 | 0.160620 |
| Successive consistency edits | 3 | 0.155726 |
| Professional product ad and poster | 2 | 0.106140 |
| Sketch rendering and sprite sheet | 2 | 0.094809 |
| Prompt-only versus markup edit | 2 | 0.104589 |
| Native SVG generation | 2 | 0.052633 |
| Native GIF generation | 2 | 0.034150 |
| **Total** | **22** | **1.163287** |

## Speed and quality

With identical prompt, low quality, low complexity and 1024×1024 size, Flare took 7.376 seconds and Sunburst took 11.734 seconds. Both cost $0.025495. These are end-to-end HTTP timings including network overhead. One trial does not establish a general speed ratio or verify the launch claim against previous-generation models; no previous-generation model was benchmarked.

The Sunburst quality ladder used the same prompt and low complexity throughout:

| Quality | Seconds | USD |
|---|---:|---:|
| Low | 11.734 | 0.025495 |
| Medium | 16.952 | 0.044245 |
| High | 40.085 | 0.053455 |
| Extra high | 50.840 | 0.094435 |
| Max | 105.213 | 0.211495 |

Each generation also varies in layout, logo design and character details. For example, the high-quality sample adds laboratory glassware that was not explicitly requested. More spending does not isolate rendering quality from sampling variation or guarantee better instruction following. The original PNGs, rather than compressed contact sheets, are the proper files for examining fine detail.

## Complexity control

All three infographic samples have the requested six boxes in two rows, exact labels, assigned color sequence and five connections on visual inspection. The TEST→RECORD connector travels outside the boxes. All three cost $0.053540 at fixed high quality. Latencies were 33.921 seconds (low), 32.353 (medium), 42.252 (high).

This particular task did not reveal a clear structural advantage for high complexity. Typography, icon choices, spacing and rounding vary. Higher complexity did not make latency monotonically increase across these single trials. Six-box correctness is a useful check, not a comprehensive evaluation of dense infographic reasoning.

## Markup-guided editing

Open `derived/markup-comparison.html` for the original, annotated preview, two edited results and a comparison slider.

- Source for both independent edits: output 03, verified by identical SHA-256 in the saved requests.
- Both requests: Flare, medium quality, low complexity, same exact text and dimensions.
- Output 17: text-only control, 20.917 seconds, $0.051992.
- Output 18: same request plus `markup`, 11.992 seconds, $0.052597.
- The overlay is a separate 1024×1024 RGBA PNG with transparent pixels. Only the red ellipse is opaque. The flattened annotated preview was not submitted as the source image.

Both edits change the intended left mug to blue, preserve the main scene layout and leave the right mug ivory. No red annotation appears in output 18. Both also change the left mug logo from teal to cream, despite the instruction to preserve it. Shape and reflection details vary slightly. The overlay result is a somewhat deeper blue.

The markup request reports 121 more text input tokens and the same image-input/output token counts as the control, accounting for the $0.000605 difference in this pair. This is an observation of these responses, not a general markup cost formula.

**Conclusion:** the markup API path works. This easy left-mug task does not demonstrate a precision improvement over an already explicit text instruction, and the pair does not establish a latency benefit. A stronger follow-up would use a genuinely ambiguous small target and repeated trials; no such additional requests were made.

## Consistency and professional layouts

The three successive edits preserve the recognizable owl, mugs, desk and composition while changing mug color, lighting and background. The first recoloring changes the logo color. The lighting edit makes the brass lamp appear silver, which should be inspected as possible material drift. The final edit introduces an observatory window while retaining the foreground arrangement. Identity retention is strong visually but not exact pixel preservation.

The product ad and poster render the requested copy legibly. They are separately prompted examples; their owl emblems are not guaranteed to match the original scene's exact logo. The professional-layout test is separate from the sequential identity test.

## SVG: API generation, scaling and local editing

Outputs 19 and 20 are native API SVGs. Both use the same explicit SVG author, `gpt-6-luna`, with low reasoning effort. This API configuration required `svg.model`; the initial request without it was rejected before generation.

| Image model | Seconds | Image + SVG author cost | XML elements | Embedded raster images |
|---|---:|---:|---:|---:|
| Flare | 21.369 | $0.0262965 | 23 | 0 |
| Sunburst | 30.325 | $0.0263365 | 35 | 0 |

`derived/svg-comparison.html` displays originals at 32, 128 and 512 CSS pixels, plus locally recolored versions and versions with one circle radius enlarged by 15%. Original files are unchanged. The viewer can toggle light/dark artwork backgrounds.

The Flare wordmark visibly clips at the SVG edges in browser rendering. Its text uses Arial/Helvetica rather than outlined glyphs, so font metrics can affect fit. The Sunburst file also contains font-dependent text. These are editable vector outputs, not automatically production-ready brand assets. Color visibility depends on the chosen background. No API calls were used for the derived color and geometry edits.

## GIFs and explicit sprite sheets

Both native GIF requests succeeded at 512×512 with six actual frames, 200 ms per frame, and infinite looping (`loop=0`), for a 1.2-second cycle. The extracted original frames and inspection JSON are saved under `derived/`.

- Flare owl: $0.017060, 7.016 seconds. The owl changes wing pose, but the requested spectacles are absent and no clear full blink appears in the extracted frames. Character details shift across frames.
- Sunburst mug: $0.017090, 11.270 seconds. Steam visibly changes while the mug remains broadly stable; small appearance changes remain. The last-to-first transition should be judged by watching the loop, not by file metadata alone.

Separately, output 15 renders the supplied local sketch into a polished owl. Output 16 is a six-pose, 3×2 sprite sheet based on that rendered reference. Six 512×512 frames were extracted in row-major order and assembled locally into `derived/sprite-sheet-loop.gif`, with no extra API charge. This exposes pose consistency and alignment directly. The generated sheet is retained unchanged.

The native GIF API returned finished GIFs, not its intermediate sprite sheets. The native GIF frame folders are decoded animation frames; the explicit sprite-sheet file is output 16. The native owl and mug GIFs are independent text-to-animation tests, not animations of the earlier reference assets.

## Files and reproducibility

- `index.html`: all 22 outputs with prompts, settings, timings and costs.
- `comparison.csv`: every attempt, including the validation rejection.
- `ledger.jsonl`: returned usage, per-component cost, elapsed times and artifact hashes.
- `requests/`: exact request parameters, source paths/hashes and prompt text. The corrected SVG attempt has its own file.
- `responses/`: API response metadata and usage. Base64 bodies were decoded into output files.
- `outputs/`: original API artifacts.
- `inputs/`: local owl sketch and transparent markup PNG.
- `derived/`: contact sheets, markup slider, SVG edits, GIF frame extractions and the locally assembled sprite animation.
- `docs/`: saved official documentation and source URLs used for the run.

No API credentials are saved in the project. The Python scripts are retained for inspection. Re-running the existing experiment skips completed outputs; uncertain-charge failures stop further calls. New experiments require their own spending authorization.
