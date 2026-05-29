import re
import json


def extract_event_schema(html: str) -> dict:
    schema_data = {}

    for block in _find_json_ld_blocks(html):
        data = _parse_json_ld(block)
        if not data:
            continue

        event = _find_event(data)
        if event:
            _extract_fields(event, schema_data)
            if 'page_schema' not in schema_data:
                schema_data['page_schema'] = json.dumps(event)

    return schema_data


def _find_json_ld_blocks(html: str) -> list[str]:
    pattern = r'<script type="application/ld\+json"[^>]*>(.*?)</script>'
    return re.findall(pattern, html, re.DOTALL | re.IGNORECASE)


def _parse_json_ld(block: str) -> dict | None:
    try:
        return json.loads(block.strip())
    except json.JSONDecodeError:
        return None


EVENT_TYPES = {"Event", "MusicEvent"}


def _is_event_type(tag) -> bool:
    if isinstance(tag, str):
        return tag in EVENT_TYPES
    if isinstance(tag, list):
        return any(t in EVENT_TYPES for t in tag)
    return False


def _find_event(data) -> dict | None:
    if isinstance(data, dict):
        if _is_event_type(data.get('@type')):
            return data
        if '@graph' in data:
            for item in data['@graph']:
                if isinstance(item, dict) and _is_event_type(item.get('@type')):
                    return item
    elif isinstance(data, list):
        for item in data:
            result = _find_event(item)
            if result:
                return result

    return None


def _extract_fields(event: dict, schema_data: dict) -> None:
    if event.get('startDate'):
        schema_data['start_date'] = _parse_date(event['startDate'])
    if event.get('endDate'):
        schema_data['end_date'] = _parse_date(event['endDate'])

    image = event.get('image')
    if image:
        if isinstance(image, dict):
            schema_data['image_url'] = image.get('url')
        elif isinstance(image, str):
            schema_data['image_url'] = image

    if event.get('description'):
        schema_data['description'] = event['description']

    event_type = event.get('@type')
    if isinstance(event_type, list):
        event_type = event_type[0] if event_type else None
    if event_type == 'MusicEvent':
        schema_data['event_type'] = 'live_music'

    offers = event.get('offers')
    if offers:
        prices = _extract_prices(offers)
        if prices:
            schema_data['price_range'] = prices


def _parse_date(date_str: str) -> str:
    if 'T' in date_str:
        return date_str.split('T')[0]
    return date_str


def _extract_prices(offers) -> str | None:
    prices = []

    if isinstance(offers, dict):
        offers = [offers]

    for offer in offers:
        if isinstance(offer, dict):
            try:
                if 'lowPrice' in offer:
                    prices.append(float(offer['lowPrice']))
                if 'highPrice' in offer:
                    prices.append(float(offer['highPrice']))
                if 'price' in offer:
                    prices.append(float(offer['price']))
            except (ValueError, TypeError):
                pass

    if not prices:
        return None

    low = min(prices)
    high = max(prices)
    if low == high and low == 0:
        return "Free"
    elif low == high:
        return f"${low:.2f}"
    return f"${low:.2f} - ${high:.2f}"
