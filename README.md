# Agro - Event Aggregator

## Setup

1. Create virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

3. Set environment variables:

    Create .env in the root of this repo with this template

    ```bash
    AGRO_ENV=
    AGRO_MYSQL_DATABASE=
    AGRO_MYSQL_HOST=
    AGRO_MYSQL_PORT=
    AGRO_MYSQL_USER=
    AGRO_MYSQL_PASSWORD=
    FIRECRAWL_API_KEY=""
    FIRECRAWL_LOCAL_API_URL=""
    FIRECRAWL_API_URL=""
    GEMINI_API_KEY=""
    OPENAI_API_KEY=""
    ```

## Usage

```bash
python agro.py get-new
python agro.py get-new --venue-id 1
python agro.py update
python agro.py update --venue-id 1
```
