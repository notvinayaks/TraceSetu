"""Functional/adversarial tests of a proposed rule, not attribution accuracy."""

import unittest
from dataclasses import replace

from fixtures import (ADDRESS, CHAIN, FEEDER, HOT, NATIVE, OTHER_CHAIN, SERVICE,
                      SUSPECT, TOKEN, WINDOW, detect, fixture, mutate_event)
from method import Anchor, Event, trace_frontier


class CandidateTests(unittest.TestCase):
    def assert_abstains(self, report, reason=None):
        self.assertEqual(report.status, "abstain")
        self.assertFalse(report.ownership_proven)
        self.assertIsNone(report.calibrated_probability)
        if reason:
            self.assertIn(reason, report.reasons)

    def test_three_complete_cycles_are_only_an_unconfirmed_hypothesis(self):
        report = detect()
        self.assertEqual(report.status, "heuristic_candidate")
        self.assertEqual(report.service, SERVICE)
        self.assertEqual(len(report.cycles), 3)
        self.assertFalse(report.ownership_proven)
        self.assertTrue(report.independent_confirmation_required)
        self.assertIsNone(report.calibrated_probability)

    def test_two_cycles_do_not_meet_toy_threshold(self):
        events, anchors, coverage = fixture()
        events = [e for e in events if e.at < 30]
        coverage = replace(coverage, closing_balances={TOKEN: 0, NATIVE: 180})
        self.assert_abstains(detect(events, anchors, coverage), "insufficient_complete_cycles_for_toy_policy")

    def test_repeated_personal_customer_payments_without_service_gas_do_not_qualify(self):
        events, anchors, coverage = fixture()
        events = [e for e in events if e.asset != NATIVE]
        self.assert_abstains(detect(events, anchors, coverage), "cycle_gas_funding_missing")

    def test_unqualified_gas_donation_does_not_qualify(self):
        events, _, _ = fixture()
        events = mutate_event(events, "gas-1", sender="SYNTHETIC_UNRELATED_DONOR")
        self.assert_abstains(detect(events), "source_qualified_service_gas_feeder_missing")

    def test_shared_relayer_is_not_a_service_gas_feeder_role(self):
        _, anchors, _ = fixture()
        anchors[1] = replace(anchors[1], role="shared_relayer")
        self.assert_abstains(detect(anchors=anchors), "source_qualified_service_gas_feeder_missing")

    def test_fully_imitated_pattern_is_indistinguishable_and_never_proves_ownership(self):
        # Same observations can describe a user-controlled wallet funded by a
        # cooperating/donating feeder and repeatedly paying an exchange.
        # No unobserved controller flag is available to a chain-pattern rule.
        report = detect()
        self.assertEqual(report.status, "heuristic_candidate")
        self.assertFalse(report.ownership_proven)
        self.assertTrue(report.independent_confirmation_required)

    def test_incomplete_history_abstains(self):
        _, _, coverage = fixture()
        self.assert_abstains(detect(coverage=replace(coverage, complete=False)),
                             "complete_all_activity_window_not_attested")

    def test_token_only_history_abstains(self):
        _, _, coverage = fixture()
        self.assert_abstains(detect(coverage=replace(coverage, all_native_token_receipts=False)),
                             "complete_all_activity_window_not_attested")

    def test_unestablished_token_semantics_abstain(self):
        _, _, coverage = fixture()
        self.assert_abstains(detect(coverage=replace(coverage, plain_token_semantics=False)),
                             "plain_nonrebasing_nonfee_token_semantics_not_established")

    def test_missing_opening_balance_abstains(self):
        _, _, coverage = fixture()
        self.assert_abstains(detect(coverage=replace(coverage, opening_balances={TOKEN: 0})),
                             "opening_token_and_native_balances_missing")

    def test_existing_balance_breaks_isolation(self):
        _, _, coverage = fixture()
        self.assert_abstains(detect(coverage=replace(coverage, opening_balances={TOKEN: 1, NATIVE: 0})),
                             "nonzero_or_invalid_opening_balance")

    def test_missing_receipt_does_not_establish_gas_payment(self):
        events, _, _ = fixture()
        self.assert_abstains(detect(mutate_event(events, "sweep-1", receipt_ref="")),
                             "direct_transfer_and_actual_gas_payment_not_established")

    def test_relayer_paid_sweep_does_not_establish_subject_gas_use(self):
        events, _, _ = fixture()
        events = mutate_event(events, "sweep-1", gas_payer="SYNTHETIC_RELAYER")
        self.assert_abstains(detect(events), "direct_transfer_and_actual_gas_payment_not_established")

    def test_allowance_spender_transaction_is_out_of_scope(self):
        events, _, _ = fixture()
        events = mutate_event(events, "sweep-1", tx_sender="SYNTHETIC_ALLOWANCE_SPENDER")
        self.assert_abstains(detect(events), "direct_transfer_and_actual_gas_payment_not_established")

    def test_native_funding_must_cover_observed_fee(self):
        events, _, _ = fixture()
        self.assert_abstains(detect(mutate_event(events, "sweep-1", fee_units=101)),
                             "observed_native_funding_cannot_cover_receipt_fee")

    def test_closing_balances_must_reconcile(self):
        _, _, coverage = fixture()
        self.assert_abstains(detect(coverage=replace(coverage, closing_balances={TOKEN: 0, NATIVE: 271})),
                             "observed_effects_do_not_reconcile_to_closing_balances")

    def test_gas_before_deposit_has_no_cycle_association_in_this_rule(self):
        events, _, _ = fixture()
        events = mutate_event(events, "gas-1", at=9, order=9)
        self.assert_abstains(detect(events), "gas_funding_not_uniquely_paired_with_pending_deposit")

    def test_hot_and_feeder_must_assert_same_service(self):
        _, anchors, _ = fixture()
        anchors[1] = replace(anchors[1], service="SYNTHETIC_OTHER_SERVICE")
        self.assert_abstains(detect(anchors=anchors), "hot_wallet_and_gas_feeder_services_disagree")

    def test_conflicting_hot_wallet_anchors_abstain(self):
        _, anchors, _ = fixture()
        anchors.append(replace(anchors[0], anchor_id="contradiction", service="SYNTHETIC_OTHER_SERVICE"))
        self.assert_abstains(detect(anchors=anchors), "conflicting_hot_wallet_service_anchors")

    def test_conflicting_feeder_anchors_abstain(self):
        _, anchors, _ = fixture()
        anchors.append(replace(anchors[1], anchor_id="contradiction", service="SYNTHETIC_OTHER_SERVICE"))
        self.assert_abstains(detect(anchors=anchors), "conflicting_gas_feeder_service_anchors")

    def test_conflict_across_hot_and_deposit_roles_is_not_hidden(self):
        _, anchors, _ = fixture()
        anchors.append(replace(anchors[0], anchor_id="other-role", role="deposit_address",
                               service="SYNTHETIC_OTHER_SERVICE"))
        self.assert_abstains(detect(anchors=anchors), "conflicting_hot_wallet_service_anchors")

    def test_conflict_across_feeder_and_hot_roles_is_not_hidden(self):
        _, anchors, _ = fixture()
        anchors.append(replace(anchors[1], anchor_id="other-role", role="hot_wallet",
                               service="SYNTHETIC_OTHER_SERVICE"))
        self.assert_abstains(detect(anchors=anchors), "conflicting_gas_feeder_service_anchors")

    def test_same_address_on_other_chain_cannot_supply_identity_anchor(self):
        _, anchors, _ = fixture()
        anchors = [replace(a, chain=OTHER_CHAIN) for a in anchors]
        self.assert_abstains(detect(anchors=anchors), "source_qualified_service_gas_feeder_missing")

    def test_other_chain_same_address_activity_does_not_contaminate_window(self):
        events, _, _ = fixture()
        events.append(Event("other-chain", "other-chain-tx", OTHER_CHAIN, "other-token",
                            "UNRELATED", ADDRESS, 1, 15, 15))
        self.assertEqual(detect(events).status, "heuristic_candidate")

    def test_expired_anchor_cannot_support_later_cycle(self):
        _, anchors, _ = fixture()
        anchors[1] = replace(anchors[1], valid_until=20)
        self.assert_abstains(detect(anchors=anchors), "source_qualified_service_gas_feeder_missing")

    def test_withdrawn_anchor_is_excluded_from_reanalysis(self):
        _, anchors, _ = fixture()
        anchors[1] = replace(anchors[1], withdrawn_at=35)
        self.assert_abstains(detect(anchors=anchors), "source_qualified_service_gas_feeder_missing")

    def test_future_learned_identity_evidence_cannot_leak_into_historical_evaluation(self):
        _, anchors, _ = fixture()
        anchors[1] = replace(anchors[1], learned_at=41)
        self.assert_abstains(detect(anchors=anchors), "source_qualified_service_gas_feeder_missing")

    def test_future_cycles_cannot_satisfy_earlier_window(self):
        events, anchors, coverage = fixture()
        coverage = replace(coverage, end=15, closing_balances={TOKEN: 0, NATIVE: 90})
        report = detect(events, anchors, coverage, window=(0, 15), as_of=15)
        self.assert_abstains(report, "insufficient_complete_cycles_for_toy_policy")
        self.assertEqual(len(report.cycles), 1)

    def test_source_exclusion_removes_support_without_overwriting_original(self):
        original = detect()
        challenged = detect(excluded_sources={"synthetic:gas-role-source"})
        self.assert_abstains(challenged, "source_qualified_service_gas_feeder_missing")
        self.assertEqual(original.status, "heuristic_candidate")

    def test_source_reference_is_mandatory(self):
        _, anchors, _ = fixture()
        anchors[1] = replace(anchors[1], evidence_ref="")
        self.assert_abstains(detect(anchors=anchors), "source_qualified_service_gas_feeder_missing")

    def test_inexact_sweep_does_not_qualify(self):
        events, _, _ = fixture()
        self.assert_abstains(detect(mutate_event(events, "sweep-1", units=999)),
                             "sweep_not_exact_integer_deposit_amount")

    def test_overlapping_incomings_do_not_qualify(self):
        events, _, _ = fixture()
        events.append(Event("extra-in", "extra-in-tx", CHAIN, TOKEN, "SOMEONE", ADDRESS, 1000, 11, 115))
        # Use consistent time/order sequence; third event falls before sweep.
        events = [replace(e, order=e.order * 10) if e.event_id != "extra-in" else e for e in events]
        self.assert_abstains(detect(events), "multiple_incomings_before_sweep")

    def test_mixed_token_asset_abstains(self):
        events, _, _ = fixture()
        events.append(Event("other-asset", "other-asset-tx", CHAIN, "OTHER_TOKEN",
                            "SOMEONE", ADDRESS, 500, 15, 15))
        self.assert_abstains(detect(events), "mixed_assets_or_other_outflows")

    def test_unexplained_native_outflow_abstains(self):
        events, _, _ = fixture()
        events.append(Event("native-out", "native-out-tx", CHAIN, NATIVE,
                            ADDRESS, "SOMEONE", 10, 15, 15))
        self.assert_abstains(detect(events), "native_outflow_not_supported")

    def test_positive_dust_is_not_silently_dropped_to_manufacture_isolation(self):
        events, _, _ = fixture()
        events.append(Event("dust", "dust-tx", CHAIN, TOKEN, "ATTACKER", ADDRESS, 1, 15, 15))
        self.assert_abstains(detect(events), "small_positive_transfer_breaks_isolation_policy")

    def test_zero_and_reverted_incomings_cannot_create_extra_cycles(self):
        events, _, _ = fixture()
        events += [Event("zero", "zero-tx", CHAIN, TOKEN, "ATTACKER", ADDRESS, 0, 15, 15),
                   Event("reverted", "reverted-tx", CHAIN, TOKEN, "ATTACKER", ADDRESS,
                         100000, 16, 16, success=False)]
        report = detect(events)
        self.assertEqual(report.status, "heuristic_candidate")
        self.assertEqual(len(report.cycles), 3)
        self.assertEqual(len(report.ignored_events), 2)

    def test_failed_deposit_does_not_count_as_received(self):
        events, _, _ = fixture()
        self.assert_abstains(detect(mutate_event(events, "deposit-1", success=False)),
                             "gas_funding_not_uniquely_paired_with_pending_deposit")

    def test_failed_outgoing_transaction_requires_more_accounting(self):
        events, _, _ = fixture()
        self.assert_abstains(detect(mutate_event(events, "sweep-1", success=False)),
                             "failed_outgoing_execution_not_supported")

    def test_float_amounts_are_not_accepted_as_exact_units(self):
        events, _, _ = fixture()
        self.assert_abstains(detect(mutate_event(events, "deposit-1", units=1000.0)),
                             "negative_or_noninteger_units")

    def test_temporal_reversal_abstains(self):
        events, _, _ = fixture()
        self.assert_abstains(detect(mutate_event(events, "sweep-1", at=9)),
                             "ledger_order_and_time_disagree")

    def test_duplicate_provider_event_is_not_a_second_observation(self):
        events, _, _ = fixture()
        events.append(events[0])
        self.assert_abstains(detect(events), "duplicate_or_ambiguous_event_id")

    def test_relabelled_duplicate_transaction_effect_abstains(self):
        events, _, _ = fixture()
        events.append(replace(events[0], event_id="same-tx-another-event", order=13, at=13))
        self.assert_abstains(detect(events), "multiple_relevant_effects_in_one_transaction")


