# FILENAME: checker.py
# Run: python core/checker.py  (from backend/ folder)

import unittest
from unittest.mock import patch, MagicMock
from core.spell_checker import SpellChecker, QUERY_THRESHOLD, MAX_SUGGESTIONS
from core.bk_tree import BKTree, BKNode
from core.levenshtein import Levenshtein, WeightedLevenshtein
from core.keyboard_proximity import substitution_cost, ADJACENT_COST, NORMAL_COST
from core.sorter import sort_candidates, _positional_similarity, _keyboard_proximity_score


# ── Helpers ────────────────────────────────────────────────────────────────── #

SAMPLE_WORDLIST = [
    "balay", "dagat", "langit", "tubig", "adlaw",
    "bulan", "bituon", "hangin", "ulan", "kalayo",
    "maayo", "dako", "gamay", "pula", "puti",
]

def make_checker():
    sc = SpellChecker()
    sc.load_wordlist(SAMPLE_WORDLIST)
    return sc


# ══════════════════════════════════════════════════════════════════════════════
# keyboard_proximity.py
# ══════════════════════════════════════════════════════════════════════════════

class TestSubstitutionCost(unittest.TestCase):

    def test_same_character_returns_zero(self):
        self.assertEqual(substitution_cost('a', 'a'), 0)
        self.assertEqual(substitution_cost('z', 'z'), 0)

    def test_adjacent_keys_return_half_cost(self):
        self.assertEqual(substitution_cost('q', 'w'), ADJACENT_COST)
        self.assertEqual(substitution_cost('s', 'd'), ADJACENT_COST)

    def test_non_adjacent_keys_return_normal_cost(self):
        self.assertEqual(substitution_cost('a', 'p'), NORMAL_COST)
        self.assertEqual(substitution_cost('q', 'z'), NORMAL_COST)

    def test_adjacency_cost_is_valid(self):
        cost = substitution_cost('a', 'b')
        self.assertIn(cost, (ADJACENT_COST, NORMAL_COST))

    def test_cost_values_are_correct(self):
        self.assertEqual(ADJACENT_COST, 0.5)
        self.assertEqual(NORMAL_COST, 1.0)


# ══════════════════════════════════════════════════════════════════════════════
# levenshtein.py
# ══════════════════════════════════════════════════════════════════════════════

class TestLevenshtein(unittest.TestCase):

    def test_identical_strings_distance_zero(self):
        lev = Levenshtein("balay", "balay")
        self.assertEqual(lev.minDistance("balay", "balay"), 0)

    def test_single_insertion(self):
        lev = Levenshtein("cat", "cats")
        self.assertEqual(lev.minDistance("cat", "cats"), 1)

    def test_single_deletion(self):
        lev = Levenshtein("cats", "cat")
        self.assertEqual(lev.minDistance("cats", "cat"), 1)

    def test_single_substitution(self):
        lev = Levenshtein("cat", "bat")
        self.assertEqual(lev.minDistance("cat", "bat"), 1)

    def test_empty_source(self):
        lev = Levenshtein("", "abc")
        self.assertEqual(lev.minDistance("", "abc"), 3)

    def test_empty_target(self):
        lev = Levenshtein("abc", "")
        self.assertEqual(lev.minDistance("abc", ""), 3)

    def test_both_empty(self):
        lev = Levenshtein("", "")
        self.assertEqual(lev.minDistance("", ""), 0)

    def test_completely_different_strings(self):
        lev = Levenshtein("abc", "xyz")
        self.assertEqual(lev.minDistance("abc", "xyz"), 3)

    def test_known_distance_kitten_sitting(self):
        lev = Levenshtein("kitten", "sitting")
        self.assertEqual(lev.minDistance("kitten", "sitting"), 3)


class TestWeightedLevenshtein(unittest.TestCase):

    def test_identical_strings_distance_zero(self):
        wl = WeightedLevenshtein("balay", "balay")
        self.assertEqual(wl.minDistance("balay", "balay"), 0)

    def test_adjacent_key_substitution_cheaper_than_normal(self):
        wl_adj = WeightedLevenshtein("a", "s")
        wl_far = WeightedLevenshtein("a", "p")
        self.assertLess(wl_adj.minDistance("a", "s"), wl_far.minDistance("a", "p"))

    def test_adjacent_substitution_cost(self):
        wl = WeightedLevenshtein("a", "s")
        self.assertEqual(wl.minDistance("a", "s"), ADJACENT_COST)

    def test_non_adjacent_substitution_cost(self):
        wl = WeightedLevenshtein("a", "p")
        self.assertEqual(wl.minDistance("a", "p"), NORMAL_COST)

    def test_weighted_distance_lte_standard(self):
        std = Levenshtein("balay", "balag")
        wl  = WeightedLevenshtein("balay", "balag")
        self.assertLessEqual(
            wl.minDistance("balay", "balag"),
            std.minDistance("balay", "balag")
        )


# ══════════════════════════════════════════════════════════════════════════════
# bk_tree.py
# ══════════════════════════════════════════════════════════════════════════════

