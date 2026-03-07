"""Integration tests: BloomFilter → HashMap → PriorityQueue IDS pipeline.

Simulates a multi-stage intrusion detection system:

  Stage 1 — BloomFilter   : probabilistic first-pass (O(k), memory-efficient)
  Stage 2 — HashMap       : exact threat-record lookup (O(1) average)
  Stage 3 — PriorityQueue : alert queue ordered by severity (max-heap)

This mirrors a real edge-deployment IDS pipeline where cheap probabilistic
filters guard expensive exact lookups, and confirmed threats are queued for
triage in severity order.
"""
from __future__ import annotations

from dataclasses import dataclass

import pytest

from dsa_toolkit.bloom_filter import BloomFilter
from dsa_toolkit.hash_map import HashMap, KeyNotFoundError
from dsa_toolkit.priority_queue import PriorityQueue, EmptyPriorityQueueError


# ---------------------------------------------------------------------------
# Domain types
# ---------------------------------------------------------------------------


@dataclass
class ThreatRecord:
    ip: str
    severity: int      # 1–10
    attack_type: str
    description: str


@dataclass
class Alert:
    ip: str
    severity: int
    attack_type: str

    # PriorityQueue compares by priority value (int here), not by item.
    # No ordering needed on Alert itself.


# ---------------------------------------------------------------------------
# Shared pipeline fixture
# ---------------------------------------------------------------------------


KNOWN_THREATS: list[ThreatRecord] = [
    ThreatRecord("192.168.1.10", 9, "DDoS",        "High-volume SYN flood"),
    ThreatRecord("10.0.0.55",    7, "PortScan",     "Stealth SYN scan"),
    ThreatRecord("172.16.0.3",   5, "Brute-Force",  "SSH brute-force attempt"),
    ThreatRecord("192.168.1.99", 3, "Probe",        "ICMP sweep"),
    ThreatRecord("10.0.0.200",   8, "Exploit",      "CVE-2023-XXXX RCE attempt"),
]


@pytest.fixture()
def pipeline() -> tuple[BloomFilter, HashMap[str, ThreatRecord], PriorityQueue[int, Alert]]:
    """Return a fully loaded (bloom_filter, threat_db, alert_queue) triple."""
    bloom: BloomFilter = BloomFilter(capacity=1000, error_rate=0.001)
    threat_db: HashMap[str, ThreatRecord] = HashMap()
    alert_queue: PriorityQueue[int, Alert] = PriorityQueue()

    for record in KNOWN_THREATS:
        bloom.add(record.ip)
        threat_db.put(record.ip, record)

    return bloom, threat_db, alert_queue


# ---------------------------------------------------------------------------
# Helper: process a single packet IP through the full pipeline
# ---------------------------------------------------------------------------


def process_packet(
    src_ip: str,
    bloom: BloomFilter,
    threat_db: HashMap[str, ThreatRecord],
    alert_queue: PriorityQueue[int, Alert],
) -> bool:
    """Run one packet through the three-stage pipeline.

    Returns True if the packet triggered a confirmed alert.
    """
    # Stage 1 — fast probabilistic filter
    if src_ip not in bloom:
        return False

    # Stage 2 — exact lookup (eliminates false positives)
    if not threat_db.contains_key(src_ip):
        return False

    # Stage 3 — enqueue confirmed alert by severity
    record = threat_db.get(src_ip)
    alert_queue.push(record.severity, Alert(record.ip, record.severity, record.attack_type))
    return True


# ---------------------------------------------------------------------------
# Stage 1: BloomFilter behaviour inside the pipeline
# ---------------------------------------------------------------------------


class TestBloomFilterStage:
    def test_all_known_threats_pass_filter(self, pipeline):
        bloom, threat_db, _ = pipeline
        for record in KNOWN_THREATS:
            assert record.ip in bloom

    def test_benign_ips_blocked_by_filter(self, pipeline):
        bloom, _, _ = pipeline
        benign = ["8.8.8.8", "1.1.1.1", "203.0.113.1"]
        for ip in benign:
            assert ip not in bloom

    def test_filter_is_not_empty_after_load(self, pipeline):
        bloom, _, _ = pipeline
        assert not bloom.is_empty()
        assert bloom.num_added() == len(KNOWN_THREATS)


# ---------------------------------------------------------------------------
# Stage 2: HashMap exact-lookup behaviour inside the pipeline
# ---------------------------------------------------------------------------


class TestHashMapStage:
    def test_all_threats_stored_in_db(self, pipeline):
        _, threat_db, _ = pipeline
        for record in KNOWN_THREATS:
            assert threat_db.contains_key(record.ip)

    def test_threat_record_fields_intact(self, pipeline):
        _, threat_db, _ = pipeline
        record = threat_db.get("192.168.1.10")
        assert record.severity == 9
        assert record.attack_type == "DDoS"

    def test_unknown_ip_not_in_db(self, pipeline):
        _, threat_db, _ = pipeline
        assert not threat_db.contains_key("99.99.99.99")

    def test_get_unknown_raises(self, pipeline):
        _, threat_db, _ = pipeline
        with pytest.raises(KeyNotFoundError):
            threat_db.get("99.99.99.99")


