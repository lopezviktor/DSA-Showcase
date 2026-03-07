"""Tests for Trie — targeting 100% coverage of trie.py."""
from __future__ import annotations

import pytest

from dsa_toolkit.trie import Trie, TrieKeyError


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def trie() -> Trie[int]:
    return Trie()


@pytest.fixture()
def filled_trie() -> Trie[int]:
    t: Trie[int] = Trie()
    for word, val in [("apple", 1), ("app", 2), ("application", 3), ("banana", 4)]:
        t.insert(word, val)
    return t


# ---------------------------------------------------------------------------
# Initial state
# ---------------------------------------------------------------------------


def test_initial_is_empty(trie: Trie[int]) -> None:
    assert trie.is_empty()


def test_initial_size_zero(trie: Trie[int]) -> None:
    assert trie.size() == 0
    assert len(trie) == 0


# ---------------------------------------------------------------------------
# insert / search / contains
# ---------------------------------------------------------------------------


def test_insert_and_search_single_word(trie: Trie[int]) -> None:
    trie.insert("hello", 42)
    assert trie.search("hello") == 42
    assert trie.size() == 1
    assert not trie.is_empty()


def test_overwrite_value_size_unchanged(trie: Trie[int]) -> None:
    trie.insert("key", 1)
    trie.insert("key", 99)
    assert trie.search("key") == 99
    assert trie.size() == 1


def test_search_nonexistent_raises(trie: Trie[int]) -> None:
    with pytest.raises(TrieKeyError):
        trie.search("ghost")


def test_search_prefix_only_raises(trie: Trie[int]) -> None:
    trie.insert("hello", 1)
    with pytest.raises(TrieKeyError):
        trie.search("hell")


def test_contains_existing_word(trie: Trie[int]) -> None:
    trie.insert("world", 7)
    assert trie.contains("world") is True


def test_contains_nonexistent_word(trie: Trie[int]) -> None:
    assert trie.contains("missing") is False


def test_contains_prefix_not_word(trie: Trie[int]) -> None:
    trie.insert("apple", 1)
    assert trie.contains("app") is False


def test_dunder_contains_true(trie: Trie[int]) -> None:
    trie.insert("foo", 0)
    assert "foo" in trie


def test_dunder_contains_false(trie: Trie[int]) -> None:
    assert "bar" not in trie


def test_dunder_contains_non_string(trie: Trie[int]) -> None:
    trie.insert("x", 1)
    assert 42 not in trie  # type: ignore[operator]


# ---------------------------------------------------------------------------
# starts_with / words_with_prefix
# ---------------------------------------------------------------------------


def test_starts_with_existing_prefix(filled_trie: Trie[int]) -> None:
    assert filled_trie.starts_with("app") is True


def test_starts_with_nonexistent_prefix(filled_trie: Trie[int]) -> None:
    assert filled_trie.starts_with("xyz") is False


def test_starts_with_empty_prefix(filled_trie: Trie[int]) -> None:
    assert filled_trie.starts_with("") is True


def test_starts_with_on_empty_trie(trie: Trie[int]) -> None:
    assert trie.starts_with("") is True
    assert trie.starts_with("a") is False


def test_words_with_prefix_returns_correct(filled_trie: Trie[int]) -> None:
    result = filled_trie.words_with_prefix("app")
    assert result == ["app", "apple", "application"]


def test_words_with_prefix_empty_returns_all(filled_trie: Trie[int]) -> None:
    result = filled_trie.words_with_prefix("")
    assert result == sorted(["apple", "app", "application", "banana"])


def test_words_with_prefix_exact_word(filled_trie: Trie[int]) -> None:
    result = filled_trie.words_with_prefix("banana")
    assert result == ["banana"]


def test_words_with_prefix_no_match(filled_trie: Trie[int]) -> None:
    assert filled_trie.words_with_prefix("zzz") == []


def test_words_with_prefix_equal_full_word_with_extensions(trie: Trie[int]) -> None:
    trie.insert("go", 1)
    trie.insert("golang", 2)
    trie.insert("goroutine", 3)
    result = trie.words_with_prefix("go")
    assert result == ["go", "golang", "goroutine"]


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------


def test_delete_leaf_word(trie: Trie[int]) -> None:
    trie.insert("cat", 1)
    trie.insert("car", 2)
    trie.delete("cat")
    assert not trie.contains("cat")
    assert trie.contains("car")
    assert trie.size() == 1


def test_delete_decrements_size(trie: Trie[int]) -> None:
    trie.insert("abc", 0)
    trie.delete("abc")
    assert trie.size() == 0
    assert trie.is_empty()


def test_delete_prefix_of_other_word(trie: Trie[int]) -> None:
    trie.insert("app", 1)
    trie.insert("apple", 2)
    trie.delete("app")
    assert not trie.contains("app")
    assert trie.contains("apple")
    assert trie.size() == 1


