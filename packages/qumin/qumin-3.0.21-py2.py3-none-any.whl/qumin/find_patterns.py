# !usr/bin/python3
# -*- coding: utf-8 -*-
"""Cluster lemmas according to their paradigms.

Author: Sacha Beniamine.
"""
import logging

from .utils import adjust_cpus
from .clustering import find_microclasses
from .representations import segments
from .representations.paradigms import Paradigms
from .representations.patterns import ParadigmPatterns

log = logging.getLogger("Qumin")


def pat_command(cfg, md):
    r"""Find pairwise alternation patterns from paradigms."""
    # Loading files and paths
    kind = cfg.pats.kind
    defective = cfg.pats.defective
    overabundant = cfg.pats.overabundant
    segcheck = True

    # Initializing segments
    sounds_file_name = md.get_table_path("sounds")
    segments.Inventory.initialize(sounds_file_name)

    num_cpus = adjust_cpus(cfg.cpus)
    paradigms = Paradigms(md.paralex,
                          defective=defective,
                          overabundant=overabundant,
                          segcheck=segcheck,
                          cells=cfg.cells,
                          pos=cfg.pos,
                          force=cfg.force,
                          sample_lexemes=cfg.sample_lexemes,
                          sample_cells=cfg.sample_cells,
                          sample_kws=dict(force_random=cfg.force_random,
                                          seed=cfg.seed),
                          resegment=cfg.resegment
                          )

    patterns = ParadigmPatterns()

    patterns.find_patterns(paradigms,
                           method=kind,
                           optim_mem=cfg.pats.optim_mem,
                           gap_prop=cfg.pats.gap_proportion,
                           cpus=num_cpus)

    patterns.unmerge_columns(paradigms)

    for pair, df in patterns.items():
        has_empty_patterns = (df.form_x != '') & (df.form_y != '') & (df.pattern.isnull())
        n = sum(has_empty_patterns)
        if has_empty_patterns.any():
            log.warning(f"{n} words don't have any patterns for {pair} "
                        "-- This means something went wrong."
                        "Please report this as a bug ! Examples:")
            log.warning(df[has_empty_patterns].sample(min(n, 10)))

    microclasses = find_microclasses(paradigms, patterns)
    filename = md.get_path("microclasses.txt")
    log.info("Found %s microclasses. Printing microclasses to %s", len(microclasses), filename)
    with open(filename, "w", encoding="utf-8") as flow:
        for m in sorted(microclasses, key=lambda m: len(microclasses[m])):
            flow.write("\n\n{} ({}) \n\t".format(m, len(microclasses[m])) + ", ".join(microclasses[m]))
    md.register_file("microclasses.txt", description="Microclass computation")

    patterns.export(md, kind, optim_mem=cfg.pats.optim_mem)
