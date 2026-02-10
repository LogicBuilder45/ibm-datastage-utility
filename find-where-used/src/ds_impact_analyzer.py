import sys
import os
import re
from datetime import datetime

BEGIN_RE = re.compile(r'^\s*BEGIN\s+(DS\w+)\b', re.IGNORECASE)
END_RE = re.compile(r'^\s*END\s+(DS\w+)\b', re.IGNORECASE)

IDENTIFIER_RE = re.compile(r'^\s*Identifier\s+"([^"]+)"\s*$', re.IGNORECASE)
NAME_RE = re.compile(r'^\s*Name\s+"([^"]+)"\s*$', re.IGNORECASE)


def extract_object_name(block_lines):
    """
    Best-effort object name extraction from a DSX block.
    Prefer Identifier, else Name.
    """
    for line in block_lines[:300]:
        m = IDENTIFIER_RE.match(line)
        if m:
            return m.group(1)
    for line in block_lines[:300]:
        m = NAME_RE.match(line)
        if m:
            return m.group(1)
    return "UNKNOWN_OBJECT"


def analyze_dsx(dsx_file, search_string):
    search_upper = search_string.upper()
    results = set()

    # Stack items: (block_type, start_line_no, list_of_lines)
    stack = []

    with open(dsx_file, "r", errors="ignore") as f:
        for line in f:
            # If we're inside any block, always append line to the current (top) block
            if stack:
                stack[-1][2].append(line)

            # Check BEGIN
            m_begin = BEGIN_RE.match(line)
            if m_begin:
                btype = m_begin.group(1).upper()

                # Start a new nested block; it becomes the new "current" block
                stack.append([btype, None, [line]])
                continue

            # Check END
            m_end = END_RE.match(line)
            if m_end and stack:
                end_type = m_end.group(1).upper()

                # Pop blocks until we close the matching type (defensive for odd DSX)
                closed_block = None
                while stack:
                    btype, _, blines = stack.pop()
                    closed_block = (btype, blines)
                    if btype == end_type:
                        break

                if closed_block:
                    btype, blines = closed_block

                    # Only evaluate "real" blocks (skip known container wrappers)
                    # This avoids treating DSROUTINES (plural wrapper) as an object itself.
                    if btype not in {"DSROUTINES", "DSPARAMSETS", "DSJOBS"}:
                        block_text_upper = "".join(blines).upper()
                        if search_upper in block_text_upper:
                            obj_name = extract_object_name(blines)
                            results.add(obj_name)

                # If we are still inside a parent block, also append this END line to it
                # (because we popped, the parent is now stack[-1] if it exists)
                if stack:
                    stack[-1][2].append(line)

    return sorted(results)


def main():
    if len(sys.argv) != 3:
        print("Usage: python ds_impact_analyzer.py <dsx_file> <search_string>")
        sys.exit(1)

    dsx_file = sys.argv[1]
    search_string = sys.argv[2]

    if not os.path.isfile(dsx_file):
        print(f"DSX file not found: {dsx_file}")
        sys.exit(1)

    objects = analyze_dsx(dsx_file, search_string)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, f"ds_job_list_result.txt")

    with open(output_file, "w") as out:
        out.write(f"Datetime: {datetime.now()}\n")
        out.write(f"Search string = {search_string}\n")
        out.write(f"Input file: {os.path.basename(dsx_file)}\n")
        out.write(f"Total match count: {len(objects)}\n")
        out.write("------------------------\n")
        out.write("Below is the list of objects where the search string was found\n\n")

        for idx, obj in enumerate(objects, start=1):
            out.write(f"{idx}. object name: {obj}\n")

    print("Impact analysis complete.")
    print(f"Output written to: {output_file}")


if __name__ == "__main__":
    main()
