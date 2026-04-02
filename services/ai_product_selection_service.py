import json
import re
from decimal import Decimal, InvalidOperation
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings


class AIProductSelectionService:
    def pick_best(self, cards, query=""):
        candidates = self._build_candidates(cards)
        if not candidates:
            return None

        if len(candidates) == 1:
            candidate = candidates[0]
            return {
                "best_index": candidate["index"],
                "title": candidate["title"],
                "reason": "Filtrlashdan keyin faqat bitta mahsulot qoldi, shu sabab u avtomatik ravishda eng yaxshi variant bo'ldi.",
                "source": "single_result",
                "used_ai": False,
            }

        if not settings.ANTHROPIC_API_KEY:
            return {
                "best_index": None,
                "title": "",
                "reason": "Claude token hali sozlanmagan.",
                "source": "missing_api_key",
                "used_ai": False,
            }

        ai_result = self._request_claude(candidates, query=query)
        if ai_result:
            return ai_result

        return {
            "best_index": None,
            "title": "",
            "reason": "Claude so'rovi muvaffaqiyatsiz tugadi.",
            "source": "ai_error",
            "used_ai": False,
            "error_detail": "Noma'lum xato.",
        }

    def _build_candidates(self, cards):
        candidates = []
        for index, card in enumerate(cards):
            if card.get("external"):
                item = card["item"]
                price = self._to_decimal(item.get("current_price"))
                market_average = self._to_decimal(item.get("market_average") or price)
                candidates.append({
                    "index": index,
                    "title": item.get("title") or "Unknown product",
                    "brand": item.get("brand") or "",
                    "model": item.get("model") or "",
                    "description": item.get("description") or "",
                    "category": item.get("category") or "",
                    "price": str(price),
                    "market_average": str(market_average),
                    "seller_reliability": int(item.get("seller_reliability") or 0),
                    "platform": item.get("platform") or "",
                    "location": item.get("location") or "",
                })
                continue

            product = card["product"]
            analytics = card.get("analytics")
            best_price = self._to_decimal(card.get("best_price"))
            market_average = self._to_decimal(getattr(analytics, "market_average", best_price) or best_price)
            candidates.append({
                "index": index,
                "title": product.title,
                "brand": product.brand or "",
                "model": product.model_name or "",
                "description": product.description or "",
                "category": getattr(product.category, "name", ""),
                "price": str(best_price),
                "market_average": str(market_average),
                "seller_reliability": int(product.seller_reliability or 0),
                "platform": "Bozor Pilot AI",
                "location": product.location or "",
            })
        return candidates

    def _request_claude(self, candidates, query=""):
        payload = {
            "model": settings.ANTHROPIC_MODEL,
            "max_tokens": settings.ANTHROPIC_MAX_TOKENS,
            "temperature": 0.2,
            "system": (
                "Siz allaqachon filtrlangan marketplace mahsulotlarini tahlil qilasiz va "
                "narx-sifat nisbati bo'yicha eng yaxshi bitta variantni tanlaysiz. "
                "Narx, brend, model, tavsif sifati va sotuvchi ishonchliligini solishtiring. "
                "Faqat JSON qaytaring va unda best_index hamda reason kalitlari bo'lsin. "
                "reason matni faqat o'zbek tilida bo'lsin. "
                "best_index albatta berilgan kandidat indekslaridan biri bo'lsin."
            ),
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(
                                {
                                    "query": query,
                                    "task": "Filtrlangan ro'yxatdan narx va sifat bo'yicha eng yaxshi mahsulotni tanlang.",
                                    "candidates": candidates,
                                },
                                ensure_ascii=False,
                            ),
                        }
                    ],
                }
            ],
        }
        request = Request(
            settings.ANTHROPIC_API_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-api-key": settings.ANTHROPIC_API_KEY,
                "anthropic-version": settings.ANTHROPIC_API_VERSION,
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=20) as response:
                raw = response.read().decode("utf-8")
            parsed = json.loads(raw)
            message = parsed["content"][0]["text"]
            content = self._parse_json_message(message)
        except HTTPError as exc:
            return self._build_error_result(f"HTTP {exc.code}: {self._read_http_error(exc)}")
        except URLError as exc:
            return self._build_error_result(f"Tarmoq xatosi: {exc.reason}")
        except TimeoutError:
            return self._build_error_result("Claude javobi kutish vaqtidan oshib ketdi.")
        except (ValueError, KeyError, IndexError, json.JSONDecodeError):
            return self._build_error_result("Claude javobini JSON ko'rinishida o'qib bo'lmadi.")

        if not isinstance(content, dict):
            return self._build_error_result("Claude javobi kutilgan formatda emas.")

        best_index = content.get("best_index")
        reason = (content.get("reason") or "").strip()
        valid_indexes = {candidate["index"] for candidate in candidates}
        if best_index not in valid_indexes:
            return self._build_error_result("Claude mavjud bo'lmagan product indeksini qaytardi.")

        selected = next(candidate for candidate in candidates if candidate["index"] == best_index)
        return {
            "best_index": best_index,
            "title": selected["title"],
            "reason": reason or "Claude bu mahsulotni narx va sifat muvozanati bo'yicha eng yaxshi deb tanladi.",
            "source": "claude",
            "used_ai": True,
        }

    def _parse_json_message(self, message):
        try:
            return json.loads(message)
        except json.JSONDecodeError:
            fenced_match = re.search(r"```json\s*(\{.*?\})\s*```", message, re.DOTALL)
            if fenced_match:
                return json.loads(fenced_match.group(1))
            object_match = re.search(r"(\{.*\})", message, re.DOTALL)
            if object_match:
                return json.loads(object_match.group(1))
            return None

    def _build_error_result(self, detail):
        return {
            "best_index": None,
            "title": "",
            "reason": "Claude so'rovi muvaffaqiyatsiz tugadi.",
            "source": "ai_error",
            "used_ai": False,
            "error_detail": str(detail)[:300],
        }

    def _read_http_error(self, error):
        try:
            body = error.read().decode("utf-8")
            payload = json.loads(body)
            if isinstance(payload, dict):
                error_payload = payload.get("error", {})
                if isinstance(error_payload, dict):
                    message = error_payload.get("message")
                    if message:
                        return message
            return body[:300]
        except (OSError, ValueError, json.JSONDecodeError):
            return "HTTP javob tanasini o'qib bo'lmadi."

    def _to_decimal(self, value):
        try:
            return Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            return Decimal("0")
