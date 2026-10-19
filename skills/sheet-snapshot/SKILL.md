---
name: sheet-snapshot
description: Snapshot an Excel (.xlsx/.csv) file or a Google Sheet into a self-contained HTML page that renders the data and lets anyone upload a newer file to see a cell-level diff (added / removed / changed rows) against the snapshot. Use when the user wants to snapshot, freeze, baseline, or "เก็บ snapshot" a spreadsheet, or compare/เปรียบเทียบ a spreadsheet against an earlier version.
---

# Sheet snapshot

Produces ONE standalone HTML file containing the snapshot data plus an upload + diff UI.
All comparison happens in the viewer's browser (SheetJS from cdnjs), no server needed.

## Steps

1. **Get the file locally**
   - Local `.xlsx` / `.xlsm` / `.csv`: use it as-is.
   - Google Sheet URL: download it as `.xlsx` with the Google Drive connector
     (`download_file_content` with export mime type
     `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`) into the scratchpad,
     and pass the sheet URL as `--source`.
   - Legacy `.xls` is not supported by the script; ask the user to resave as `.xlsx`.

2. **Pick the key column(s)** used to match rows between snapshot and upload.
   Look at the headers (first non-empty row of each sheet). Prefer a unique ID column
   (employee ID, รหัส, email, order no.). If no single column is unique, combine columns.
   If unsure, omit `--key`: the page auto-detects a unique ID-like column and the viewer can
   change it with the chips at the top.

3. **Run the script** (Python 3 standard library only):

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/sheet-snapshot/scripts/snapshot.py" "<input>" \
     -o "<out>.html" [--key "Col A,Col B"] [--title "..."] [--source "<url or label>"]
   ```

   Default output name: `<file>-snapshot-<YYYYmmdd-HHMMSS>.html` in the current directory.

4. **Show the result**: open the HTML for the user (browser pane / SendUserFile).

5. **Shareable link (when the user wants one)**: publish the generated HTML with the
   Artifact tool. No capabilities are needed: upload and diff run entirely in the viewer's browser.

   **ALWAYS ask before publishing**, with AskUserQuestion, even if the user already said
   "publish" and even if this session published one before:
   - **Update an existing link**: the snapshot replaces the page at a link people already have.
   - **Create a new link**: a separate page with its own URL.

   If they pick an existing link:
   - Use the URL they gave; if none, ask for it (or offer `action: "list"` to find it).
   - `action: "read"` the URL first. If the result does not say the user is a **writer**
     (they only have view/comment access), stop and say they need Editor access from the
     owner, or offer a new link instead. Never fall back to a new link silently.
   - Publish with `url` set to that link, so the URL and its sharing stay the same.
   - On a conflict (someone published in between), say so, then republish onto the newer version.

   If they pick a new link: publish without `url`, with icon `table`.

   After publishing, give the link and remind them it is private until they (the owner)
   share it from the page's Share menu.

## What the page does
- Tabs: snapshot table (searchable) / comparison result.
- Drag-drop or pick a `.xlsx`/`.csv` → matched by sheet name (or the only sheet) → diff.
- Columns matched by trimmed header name, so reordered columns are fine; added/removed
  columns are reported.
- Values normalised before comparing: whitespace trimmed/collapsed, `"1"` == `1`,
  dates compared as `YYYY-MM-DD[ HH:MM:SS]`.
- Duplicate keys are flagged; with no key, rows are compared by position.

## Limits
- First non-empty row is treated as the header row.
- Formulas are compared by cached value (what Excel last calculated), not the formula text.
- Hidden sheets are skipped. Very large sheets (>100k rows) make a heavy HTML file.
