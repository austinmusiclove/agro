# Agro - Event Aggregator

## Environment Variables

Create .env in the root of this repo with this template

export AGRO_MYSQL_DATABASE=
export AGRO_MYSQL_HOST=
export AGRO_MYSQL_PORT=
export AGRO_MYSQL_USER=
export AGRO_MYSQL_PASSWORD=
export AGRO_LLM_PROVIDER=
export GEMINI_API_KEY=

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
   ```bash
   export AGRO_MYSQL_HOST=localhost
   export AGRO_MYSQL_PORT=3306
   export AGRO_MYSQL_USER=root
   export AGRO_MYSQL_PASSWORD=your_password
   export AGRO_MYSQL_DATABASE=agro
   ```

## Usage

```bash
python agro.py get-new
python agro.py get-new --venue-id 1
python agro.py update
python agro.py update --venue-id 1
```
