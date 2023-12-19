This app does the following:

1. Queries email (that supports the jmap standard) to check for an Daily Income Trader email with a stock pick
2. Parses the email, and extracts information needed to place an order
3. Sanity checks the info to make sure it is reasonable
3. Writes information to a database (unless it already exists)
4. A separate process reads from the database, places and order, then marks the order as submitted

Installation Instructions

1. Setup Python:

a. brew install pyenv
b. pyenv install 3.12.0
c. Follow instructions here to update shell: https://www.freecodecamp.org/news/python-version-on-mac-update/
d. Start a new shell
e. pyenv global 3.9.2

2. Install postgres
a. brew install postgresql

3. Setup database env variables
* DIT_DB_NAME=
* DIT_DB_USERNAME=
* DIT_DB_PASSWORD=

4. Setup Database (replace DIT_DB_USERNAME and DIT_DB_PASSWORD and DIT_DB_NAME with actual values)
a. psql postgres
b. CREATE ROLE DIT_DB_USERNAME WITH LOGIN PASSWORD 'DIT_DB_PASSWORD';
c. CREATE DATABASE DIT_DB_NAME;
d. GRANT ALL PRIVILEGES ON DATABASE DIT_DB_NAME TO DIT_DB_USERNAME;

4. Install pip libraries

a. pip install --upgrade pip
b. pip install jmapc
c. pip install django
d. pip install setuptools

5. Setup the following environment variables (Examples given for fastmail):

* JMAP_HOST=api.fastmail.com
* JMAP_API_TOKEN_DIT= (your fastmail token)
* JMAP_FOLDER_NAME_DIT= (the folder name to check)

6. Apply database migrations:
a. python manage.py migrate

7. Download and setup twsapi
a. Download: https://interactivebrokers.github.io/#
b. Install and Setup: https://ibkrcampus.com/ibkr-api-page/trader-workstation-api/ 

==============

To create a new model/migration:
1. Add model to db/models.py
2. Run: python manage.py makemigrations db

To apply migration:
1. Run: python manage.py migrate
