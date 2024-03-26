# Daily Income Trader

## Overview

### dit-email-to-order.py:

1. Queries email (that supports the jmap standard) to check for an Daily Income Trader email with a stock pick
2. Parses the email, and extracts information needed to place an order
3. Sanity checks the info to make sure it is reasonable
4. Writes information to a database (unless it already exists)

### dit-order-to-tws.py:

4. Reads from the database, places and order, then marks the order as submitted

## Setup

1. Setup Python 3 with asdf: https://rednafi.com/python/install_python_with_asdf/

2. Install postgres
a. brew install postgresql

3. Setup environment variables
- DIT_DB_NAME=
- DIT_DB_USERNAME=
- DIT_DB_PASSWORD=
- JMAP_HOST=api.fastmail.com
- JMAP_API_TOKEN_DIT= (your fastmail token)
- JMAP_FOLDER_NAME_DIT= (the folder name to check)
- TWS_PAPER_ACCOUNT_NAME_DIT=
- TWS_LIVE_ACCOUNT_NAME_DIT=

4. Setup Database (replace DIT_DB_USERNAME and DIT_DB_PASSWORD and DIT_DB_NAME with actual values)
a. psql postgres
b. CREATE ROLE DIT_DB_USERNAME WITH LOGIN PASSWORD 'DIT_DB_PASSWORD';
c. CREATE DATABASE DIT_DB_NAME;
d. GRANT ALL PRIVILEGES ON DATABASE DIT_DB_NAME TO DIT_DB_USERNAME;

5. Install pip libraries
a. pip install --upgrade pip
b. pip install jmapc
c. pip install django
d. pip install setuptools
e. pip install ib_insync

6. Apply database migrations:
a. python manage.py migrate

7. Setup TWS
a. Install Offline TWS Stable Version (Offline version needed for IBC)
b. Configure TWS for trading: https://ibkrcampus.com/ibkr-api-page/trader-workstation-api/#tws-config
c. Download and configure IBC: https://github.com/IbcAlpha/IBC

## Misc

### Database

This project uses the django ORM.

To create a new model/migration:
1. Add model to db/models.py
2. Run: python manage.py makemigrations db

To apply migration:
1. Run: python manage.py migrate
