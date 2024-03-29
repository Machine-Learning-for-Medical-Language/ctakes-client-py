#!/usr/bin/env python3
# pylint: disable=invalid-name
"""Generates and shows polarity difference reports between cTAKES and cNLP"""

import argparse
import asyncio
import csv
import json
import os
import sys
import time
from json.decoder import JSONDecodeError

import ctakesclient
from ctakesclient.typesystem import MatchText, Polarity


def default(parser, args):
    del args

    parser.print_help()


async def compare_note_polarity(text: str):
    """
    Prints difference summary (if any)
    """
    ner = await ctakesclient.client.extract(text)

    matches = ner.list_match()
    spans = ner.list_spans(matches)

    polarities_cnlp = await ctakesclient.transformer.list_polarity(text, spans)
    if len(matches) != len(polarities_cnlp):
        raise JSONDecodeError("Polarity lists had different lengths!", text, 0)

    differing = []
    for i in range(len(matches)):
        if matches[i].polarity.value != polarities_cnlp[i].value:
            differing.append(
                {
                    "cnlp_polarity": polarities_cnlp[i].value,
                    "match": matches[i].as_json(),
                }
            )

    return differing


async def calculate(parser, args):
    del parser

    output_path = os.path.splitext(args.notes_path)[0] + ".pdr.ndjson"
    if os.path.exists(output_path) and not args.resume:
        print("Output file already exists. Use --continue if this is intended.", file=sys.stderr)
        sys.exit(1)

    print("Processing...")

    if args.resume:
        mode = "r+"
    else:
        mode = "w"

    total_tic = time.perf_counter()
    with open(output_path, mode, buffering=1, encoding="utf8") as output_file:
        start_processing_after = None
        if args.resume:
            # Read until the end
            line = None
            for line in output_file:
                pass
            if line:
                start_processing_after = json.loads(line)["instance_num"]
                print(f"Resuming after instance id {start_processing_after}...")

        with open(args.notes_path, "r", encoding="utf8") as notes_file:
            notes = csv.DictReader(notes_file)
            for count, note in enumerate(notes, start=1):
                if start_processing_after is not None:
                    if note["INSTANCE_NUM"] == start_processing_after:
                        start_processing_after = None
                    continue

                note_tic = time.perf_counter()
                try:
                    error = None
                    differences = await compare_note_polarity(note["OBSERVATION_BLOB"])
                except JSONDecodeError as e:
                    error = str(e)
                    differences = []

                json.dump(
                    {
                        # Save the instance id for later sanity checking
                        "instance_num": note["INSTANCE_NUM"],
                        "note": note["OBSERVATION_BLOB"],
                        "error": error,
                        "differences": differences,
                    },
                    output_file,
                )
                output_file.write("\n")
                output_file.flush()  # just in case we want to stop halfway
                note_toc = time.perf_counter()

                print(
                    f"Processed note {count} "
                    f"(instance id: {note['INSTANCE_NUM']}) "
                    f"in {note_toc - note_tic:.0f} seconds"
                )
    total_toc = time.perf_counter()

    print(f"Total time spent: {total_toc - total_tic:.0f} seconds")


def note_context(text: str, match: MatchText) -> str:
    """Returns the original line that the match comes from"""
    start = text.rfind("\n", 0, match.begin) + 1
    end = text.find("\n", match.end)
    return text[start:end].strip()


def show_note(args, note):
    if args.diff:
        if len(note["differences"]) < args.diff:
            print("Not enough differences in the specified note! " f"Only {len(note['differences'])}")
            sys.exit(1)

    if args.show_full:
        print(note["note"])
        print("\n\n\n==================================")

    if note["error"]:
        print("ERROR:", note["error"])

    found_any = False

    # Flatten mentions to allow for comma separated mentions
    # That is, these are equivalent: "--mention A --mention B" and "--mention A,B"
    mentions = {x for user_mention in args.mention for x in user_mention.split(",")}

    for count, diff in enumerate(note["differences"], start=1):
        if args.diff and args.diff != count:
            continue

        m = MatchText(source=diff["match"])
        cnlp = diff["cnlp_polarity"]

        if mentions and m.type.value not in mentions:
            continue

        print(f"\n=== differing span {count} ({m.begin}-{m.end}): " f"{m.type.value}: '{m.text}' ===")
        print("cTAKES says:", m.polarity.name)
        print("cNLP says  :", Polarity(cnlp).name)
        print("Context:", note_context(note["note"], m))
        found_any = True

    if not found_any:
        print("No matching differences found!")


async def report(parser, args):
    del parser

    if args.note and args.instance:
        print("You can only specify a note number or an instance number but " "not both", file=sys.stderr)
        sys.exit(1)

    if not args.note and not args.instance:
        print("You must provide a note number or an instance number", file=sys.stderr)
        sys.exit(1)

    with open(args.pdr_path, "r", encoding="utf8") as pdr:
        for count, line in enumerate(pdr, start=1):
            note_data = json.loads(line)

            if args.note and args.note == count:
                show_note(args, note_data)
                return

            if args.instance and args.instance == note_data["instance_num"]:
                show_note(args, note_data)
                return

    print("Note not found!", file=sys.stderr)
    sys.exit(1)


async def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser.set_defaults(func=default)

    calculate_parser = subparsers.add_parser("calculate")
    calculate_parser.add_argument("notes_path", metavar="notes.csv")
    calculate_parser.add_argument("-c", "--continue", dest="resume", action="store_true")
    # TODO: offer an --update option (and/or a --replace with a danger prompt)
    calculate_parser.set_defaults(func=calculate)

    report_parser = subparsers.add_parser("show")
    report_parser.add_argument("pdr_path", metavar="notes.pdr.ndjson")
    report_parser.add_argument("--show-full", action="store_true")
    report_parser.add_argument("--note", type=int, action="store", help="only show differences for this note number")
    report_parser.add_argument("--instance", type=int, action="store", help="only show differences for this note ID")
    report_parser.add_argument("--diff", type=int, action="store", help="only show this specific difference number")
    report_parser.add_argument("--mention", action="append", default=[], help="only show these mention types")
    report_parser.set_defaults(func=report)

    args = parser.parse_args()
    await args.func(parser, args)


if __name__ == "__main__":
    asyncio.run(main())
