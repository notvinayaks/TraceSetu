"""Run the synthetic functional suite and write auditable scenario outcomes."""

import hashlib
import json
import sys
import unittest
from dataclasses import replace
from pathlib import Path

from fixtures import ADDRESS, CHAIN, NATIVE, SERVICE, SUSPECT, TOKEN, WINDOW, detect, fixture, mutate_event
from method import Anchor, Event, trace_frontier


class RecordingResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.outcomes = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.outcomes.append({"test": test.id(), "outcome": "passed"})

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.outcomes.append({"test": test.id(), "outcome": "failed"})

    def addError(self, test, err):
        super().addError(test, err)
        self.outcomes.append({"test": test.id(), "outcome": "error"})


def scenarios():
    events, anchors, coverage = fixture()
    common = dict(chain=CHAIN, asset=TOKEN, start_address=SUSPECT, window=WINDOW, as_of=40)
    candidate = detect()
    incomplete = detect(coverage=replace(coverage, complete=False))
    excluded = {"synthetic:gas-role-source"}
    challenged = detect(excluded_sources=excluded)
    no_gas = [e for e in events if e.asset != NATIVE]
    donation = mutate_event(events, "gas-1", sender="SYNTHETIC_UNQUALIFIED_DONOR")
    relayer = [anchors[0], replace(anchors[1], role="shared_relayer")]
    conflict = anchors + [replace(anchors[0], anchor_id="conflict", service="SYNTHETIC_SERVICE_BETA")]
    temporal = mutate_event(events, "sweep-1", at=9)
    future = [anchors[0], replace(anchors[1], learned_at=41)]
    revisit_events = [
        Event("first-arrival", "tx-a", CHAIN, TOKEN, SUSPECT, ADDRESS, 1000, 1, 1),
        Event("forward", "tx-b", CHAIN, TOKEN, ADDRESS, "SYNTHETIC_TRANSIT", 1000, 2, 2),
        Event("return", "tx-c", CHAIN, TOKEN, "SYNTHETIC_TRANSIT", ADDRESS, 1000, 3, 3),
    ]
    later_custody = [Anchor("later-custody", CHAIN, ADDRESS, SERVICE, "deposit_address",
                            3, 100, 0, "synthetic:later-role", "fixture://later-role")]
    gas_only = [replace(anchors[0], role="gas_feeder"), anchors[1]]
    return {
        "three_isolated_cycles": candidate.to_dict(),
        "repeated_personal_payments_without_service_gas": detect(no_gas).to_dict(),
        "unqualified_gas_donation": detect(donation).to_dict(),
        "shared_relayer_without_service_feeder_role": detect(anchors=relayer).to_dict(),
        "incomplete_window": incomplete.to_dict(),
        "conflicting_service_anchors": detect(anchors=conflict).to_dict(),
        "temporal_reversal": detect(temporal).to_dict(),
        "future_identity_evidence_excluded": detect(anchors=future).to_dict(),
        "gas_source_excluded": challenged.to_dict(),
        "adversarial_full_pattern_imitation": {
            "observations": "identical_to_three_isolated_cycles",
            "alternative_hidden_reality": "customer_controls_address_and_receives_cooperating_service_feeder_gas",
            "detector_result": candidate.to_dict(),
            "can_this_rule_distinguish_control_from_pattern_alone": False,
            "interpretation": "unresolved_identifiability_limit_not_a_successful_ownership_classification",
        },
        "known_label_only_frontier": trace_frontier(events, anchors, mode="known_labels_only", **common),
        "candidate_hypothesis_frontier": trace_frontier(events, anchors, detections=[candidate], **common),
        "incomplete_boundary_frontier": trace_frontier(events, anchors, detections=[incomplete], **common),
        "source_excluded_frontier": trace_frontier(events, anchors, detections=[challenged],
                                                   excluded_sources=excluded, **common),
        "stale_candidate_after_anchor_removal_frontier": trace_frontier(events, [],
                                                                        detections=[candidate], **common),
        "time_varying_custody_revisit_frontier": trace_frontier(revisit_events, later_custody,
                                                                mode="known_labels_only", **common),
        "gas_feeder_only_role_frontier": trace_frontier(events, gas_only,
                                                        mode="known_labels_only", **common),
    }


def main():
    directory = Path(__file__).resolve().parent
    suite = unittest.defaultTestLoader.discover(str(directory), pattern="test_method.py")
    test_result = unittest.TextTestRunner(stream=sys.stderr, verbosity=1,
                                         resultclass=RecordingResult).run(suite)
    data = {
        "experiment": "TraceSetu proposed isolated account-based deposit-candidate reference",
        "version": 2,
        "status": "isolated_research_reference_not_integrated_into_mvp",
        "data_origin": "entirely_synthetic_no_real_addresses_or_identity_labels",
        "external_api_calls": 0,
        "real_world_precision_measured": False,
        "real_world_recall_measured": False,
        "synthetic_pass_rate_is_attribution_accuracy": False,
        "proven_ownership_outputs_allowed": False,
        "thresholds": {"minimum_cycles": 3, "minimum_token_units": 100,
                       "calibrated": False, "purpose": "toy_demonstration_policy_only"},
        "tests": {"run": test_result.testsRun, "failures": len(test_result.failures),
                  "errors": len(test_result.errors), "skipped": len(test_result.skipped),
                  "all_passed": test_result.wasSuccessful(), "outcomes": test_result.outcomes},
        "scenarios": scenarios(),
        "source_sha256": {name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
                          for name in ("method.py", "fixtures.py", "test_method.py", "run_experiment.py")},
    }
    destination = directory / "results.json"
    destination.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"results_file": str(destination), "tests_run": test_result.testsRun,
                      "all_passed": test_result.wasSuccessful(), "data_origin": "synthetic"}))
    return 0 if test_result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
