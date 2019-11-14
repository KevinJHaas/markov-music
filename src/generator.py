#!/usr/bin/env python3
# This class handles the generation of a new song given a markov chain
# containing the note transitions and their frequencies.
import argparse
import mido

from markov_chain import MarkovChain
from midi_parser import MidiParser


class Generator:
    def __init__(self, markov_chain):
        self.markov_chain = markov_chain

    @staticmethod
    def load(markov_chain):
        assert isinstance(markov_chain, MarkovChain)
        return Generator(markov_chain)

    def _note_to_messages(self, note):
        return [
            mido.Message("note_on", note=note.note, velocity=127, time=0),
            mido.Message("note_off", note=note.note, velocity=0, time=note.duration),
        ]

    def generate(self, filename, numtracks):
        with mido.midifiles.MidiFile() as midi:
            for tracknum in range(numtracks):
                track = mido.MidiTrack()
                last_note = None
                # Generate a sequence of 100 notes
                for i in range(100):
                    new_note = self.markov_chain.get_next(last_note)
                    track.extend(self._note_to_messages(new_note))
                midi.tracks.append(track)
            midi.save(filename)


if __name__ == "__main__":
    # Example usage:
    # python generator.py <in.mid> <out.mid>

    parser = argparse.ArgumentParser()
    parser.add_argument("infile", metavar="in.mid", help="The midi input file")
    parser.add_argument(
        "outfile", metavar="out.mid", help="Where to put the generated midi file"
    )
    parser.add_argument(
        "-n", dest="numtracks", help="How many tracks to generate", default=1, type=int
    )

    args = parser.parse_args()

    chain = MidiParser(args.infile).get_chain()
    Generator.load(chain).generate(args.outfile, args.numtracks)
    print("Generated markov chain at file", args.outfile)
