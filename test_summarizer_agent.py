import io
import math
import unittest
from contextlib import redirect_stdout
from unittest.mock import Mock, patch

import summarizer_agent as agent


class ExecuteSummaryTests(unittest.TestCase):
    @patch("summarizer_agent.requests.get")
    def test_match_rejects_zero_before_network(self, get):
        with self.assertRaisesRegex(RuntimeError, "router treats zero as an absent ceiling"):
            agent.match_providers("https://example.test", "amk_test", 0)
        get.assert_not_called()

    @patch("summarizer_agent.requests.post")
    def test_execute_sends_bounded_one_shot_contract(self, post):
        response = Mock(status_code=200)
        response.json.return_value = {
            "status": "success",
            "output": {"summary": "short"},
            "receipt_id": "rcpt_test",
        }
        post.return_value = response

        result = agent.execute_summary(
            base_url="https://example.test/",
            api_key="amk_test",
            text="long text",
            max_cost=0.25,
            idempotency_key="summarize-test-1",
            payment_authorized=True,
        )

        self.assertEqual(result["receipt_id"], "rcpt_test")
        _, kwargs = post.call_args
        self.assertEqual(kwargs["json"]["constraints"], {"max_cost": 0.25})
        self.assertNotIn("idempotency_key", kwargs["json"])
        self.assertNotIn("Idempotency-Key", kwargs["headers"])

    @patch("summarizer_agent.requests.post")
    def test_paid_execute_fails_closed_without_authorization(self, post):
        with self.assertRaisesRegex(RuntimeError, "explicit payment authorization"):
            agent.execute_summary(
                "https://example.test",
                "amk_test",
                "text",
                0.01,
                "summarize-test-2",
            )
        post.assert_not_called()

    @patch("summarizer_agent.requests.post")
    def test_invalid_costs_fail_before_network(self, post):
        for value in (-0.01, 0, math.inf, math.nan):
            with self.subTest(value=value):
                with self.assertRaisesRegex(RuntimeError, "finite, positive"):
                    agent.execute_summary(
                        "https://example.test",
                        "amk_test",
                        "text",
                        value,
                        f"summarize-invalid-cost-{value}",
                        payment_authorized=True,
                    )
        post.assert_not_called()

    @patch("summarizer_agent.requests.post")
    def test_zero_cost_cannot_bypass_authorization(self, post):
        with self.assertRaisesRegex(RuntimeError, "deployed router treats zero"):
            agent.execute_summary(
                "https://example.test",
                "amk_test",
                "text",
                0,
                "summarize-zero",
                payment_authorized=False,
            )
        post.assert_not_called()

    @patch("summarizer_agent.requests.post")
    def test_idempotency_key_is_a_local_one_attempt_guard(self, post):
        response = Mock(status_code=200)
        response.json.return_value = {"status": "success"}
        post.return_value = response
        key = "summarize-local-guard"

        agent.execute_summary(
            "https://example.test", "amk_test", "text", 0.01, key, payment_authorized=True
        )
        with self.assertRaisesRegex(RuntimeError, "already attempted in this process"):
            agent.execute_summary(
                "https://example.test", "amk_test", "text", 0.01, key, payment_authorized=True
            )
        self.assertEqual(post.call_count, 1)

    @patch("summarizer_agent.requests.post")
    def test_invalid_idempotency_key_fails_before_network(self, post):
        with self.assertRaisesRegex(RuntimeError, "idempotency_key must be"):
            agent.execute_summary(
                "https://example.test",
                "amk_test",
                "text",
                0.01,
                "bad\nheader",
                payment_authorized=True,
            )
        post.assert_not_called()

    def test_print_result_surfaces_receipt_metadata_when_present(self):
        output = io.StringIO()
        with redirect_stdout(output):
            agent.print_result(
                {
                    "status": "success",
                    "provider": {"name": "Provider"},
                    "output": {"summary": "short"},
                    "receipt_id": "rcpt_test",
                    "receipt_url": "/receipts/rcpt_test",
                    "settlement": "settled",
                }
            )
        rendered = output.getvalue()
        self.assertIn("rcpt_test", rendered)
        self.assertIn("settled", rendered)


if __name__ == "__main__":
    unittest.main()
