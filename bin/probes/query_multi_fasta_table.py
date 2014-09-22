#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
(c) 2014 Brant Faircloth || http://faircloth-lab.org/
All rights reserved.

This code is distributed under a 3-clause BSD license. Please see
LICENSE.txt for more information.

Created on 11 April 2014 15:08 PDT (-0700)
"""


import os
import numpy
import sqlite3
import argparse
from collections import Counter

import pdb

class SpecificCountsAction(argparse.Action):
    def __call__(self, parser, args, values, option = None):
        args.specific_counts=values
        if args.specific_counts and not args.output:
            parser.error("If you request --specific-counts, you must also use --output.")


def get_args():
    """Get arguments from CLI"""
    parser = argparse.ArgumentParser(
        description="""Query the multimerge taxa to output matching loci"""
    )
    parser.add_argument(
        "--db",
        required=True,
        help="""The database to query"""
    )
    parser.add_argument(
        "--output",
        help="""When using --specific-counts, output a BED file of those loci"""
    )
    parser.add_argument(
        "--base-taxon",
        required=True,
        type=str,
        help="""The base taxon to use."""
    )
    parser.add_argument(
        "--specific-counts",
        type=int,
        default=None,
        action=SpecificCountsAction,
        help="""Return data for a specific minimum number of taxa."""
    )
    return parser.parse_args()

def main():
    args = get_args()
    conn = sqlite3.connect(args.db)
    cur = conn.cursor()
    # get header names
    cur.execute("PRAGMA table_info({})".format(args.base_taxon))
    values = [str(r[1]) for r in cur.fetchall()]
    #pdb.set_trace()
    taxa = values[1:]
    if not args.specific_counts:
        # query all the data
        query = "SELECT * FROM {}".format(args.base_taxon)
        counts = numpy.zeros(len(taxa) + 1)
        for row in cur.execute(query):
            #pdb.set_trace()
            ss = sum(row[1:])
            counts[ss] += 1
        for i in xrange(len(taxa) + 1):
            print "Loci shared by {} taxa:\t{:,}".format(i, sum(counts[i:]))
    else:
        # query all the data
        query = "SELECT * FROM {}".format(args.base_taxon)
        c = Counter()
        total_loci = 0
        with open(args.output, 'w') as outf1:
            outf1.write("# Hits against {} taxa\n".format(str(args.specific_counts)))
            outf1.write("# {}\n".format(",".join(taxa)))
            outf1.write("[hits]\n")
            with open("{}.missing.matrix".format(args.output), 'w') as outf2:
                outf2.write("# {}\n".format(",".join(taxa)))
                outf2.write("[misses]\n")
                for row in cur.execute(query):
                    taxon_count = sum(row[1:])
                    if taxon_count >= args.specific_counts:
                        row_taxa = [taxa[i] for i,j in enumerate(row[1:]) if j == 1]
                        c += Counter(row_taxa)
                        total_loci += 1
                        outf1.write("{}\n".format(row[0]))
                    else:
                        outf2.write("{}\t{}\n".format(row[0], taxon_count, ",".join([str(i) for i in row[1:]])))
        print c
        print "Total loci = {}".format(total_loci)



if __name__ == '__main__':
    main()