# ---------------------------------------------------------------------------
# Stage 3: PriorityQueue alert ordering inside the pipeline
# ---------------------------------------------------------------------------


class TestPriorityQueueStage:
    def test_alerts_dequeued_highest_severity_first(self, pipeline):
        bloom, threat_db, alert_queue = pipeline
        for record in KNOWN_THREATS:
            process_packet(record.ip, bloom, threat_db, alert_queue)

        severities: list[int] = []
        while not alert_queue.is_empty():
            priority, _ = alert_queue.pop()
            severities.append(priority)

        assert severities == sorted(severities, reverse=True)

    def test_alert_count_matches_confirmed_threats(self, pipeline):
        bloom, threat_db, alert_queue = pipeline
        for record in KNOWN_THREATS:
            process_packet(record.ip, bloom, threat_db, alert_queue)

        assert alert_queue.size() == len(KNOWN_THREATS)

    def test_peek_is_highest_severity(self, pipeline):
        bloom, threat_db, alert_queue = pipeline
        for record in KNOWN_THREATS:
            process_packet(record.ip, bloom, threat_db, alert_queue)

        priority, alert = alert_queue.peek()
        expected_max = max(r.severity for r in KNOWN_THREATS)
        assert priority == expected_max
        assert alert.severity == expected_max

    def test_empty_queue_raises_on_pop(self, pipeline):
        _, _, alert_queue = pipeline
        with pytest.raises(EmptyPriorityQueueError):
            alert_queue.pop()

    def test_top_k_alerts_are_most_severe(self, pipeline):
        bloom, threat_db, alert_queue = pipeline
        for record in KNOWN_THREATS:
            process_packet(record.ip, bloom, threat_db, alert_queue)

        top2 = alert_queue.top_k(2)
        severities = [p for p, _ in top2]
        all_severities = sorted([r.severity for r in KNOWN_THREATS], reverse=True)
        assert severities == all_severities[:2]


# ---------------------------------------------------------------------------
# Full end-to-end pipeline scenarios
# ---------------------------------------------------------------------------


class TestFullPipeline:
    def test_benign_packet_produces_no_alert(self, pipeline):
        bloom, threat_db, alert_queue = pipeline
        triggered = process_packet("8.8.8.8", bloom, threat_db, alert_queue)
        assert triggered is False
        assert alert_queue.is_empty()

    def test_malicious_packet_produces_alert(self, pipeline):
        bloom, threat_db, alert_queue = pipeline
        triggered = process_packet("192.168.1.10", bloom, threat_db, alert_queue)
        assert triggered is True
        assert alert_queue.size() == 1

    def test_mixed_traffic_only_threats_enqueued(self, pipeline):
        bloom, threat_db, alert_queue = pipeline
        traffic = [
            "8.8.8.8",          # benign
            "192.168.1.10",     # malicious — severity 9
            "1.1.1.1",          # benign
            "10.0.0.200",       # malicious — severity 8
            "203.0.113.5",      # benign
            "172.16.0.3",       # malicious — severity 5
        ]
        for ip in traffic:
            process_packet(ip, bloom, threat_db, alert_queue)

        assert alert_queue.size() == 3
        priority, alert = alert_queue.pop()
        assert priority == 9
        assert alert.ip == "192.168.1.10"

    def test_high_throughput_stream(self, pipeline):
        """1 000 packets, 20 % malicious — all threats confirmed and queued."""
        bloom, threat_db, alert_queue = pipeline
        malicious_ips = [r.ip for r in KNOWN_THREATS]   # 5 IPs
        confirmed = 0
        for i in range(1000):
            ip = malicious_ips[i % len(malicious_ips)] if i % 5 == 0 else f"10.1.{i // 256}.{i % 256}"
            if process_packet(ip, bloom, threat_db, alert_queue):
                confirmed += 1

        assert confirmed == 200   # 1000 / 5 malicious packets
        assert alert_queue.size() == 200

    def test_pipeline_reset_and_reload(self, pipeline):
        """Clear all three stages and reload — pipeline must work identically."""
        bloom, threat_db, alert_queue = pipeline

        # Process once
        process_packet("192.168.1.10", bloom, threat_db, alert_queue)
        assert alert_queue.size() == 1

        # Reset
        bloom.clear()
        threat_db.clear()
        alert_queue.clear()

        assert bloom.is_empty()
        assert threat_db.is_empty()
        assert alert_queue.is_empty()

        # Reload
        for record in KNOWN_THREATS:
            bloom.add(record.ip)
            threat_db.put(record.ip, record)

        # Pipeline must work identically after reload
        triggered = process_packet("192.168.1.10", bloom, threat_db, alert_queue)
        assert triggered is True
        assert alert_queue.size() == 1

    def test_severity_ordering_across_all_threats(self, pipeline):
        """All 5 threats processed — alerts come out in strict severity order."""
        bloom, threat_db, alert_queue = pipeline
        for record in KNOWN_THREATS:
            process_packet(record.ip, bloom, threat_db, alert_queue)

        expected_order = sorted(KNOWN_THREATS, key=lambda r: r.severity, reverse=True)
        for expected in expected_order:
            priority, alert = alert_queue.pop()
            assert priority == expected.severity
            assert alert.ip == expected.ip