class TestBKNode(unittest.TestCase):

    def test_node_stores_word(self):
        node = BKNode("balay")
        self.assertEqual(node.word, "balay")

    def test_node_children_empty_on_init(self):
        node = BKNode("balay")
        self.assertEqual(node.children, {})


class TestBKTree(unittest.TestCase):

    def test_insert_single_word_becomes_root(self):
        tree = BKTree()
        tree.insert("balay")
        self.assertIsNotNone(tree.root)
        self.assertEqual(tree.root.word, "balay")

    def test_insert_multiple_words(self):
        tree = BKTree()
        for w in ["balay", "dagat", "langit"]:
            tree.insert(w)
        self.assertIsNotNone(tree.root)

    def test_query_empty_tree_returns_empty(self):
        tree = BKTree()
        self.assertEqual(tree.query("balay", 2), [])

    def test_query_exact_match(self):
        tree = BKTree()
        tree.insert("balay")
        words = [w for w, _ in tree.query("balay", 0)]
        self.assertIn("balay", words)

    def test_query_within_threshold(self):
        tree = BKTree()
        for w in ["balay", "dagat", "tubig"]:
            tree.insert(w)
        words = [w for w, _ in tree.query("balag", 1.5)]
        self.assertIn("balay", words)

    def test_query_outside_threshold_excluded(self):
        tree = BKTree()
        tree.insert("balay")
        self.assertEqual(tree.query("xyz", 0), [])

    def test_duplicate_insert_no_crash(self):
        tree = BKTree()
        tree.insert("balay")
        tree.insert("balay")  # should not raise

    def test_query_returns_word_distance_tuples(self):
        tree = BKTree()
        tree.insert("balay")
        for w, d in tree.query("balay", 0):
            self.assertIsInstance(w, str)
            self.assertIsInstance(d, (int, float))


# ══════════════════════════════════════════════════════════════════════════════
# sorter.py
# ══════════════════════════════════════════════════════════════════════════════

class TestPositionalSimilarity(unittest.TestCase):

    def test_identical_words(self):
        self.assertEqual(_positional_similarity("balay", "balay"), 5)

    def test_no_overlap(self):
        self.assertEqual(_positional_similarity("aaaaa", "bbbbb"), 0)

    def test_partial_overlap(self):
        self.assertEqual(_positional_similarity("balay", "balag"), 4)

    def test_different_length_uses_zip(self):
        self.assertEqual(_positional_similarity("abc", "abcdef"), 3)


class TestKeyboardProximityScore(unittest.TestCase):

    def test_identical_words_score_zero(self):
        self.assertEqual(_keyboard_proximity_score("balay", "balay"), 0)

    def test_adjacent_substitution_yields_non_negative(self):
        self.assertGreaterEqual(_keyboard_proximity_score("balay", "balag"), 0)

    def test_more_differences_higher_score(self):
        score_one = _keyboard_proximity_score("bala", "bals")
        score_two = _keyboard_proximity_score("bala", "bsls")
        self.assertGreaterEqual(score_two, score_one)


class TestSortCandidates(unittest.TestCase):

    def test_empty_candidates(self):
        self.assertEqual(sort_candidates([], "balay"), [])

    def test_closer_edit_distance_ranked_first(self):
        candidates = [("balag", 0.5), ("dagat", 2.0)]
        ranked = sort_candidates(candidates, "balay")
        self.assertEqual(ranked[0][0], "balag")

    def test_same_distance_higher_positional_sim_first(self):
        candidates = [("baaay", 1.0), ("balay", 1.0)]
        ranked = sort_candidates(candidates, "balay")
        self.assertEqual(ranked[0][0], "balay")

    def test_returns_all_candidates(self):
        candidates = [("balay", 0), ("balag", 0.5), ("tubig", 3.0)]
        self.assertEqual(len(sort_candidates(candidates, "balay")), 3)

    def test_output_preserves_tuples(self):
        ranked = sort_candidates([("balay", 1.0)], "balay")
        self.assertIsInstance(ranked[0], tuple)
        self.assertEqual(len(ranked[0]), 2)


# ══════════════════════════════════════════════════════════════════════════════
# spell_checker.py
# ══════════════════════════════════════════════════════════════════════════════

class TestSpellCheckerLoading(unittest.TestCase):

    def test_load_wordlist_populates_tree(self):
        sc = SpellChecker()
        sc.load_wordlist(["balay", "dagat"])
        self.assertEqual(sc.wordlist_size, 2)

    def test_load_wordlist_strips_whitespace(self):
        sc = SpellChecker()
        sc.load_wordlist(["  balay  ", "\tdagat\n"])
        self.assertEqual(sc.wordlist_size, 2)

    def test_load_wordlist_lowercases(self):
        sc = SpellChecker()
        sc.load_wordlist(["BALAY", "Dagat"])
        self.assertTrue(sc.is_correct("balay"))
        self.assertTrue(sc.is_correct("dagat"))

    def test_load_wordlist_deduplicates(self):
        sc = SpellChecker()
        sc.load_wordlist(["balay", "balay", "BALAY"])
        self.assertEqual(sc.wordlist_size, 1)

    def test_load_wordlist_ignores_empty_lines(self):
        sc = SpellChecker()
        sc.load_wordlist(["balay", "", "  ", "dagat"])
        self.assertEqual(sc.wordlist_size, 2)

    def test_load_wordlist_incremental(self):
        sc = SpellChecker()
        sc.load_wordlist(["balay"])
        sc.load_wordlist(["dagat"])
        self.assertEqual(sc.wordlist_size, 2)


