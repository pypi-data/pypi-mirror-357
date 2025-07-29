#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import pandas as pd

from qumin.representations.patterns import ParadigmPatterns


class ParadigmPatternsTestCase(unittest.TestCase):
    def test_check_missing_patterns(self):
        paradigms = pd.DataFrame([
            ['form1', 'lexA', 'cellA'],
            ['form2', 'lexA', 'cellA'],
            ['form3', 'lexA', 'cellB'],
            ['form4', 'lexA', 'cellB'],
            ['form5', 'lexB', 'cellA'],
            ['form6', 'lexB', 'cellB'],
            ['form7', 'lexC', 'cellA'],
            ['form8', 'lexC', 'cellC'],
            ], columns=['form_id', 'lexeme', 'cell']
        ).set_index('form_id')
        table = pd.DataFrame([
            ['form1', 'form3', 'pat1'],
            ['form1', 'form4', 'pat2'],
            ['form2', 'form3', 'pat3'],
            ['form2', 'form4', 'pat4'],
            ['form5', 'form6', 'pat4'],
            ],
            columns=['form_x', 'form_y', 'pattern']
            )
        pair = ['cellA', 'cellB']

        patterns = ParadigmPatterns()

        # Test if correct patterns are accepted:
        try:
            patterns._check_missing_patterns(paradigms, table, pair)
        except ValueError:
            self.fail("patterns._check_missing_patterns unexpectedly raised ValueError.")

        # If we artificially remove some patterns, we should raise ValueError
        self.assertRaises(ValueError, patterns._check_missing_patterns,
                          paradigms, table.iloc[0:2], pair)

