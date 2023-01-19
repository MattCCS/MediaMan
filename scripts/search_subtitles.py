"""
Search .vtt files in MediaMan for the given text.
"""

import re
import sys
import pathlib
from collections import defaultdict

from mediaman.core import api


PREVIEW_MARGIN = 40


def lac_vtt():
    files = list(api.run_fuzzy(".vtt", service_selector="lac"))[0][1]
    return files


def all_vtt():
    responses = list(api.run_fuzzy(".vtt", service_selector="all"))[0][1]
    return [
        f for response in responses
        for f in response.response
    ]


def main():
    query = " ".join(sys.argv[1:]).lower()

    # 1) Find all .vtt files
    print("Finding all .vtt files...")
    vtt_files = all_vtt()
    # vtt_files = lac_vtt()
    # print(vtt_files)

    # 2) Download all .vtt files content
    def content(f):
        print(f"Downloading {f['name'], f['id']} ...")
        bytez = b"".join(api.run_stream(root=pathlib.Path(), file_name=f["id"]))
        text = bytez.decode("utf-8")
        return text

    vtt_content = {}
    for f in vtt_files:
        if f["hashes"][0] not in vtt_content:
            vtt_content[f["hashes"][0]] = (f, content(f))
    # print(content)

    matches = defaultdict(list)

    # 3) Search for text
    for (hash, (f, text)) in vtt_content.items():
        for m in re.finditer(query, text.lower()):
            start = max(0, m.start() - PREVIEW_MARGIN)
            end = m.end() + PREVIEW_MARGIN
            matches[(f["name"], hash)].append(text[start:end])

    # 4) Print results
    for (file_name, results) in matches.items():
        print("-" * len(file_name))
        print(file_name)
        for result in results:
            result_oneline = result.replace("\n", " ")
            print(f"〈 {result_oneline} 〉")


if __name__ == "__main__":
    main()