class TestSpellCheckerIsCorrect(unittest.TestCase):

    def setUp(self):
        self.checker = make_checker()

    def test_known_word_is_correct(self):
        self.assertTrue(self.checker.is_correct("balay"))

    def test_unknown_word_is_incorrect(self):
        self.assertFalse(self.checker.is_correct("xyzzy"))

    def test_case_insensitive(self):
        self.assertTrue(self.checker.is_correct("BALAY"))
        self.assertTrue(self.checker.is_correct("Dagat"))

    def test_empty_string_is_incorrect(self):
        self.assertFalse(self.checker.is_correct(""))


class TestSpellCheckerCheck(unittest.TestCase):

    def setUp(self):
        self.checker = make_checker()

    def test_correct_word_returns_empty_list(self):
        self.assertEqual(self.checker.check("balay"), [])

    def test_misspelled_word_returns_suggestions(self):
        suggestions = self.checker.check("balag")
        self.assertIsInstance(suggestions, list)
        self.assertLessEqual(len(suggestions), MAX_SUGGESTIONS)

    def test_suggestions_are_strings(self):
        for s in self.checker.check("balag"):
            self.assertIsInstance(s, str)

    def test_empty_string_returns_empty(self):
        self.assertEqual(self.checker.check(""), [])

    def test_whitespace_only_returns_empty(self):
        self.assertEqual(self.checker.check("   "), [])

    def test_max_suggestions_respected(self):
        self.assertLessEqual(len(self.checker.check("balag", max_suggestions=1)), 1)

    def test_max_suggestions_default(self):
        self.assertLessEqual(len(self.checker.check("balag")), MAX_SUGGESTIONS)

    def test_very_different_word_returns_list(self):
        self.assertIsInstance(self.checker.check("zzzzzzzz"), list)

    def test_close_misspelling_includes_correct_word(self):
        self.assertIn("adlaw", self.checker.check("adlw"))

    def test_case_normalised_before_check(self):
        self.assertIsInstance(self.checker.check("BALAG"), list)

    def test_suggestions_are_from_wordlist(self):
        for s in self.checker.check("balag"):
            self.assertTrue(self.checker.is_correct(s))


class TestSpellCheckerWordlistSize(unittest.TestCase):

    def test_empty_checker_size_zero(self):
        self.assertEqual(SpellChecker().wordlist_size, 0)

    def test_size_matches_unique_words(self):
        sc = SpellChecker()
        sc.load_wordlist(SAMPLE_WORDLIST)
        expected = len(set(w.lower() for w in SAMPLE_WORDLIST))
        self.assertEqual(sc.wordlist_size, expected)


# ══════════════════════════════════════════════════════════════════════════════
# Integration tests
# ══════════════════════════════════════════════════════════════════════════════

class TestIntegration(unittest.TestCase):

    def setUp(self):
        self.checker = make_checker()

    def test_full_pipeline_correct_word(self):
        self.assertEqual(self.checker.check("balay"), [])

    def test_full_pipeline_one_typo(self):
        self.assertGreaterEqual(len(self.checker.check("balat")), 1)

    def test_full_pipeline_adjacent_key_typo(self):
        self.assertIn("balay", self.checker.check("balau"))

    def test_weighted_distance_prefers_adjacent_typo(self):
        wl_adj = WeightedLevenshtein("balay", "balag")
        wl_far = WeightedLevenshtein("balay", "balap")
        self.assertLessEqual(
            wl_adj.minDistance("balay", "balag"),
            wl_far.minDistance("balay", "balap")
        )

    def test_bktree_query_matches_spell_checker_suggestions(self):
        word = "daggat"
        tree_words = {w for w, _ in self.checker._tree.query(word, QUERY_THRESHOLD)}
        for s in self.checker.check(word):
            self.assertIn(s, tree_words)

    def test_wordlist_reload_adds_new_words(self):
        self.checker.load_wordlist(["bag-o"])
        self.assertTrue(self.checker.is_correct("bag-o"))


# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(__import__(__name__))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    total  = result.testsRun
    failed = len(result.failures) + len(result.errors)
    passed = total - failed

    print("\n" + "═" * 50)
    print(f"  RESULTS: {passed}/{total} passed", end="")
    if failed:
        print(f"  |  {failed} failed")
    else:
        print("  ✓ All tests passed!")
    print("═" * 50)