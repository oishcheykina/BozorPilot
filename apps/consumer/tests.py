from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from services.ai_product_selection_service import AIProductSelectionService


class AIProductSelectionServiceTests(SimpleTestCase):
    def setUp(self):
        self.service = AIProductSelectionService()

    @override_settings(ANTHROPIC_API_KEY="")
    def test_missing_key_returns_configuration_message(self):
        cards = [
            {
                "external": True,
                "item": {
                    "title": "Phone A",
                    "brand": "BrandA",
                    "category": "Phones",
                    "current_price": "900000",
                    "market_average": "1200000",
                    "seller_reliability": 90,
                },
            },
            {
                "external": True,
                "item": {
                    "title": "Phone B",
                    "brand": "BrandB",
                    "category": "Phones",
                    "current_price": "1150000",
                    "market_average": "1200000",
                    "seller_reliability": 80,
                },
            },
        ]

        result = self.service.pick_best(cards, query="phone")

        self.assertIsNone(result["best_index"])
        self.assertEqual(result["source"], "missing_api_key")

    @override_settings(ANTHROPIC_API_KEY="test-key")
    def test_claude_result_is_used_when_available(self):
        cards = [
            {"external": True, "item": {"title": "Phone A", "current_price": "900000", "market_average": "1200000"}},
            {"external": True, "item": {"title": "Phone B", "current_price": "850000", "market_average": "1100000"}},
        ]

        with patch.object(
            AIProductSelectionService,
            "_request_claude",
            return_value={
                "best_index": 1,
                "title": "Phone B",
                "reason": "Best balance.",
                "source": "claude",
                "used_ai": True,
            },
        ):
            result = self.service.pick_best(cards, query="phone")

        self.assertEqual(result["best_index"], 1)
        self.assertEqual(result["source"], "claude")