class FrontierTests(unittest.TestCase):
    def trace(self, events=None, anchors=None, **kwargs):
        base_events, base_anchors, _ = fixture()
        parameters = dict(chain=CHAIN, asset=TOKEN, start_address=SUSPECT,
                          window=WINDOW, as_of=40)
        parameters.update(kwargs)
        return trace_frontier(base_events if events is None else events,
                              base_anchors if anchors is None else anchors, **parameters)

    def test_known_label_baseline_reaches_farther_hot_wallet_without_proving_nearestness(self):
        output = self.trace(mode="known_labels_only")
        self.assertTrue(output["stops"])
        self.assertTrue(all(s["address"] == HOT and s["hops"] == 2 for s in output["stops"]))
        self.assertTrue(all(ADDRESS in s["unlabelled_predecessors"] for s in output["stops"]))
        self.assertFalse(output["globally_nearest_service_proven"])

    def test_hypothesis_frontier_stops_before_farther_hot_wallet(self):
        output = self.trace(detections=[detect()])
        self.assertEqual(len(output["stops"]), 1)
        stop = output["stops"][0]
        self.assertEqual(stop["address"], ADDRESS)
        self.assertEqual(stop["hops"], 1)
        self.assertEqual(stop["status"], "provisional_custody_boundary")
        self.assertFalse(stop["ownership_proven"])

    def test_unknown_assessed_boundary_is_not_skipped_to_farther_hot_wallet(self):
        _, _, coverage = fixture()
        report = detect(coverage=replace(coverage, complete=False))
        output = self.trace(detections=[report])
        self.assertEqual(len(output["stops"]), 1)
        self.assertEqual(output["stops"][0]["status"], "unresolved_assessed_boundary")
        self.assertEqual(output["stops"][0]["address"], ADDRESS)

    def test_source_challenge_recomputes_and_stops_unresolved(self):
        excluded = {"synthetic:gas-role-source"}
        report = detect(excluded_sources=excluded)
        output = self.trace(detections=[report], excluded_sources=excluded)
        self.assertEqual(output["stops"][0]["status"], "unresolved_assessed_boundary")

    def test_stale_unchallenged_candidate_cannot_survive_source_exclusion(self):
        output = self.trace(detections=[detect()], excluded_sources={"synthetic:gas-role-source"})
        self.assertEqual(output["stops"][0]["status"], "unresolved_stale_or_mismatched_assessment")

    def test_removing_anchors_invalidates_precomputed_candidate(self):
        output = self.trace(anchors=[], detections=[detect()])
        self.assertEqual(len(output["stops"]), 1)
        self.assertEqual(output["stops"][0]["address"], ADDRESS)
        self.assertEqual(output["stops"][0]["status"], "unresolved_stale_or_mismatched_assessment")

    def test_changing_anchor_role_invalidates_precomputed_candidate(self):
        _, anchors, _ = fixture()
        anchors[1] = replace(anchors[1], role="shared_relayer")
        output = self.trace(anchors=anchors, detections=[detect()])
        self.assertEqual(output["stops"][0]["status"], "unresolved_stale_or_mismatched_assessment")

    def test_withdrawing_anchor_invalidates_precomputed_candidate(self):
        _, anchors, _ = fixture()
        anchors[1] = replace(anchors[1], withdrawn_at=35)
        output = self.trace(anchors=anchors, detections=[detect()])
        self.assertEqual(output["stops"][0]["status"], "unresolved_stale_or_mismatched_assessment")

    def test_changed_sweep_units_invalidate_precomputed_candidate(self):
        events, _, _ = fixture()
        events = mutate_event(events, "sweep-1", units=999)
        output = self.trace(events=events, detections=[detect()])
        self.assertEqual(output["stops"][0]["status"], "unresolved_stale_or_mismatched_assessment")

    def test_removed_cycle_invalidates_precomputed_candidate(self):
        events, _, _ = fixture()
        events = [e for e in events if e.at < 30]
        output = self.trace(events=events, detections=[detect()])
        self.assertEqual(output["stops"][0]["status"], "unresolved_stale_or_mismatched_assessment")

    def test_new_dust_transfer_invalidates_precomputed_candidate(self):
        events, _, _ = fixture()
        events.append(Event("dust", "dust-tx", CHAIN, TOKEN, "ATTACKER", ADDRESS, 1, 15, 15))
        output = self.trace(events=events, detections=[detect()])
        self.assertEqual(output["stops"][0]["status"], "unresolved_stale_or_mismatched_assessment")

    def test_input_reordering_keeps_same_evidence_snapshot(self):
        events, anchors, _ = fixture()
        original = detect()
        reordered = detect(list(reversed(events)), list(reversed(anchors)))
        self.assertEqual(original.evidence_snapshot_sha256, reordered.evidence_snapshot_sha256)
        output = self.trace(events=list(reversed(events)), anchors=list(reversed(anchors)),
                            detections=[original])
        self.assertEqual(output["stops"][0]["status"], "provisional_custody_boundary")

    def test_address_revisit_preserves_time_varying_custody_role(self):
        # D has no custody assertion at the first arrival, but acquires one
        # before the return. Address-only visited pruning loses this boundary.
        events = [
            Event("first-arrival", "tx-a", CHAIN, TOKEN, SUSPECT, ADDRESS, 1000, 1, 1),
            Event("forward", "tx-b", CHAIN, TOKEN, ADDRESS, "SYNTHETIC_TRANSIT", 1000, 2, 2),
            Event("return", "tx-c", CHAIN, TOKEN, "SYNTHETIC_TRANSIT", ADDRESS, 1000, 3, 3),
        ]
        anchors = [Anchor("later-custody", CHAIN, ADDRESS, SERVICE, "deposit_address",
                          3, 100, 0, "synthetic:later-role", "fixture://later-role")]
        output = self.trace(events=events, anchors=anchors, mode="known_labels_only")
        self.assertEqual(len(output["stops"]), 1)
        stop = output["stops"][0]
        self.assertEqual(stop["status"], "known_service_assertion")
        self.assertEqual(stop["address"], ADDRESS)
        self.assertEqual(stop["hops"], 3)
        self.assertEqual(stop["path_event_ids"], ["first-arrival", "forward", "return"])

    def test_address_cycles_cannot_reuse_events_or_escape_hop_bounds(self):
        events = [
            Event("first-arrival", "tx-a", CHAIN, TOKEN, SUSPECT, ADDRESS, 1000, 1, 1),
            Event("forward", "tx-b", CHAIN, TOKEN, ADDRESS, "SYNTHETIC_TRANSIT", 1000, 2, 2),
            Event("return", "tx-c", CHAIN, TOKEN, "SYNTHETIC_TRANSIT", ADDRESS, 1000, 3, 3),
            Event("forward-again", "tx-d", CHAIN, TOKEN, ADDRESS, "SYNTHETIC_TRANSIT", 1000, 4, 4),
        ]
        output = self.trace(events=events, anchors=[], mode="known_labels_only", max_hops=3)
        self.assertTrue(any(s["status"] == "unresolved_hop_limit" for s in output["stops"]))
        self.assertTrue(all(len(s["path_event_ids"]) <= 3 for s in output["stops"]))
        self.assertTrue(all(len(s["path_event_ids"]) == len(set(s["path_event_ids"]))
                            for s in output["stops"]))

    def test_never_trace_unrelated_withdrawals_inside_service(self):
        events, _, _ = fixture()
        events.append(Event("pooled-withdrawal", "pooled-withdrawal-tx", CHAIN, TOKEN,
                            HOT, "UNRELATED_CUSTOMER", 1000, 35, 35))
        output = self.trace(events, mode="known_labels_only")
        self.assertTrue(all(s["address"] == HOT for s in output["stops"]))
        self.assertTrue(all("pooled-withdrawal" not in s["path_event_ids"] for s in output["stops"]))

    def test_gas_feeder_role_stops_without_asserting_customer_deposit_acceptance(self):
        events, anchors, _ = fixture()
        anchors[0] = replace(anchors[0], role="gas_feeder")
        events.append(Event("service-out", "service-out-tx", CHAIN, TOKEN,
                            HOT, "SYNTHETIC_LATER_ADDRESS", 1000, 35, 35))
        output = self.trace(events=events, anchors=anchors, mode="known_labels_only")
        self.assertTrue(output["stops"])
        self.assertTrue(all(s["address"] == HOT for s in output["stops"]))
        self.assertTrue(all(s["status"] == "unresolved_service_controlled_non_deposit_role"
                            for s in output["stops"]))
        self.assertTrue(all(not s["deposit_acceptance_asserted"] for s in output["stops"]))
        self.assertTrue(all("service-out" not in s["path_event_ids"] for s in output["stops"]))

    def test_hot_wallet_assertion_alone_is_not_deposit_acceptance(self):
        output = self.trace(mode="known_labels_only")
        self.assertTrue(all(s["asserted_roles"] == ["hot_wallet"] for s in output["stops"]))
        self.assertTrue(all(not s["deposit_acceptance_asserted"] for s in output["stops"]))

    def test_backward_in_time_path_is_not_traversed(self):
        events, _, _ = fixture()
        events = [e for e in events if e.at < 20]
        events = mutate_event(events, "sweep-1", at=9)
        output = self.trace(events, mode="known_labels_only")
        self.assertEqual(output["stops"][0]["address"], ADDRESS)
        self.assertEqual(output["stops"][0]["status"], "unresolved_no_observed_continuation")

    def test_cross_chain_matching_address_is_not_a_path(self):
        events, _, _ = fixture()
        events = [replace(e, chain=OTHER_CHAIN) if e.sender == ADDRESS else e for e in events]
        output = self.trace(events, mode="known_labels_only")
        self.assertTrue(all(s["address"] != HOT for s in output["stops"]))

    def test_hop_limit_does_not_become_no_vasp_claim(self):
        output = self.trace(mode="known_labels_only", max_hops=1)
        self.assertEqual(output["stops"][0]["status"], "unresolved_hop_limit")
        self.assertFalse(output["globally_nearest_service_proven"])

    def test_state_budget_reports_unvisited_work(self):
        output = self.trace(mode="known_labels_only", max_states=1)
        self.assertTrue(output["truncated_by_state_budget"])
        self.assertGreater(output["unvisited_state_count"], 0)

    def test_conflicting_known_service_assertions_stop_unresolved(self):
        _, anchors, _ = fixture()
        anchors.append(replace(anchors[0], anchor_id="contradiction", service="SYNTHETIC_OTHER_SERVICE"))
        output = self.trace(anchors=anchors, mode="known_labels_only")
        self.assertTrue(all(s["status"] == "unresolved_conflicting_service_assertions" for s in output["stops"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
