# midi-velocity-mapper

[![PyPI - Version](https://img.shields.io/pypi/v/midi-velocity-mapper.svg)](https://pypi.org/project/midi-velocity-mapper)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/midi-velocity-mapper.svg)](https://pypi.org/project/midi-velocity-mapper)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install midi-velocity-mapper
```

## Usage

```console
usage: mvm [-h] [-i INPUT_PORT] [-o OUTPUT_PORT] [-d]

Translate MIDI velocities using per-note velocity mappings.

options:
  -h, --help            show this help message and exit
  -i, --input-port INPUT_PORT
                        name of MIDI Input port
  -o, --output-port OUTPUT_PORT
                        name of MIDI Output port
  -d, --debug           display debug output
```

The program uses the `config.toml`, described in the next section, to
instantiate per-note velocity curves. It then captures note data from a MIDI
input port and translates note velocities using the curves, passing the
translated data to a MIDI output port. If the MIDI ports are not set via the
command-line flags, prompts are issued to select the appropriate ports
interactively. Currently, only velocities of MIDI "Note On" messages are
translated, but support for "Note Off" velocities, etc. might be added in the
future.

## Configuration

The per-note velocity mappings are defined in a file named `config.toml` in the
current directory. Each section of the TOML file corresponds to a MIDI note
name (with octave also specified). Section names use the format
`[note.NOTENAME]`, where NOTENAME is one of the names listed in the file
`data/keys-all.tsv`.

Supported keys of each section have format `in<NUM>` where `NUM` is in the
range 0-127. Key values are integers in the range 0-127. Together, each
key/value pair represents a mapping of an input velocity to an output velocity.

A maximum of 128 input/output mappings are permitted for each note; this is
enforced by the semantics of TOML and how the key/values are defined in the
config.

See the `config-examples` directory in the git repository for example
config.toml files that illustrate the configuration format.

## License

`midi-velocity-mapper` is distributed under the terms of the
[MIT](https://spdx.org/licenses/MIT.html) license.
