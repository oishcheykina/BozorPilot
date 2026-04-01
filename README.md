# Bozor Pilot AI

Investor-demo-grade Django MVP for Uzbekistan market price intelligence.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations accounts core
python manage.py migrate
python manage.py seed_demo_data
python manage.py createsuperuser
python manage.py runserver
```

## Demo accounts

- `consumer@bozorpilot.ai` / `demo12345`
- `business@bozorpilot.ai` / `demo12345`

## Integration notes

- Replace mock category sync logic in `services/soliq_service.py` with official classifier API logic.
- Replace local mock pricing ingestion with partner or marketplace import logic in `services/market_data_service.py`.
- Extend deterministic rules in `services/analytics_service.py` and `services/recommendation_service.py` before adding optional LLM enrichments.
