# SPDX-FileCopyrightText: 2025 Patrick McCarty <pnorcks@gmail.com>
#
# SPDX-License-Identifier: MIT

import argparse
import math
import re
import tomllib

import mido

from rich import print as rprint
from rich.prompt import Prompt

from midi_velocity_mapper.util import debug
from midi_velocity_mapper.util import info
from midi_velocity_mapper.util import warning
from midi_velocity_mapper.util import fatal
from midi_velocity_mapper.util import int_in_range
from midi_velocity_mapper.util import load_id_name_mapping
from midi_velocity_mapper.util import load_name_id_mapping


VELOCITY_MAP = dict()


def _process_curve_for_note(note_id, mappings):
    """Process a curve for a MIDI note defined by in/out velocity mappings."""
    global VELOCITY_MAP

    test_val = note_id
    if not int_in_range(test_val):
        fatal(f"Note {note_id} must be an integer between 0 and 127 inclusive... instead, found {test_val}")

    parsed_mappings = []
    for in_key, out_val in mappings.items():
        # The keys representing input velocities have a specific format:
        # in<NUM>, where NUM is in the range 0-127. Reject any other key names,
        # specifically for the purposes of curve generation. Do not issue a
        # warning, since other key/values might be used for other purposes in
        # the future.
        if not re.search(r'^in[0-9]{1,3}$', in_key):
            continue
        test_val = in_key[2:]
        # FIXME: need better error messages here so that the Note "ID" matches
        # the identifier specified in the TOML file.
        if not int_in_range(test_val):
            fatal(f"Note {note_id}: input velocity must be an integer between 0 and 127 inclusive... instead, found {test_val}")
        in_val = int(test_val)
        test_val = out_val
        if not int_in_range(test_val):
            fatal(f"Note {note_id}: output velocity must be an integer between 0 and 127 inclusive... instead, found {test_val}")
        out_val = int(test_val)
        parsed_mappings.append(tuple((in_val, out_val)))

    # Now instantiate a complete velocity mapping table for the note,
    # consulting the parsed input/output mappings defined for it. Precomputing
    # the values is better, to minimize the runtime performance, due to the
    # expectation of this program being run in a realtime environment.

    # Start by instantiating a linear mapping, just to fill in values.

    note_int = int(note_id)
    VELOCITY_MAP[note_int] = dict()
    for v in range(0, 128):
        VELOCITY_MAP[note_int][v] = v

    # Then adjust it according to the individual mappings.
    start_curve = 0
    end_curve = 127
    seg_start_in = 0
    seg_start_out = 0
    # Make sure mappings are sorted by input velocity, ensuring correct curve generation
    for pair in sorted(parsed_mappings):
        i = pair[0]
        o = pair[1]
        if i == start_curve:
            # we are at the beginning of the curve, so this begins the first segment
            VELOCITY_MAP[note_int][i] = o
            continue

        # create a linear segment by filling in all values in the range {seg_start_in .. i}
        delta_out = o - seg_start_out
        delta_in = i - seg_start_in
        for seg_mid_in in range(seg_start_in, i+1):
            seg_mid_out = seg_start_out + math.floor(delta_out * ((seg_mid_in - seg_start_in) / delta_in))
            VELOCITY_MAP[note_int][seg_mid_in] = seg_mid_out

        # prepare for next iteration
        seg_start_in = i
        seg_start_out = o

    # FIXME: Create final segment to end at [127,127] if needed,
    # to complete to curve. Perhaps that should be a tunable
    # option though, in case users want to limit the max velocity
    # for certain notes.


def init_velocity_curves():
    config = {}
    with open('config.toml', 'rb') as f:
        config = tomllib.load(f)
    # There must be a toplevel defined called "note".
    notes = config.get('note')
    if not notes:
        fatal("Config: missing 'note' table, required to define mappings.")
    mapped_count = 0
    # Subtables exist for each note with mappings
    for key, mappings in notes.items():
        name_map = load_name_id_mapping()
        note_id = name_map.get(key)
        # FIXME: Additional name mappings should be added to support the
        # various other ways to describe note+octave names, as well as the
        # ability to translate all of it. After this support exists, we must
        # normalize these additional mappings.
        if not note_id:
            warning(f"Config: skipping mapping(s) for unrecognized note name: {key}")
        _process_curve_for_note(note_id, mappings)
        mapped_count = mapped_count + 1
    #debug(VELOCITY_MAP)
    return mapped_count


def translate_velocity(msg, args, name_map):
    if msg.note in VELOCITY_MAP:
        mapped_velocity = VELOCITY_MAP[msg.note][msg.velocity]
        if args.debug:
            debug(f"{name_map[str(msg.note)]:>3}: "
                  f"velocity {msg.velocity:>3} -> "
                  f"{mapped_velocity:>3}")
        return msg.copy(velocity=mapped_velocity)
    else:
        if args.debug:
            debug(f"{name_map[str(msg.note)]:>3}: "
                  f"velocity {msg.velocity:>3} -> "
                  f"(no mapping)")
        return msg


def select_port(names):
    for i, p in enumerate(names):
        rprint(f"\t{i}: {p}")
    indices = [str(i) for i in range(0, len(names))]
    idx_choice = Prompt.ask("Choice of port", choices=indices)
    return names[int(idx_choice)]


def main():
    ap = argparse.ArgumentParser(prog="mvm", description="Translate MIDI velocities using per-note velocity mappings.")
    ap.add_argument("-i", "--input-port", help="name of MIDI Input port")
    ap.add_argument("-o", "--output-port", help="name of MIDI Output port")
    ap.add_argument("-d", "--debug", action='store_true', help="display debug output")
    args = ap.parse_args()

    # Enable user-configurable per-note velocity curves
    mapped_count = init_velocity_curves()
    info(f"Initialized {mapped_count} velocity curves")

    # Enable pretty-printing note names instead of their MIDI note values
    name_map = load_id_name_mapping()
    info("Initialized note name mapping")

    try:
        if args.input_port:
            in_port = args.input_port
        else:
            names = mido.get_input_names()
            info("Select a MIDI Input port")
            # The input port does not need to be opened yet... this is done in
            # the 'with' block below.
            in_port_name = select_port(names)

        if args.output_port:
            out_port = args.output_port
        else:
            in_port_list = mido.get_input_names()
            names = mido.get_output_names()
            info("Select a MIDI Output port")
            # Special case for this program: we want the ability to select a
            # "virtual" output port for other programs to connect to. In other
            # words, the output port does not need to be a pre-existing port.
            names.append("Virtual (freshly allocated)")
            out_port_name = select_port(names)

            if out_port_name == "Virtual (freshly allocated)":
                out_port = mido.open_output()
            else:
                out_port = mido.open_output(out_port_name)

        info(f"MIDI input port: [i]{in_port_name}[/i]")
        info(f"MIDI output port: [i]{out_port_name}[/i]")

        with mido.open_input(in_port_name) as in_port:
            info("Ready for MIDI input")
            for msg in in_port:
                if msg.type == 'note_on':
                    out_msg = translate_velocity(msg, args, name_map)
                else:
                    out_msg = msg.copy()
                out_port.send(out_msg)
    except KeyboardInterrupt:
        pass
    finally:
        info("Exiting program")
        out_port.close()


if __name__ == "__main__":
    main()