def test_delete_word_that_has_extension(trie: Trie[int]) -> None:
    """Deleting 'app' when 'apple' exists: is_end cleared, node not pruned."""
    trie.insert("app", 1)
    trie.insert("apple", 2)
    trie.delete("app")
    assert trie.starts_with("apple")


def test_delete_extension_leaves_prefix(trie: Trie[int]) -> None:
    trie.insert("app", 1)
    trie.insert("apple", 2)
    trie.delete("apple")
    assert trie.contains("app")
    assert not trie.contains("apple")


def test_delete_nonexistent_raises(trie: Trie[int]) -> None:
    with pytest.raises(TrieKeyError):
        trie.delete("nope")


def test_delete_partial_path_raises(trie: Trie[int]) -> None:
    trie.insert("hello", 1)
    with pytest.raises(TrieKeyError):
        trie.delete("hell")


def test_delete_missing_mid_path_raises(trie: Trie[int]) -> None:
    trie.insert("abc", 1)
    with pytest.raises(TrieKeyError):
        trie.delete("axc")


def test_delete_last_word_empties_trie(trie: Trie[int]) -> None:
    trie.insert("only", 1)
    trie.delete("only")
    assert trie.is_empty()


def test_delete_prunes_dead_nodes(trie: Trie[int]) -> None:
    trie.insert("abc", 1)
    trie.delete("abc")
    # Root should have no children after pruning
    assert trie._root.children == {}


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_empty_string_as_valid_word(trie: Trie[int]) -> None:
    trie.insert("", 0)
    assert trie.contains("") is True
    assert trie.search("") == 0
    assert trie.size() == 1


def test_empty_string_delete(trie: Trie[int]) -> None:
    trie.insert("", 0)
    trie.delete("")
    assert not trie.contains("")
    assert trie.is_empty()


def test_unicode_characters(trie: Trie[str]) -> None:
    trie.insert("café", "coffee")
    trie.insert("naïve", "simple")
    assert trie.search("café") == "coffee"
    assert trie.search("naïve") == "simple"
    assert trie.size() == 2


def test_repeated_characters(trie: Trie[int]) -> None:
    trie.insert("aaa", 1)
    trie.insert("aaaa", 2)
    assert trie.contains("aaa") is True
    assert trie.contains("aaaa") is True
    assert trie.contains("aa") is False


# ---------------------------------------------------------------------------
# IDS scenarios
# ---------------------------------------------------------------------------


def test_ip_prefix_matching() -> None:
    """CIDR-style prefix lookup for IP blacklists."""
    t: Trie[str] = Trie()
    t.insert("192.168.1.", "internal_subnet")
    t.insert("10.0.", "private_10")
    t.insert("172.16.", "private_172")

    # Exact prefix lookup
    assert t.starts_with("192.168.1.")
    assert t.starts_with("10.0.")
    # Address from 192.168.1.x starts with the known prefix
    assert t.starts_with("192.168.1.5"[:9])  # first 9 chars = "192.168.1"
    assert not t.starts_with("8.8.8.")


def test_domain_blacklist_exact_lookup() -> None:
    """Exact domain lookup for C&C blacklist."""
    t: Trie[str] = Trie()
    cnc_domains = ["malware.example.com", "c2.badactor.net", "update.evil.org"]
    for d in cnc_domains:
        t.insert(d, "blocked")

    assert t.contains("malware.example.com")
    assert not t.contains("safe.example.com")
    assert t.search("c2.badactor.net") == "blocked"


def test_domain_blacklist_subdomain_starts_with() -> None:
    """Detect any subdomain of a malicious TLD using starts_with."""
    t: Trie[str] = Trie()
    t.insert("evil.org", "blocked")
    t.insert("also.evil.org", "blocked")

    # Both are present; a raw starts_with on the TLD suffix requires exact prefix
    assert t.starts_with("evil.org")
    assert t.starts_with("also.evil.org")
    assert not t.starts_with("good.org")


def test_words_with_prefix_enumerate_tld() -> None:
    """Enumerate all known malicious domains under a suspicious TLD."""
    t: Trie[str] = Trie()
    domains = [
        "malware.evil.tld",
        "c2.evil.tld",
        "download.evil.tld",
        "safe.good.tld",
    ]
    for d in domains:
        t.insert(d, "alert")

    evil_domains = t.words_with_prefix("malware.evil.tld"[:0] + "")
    # Prefix "" returns all; filter in application code
    assert "malware.evil.tld" in evil_domains
    assert "safe.good.tld" in evil_domains

    specific = t.words_with_prefix("malware")
    assert specific == ["malware.evil.tld"]


# ---------------------------------------------------------------------------
# repr
# ---------------------------------------------------------------------------


def test_repr(filled_trie: Trie[int]) -> None:
    assert repr(filled_trie) == "Trie(size=4)"


def test_repr_empty(trie: Trie[int]) -> None:
    assert repr(trie) == "Trie(size=0)"
