# NotiFi 🔔
[![NotiFi](https://img.shields.io/badge/NotiFi-4287f-blue?style=flat-square)](https://notifi-4276f.web.app/)

NotiFi is a Automated Price Drop Notification Application.\
The tech stack used was **Python** and **Flask** in the back end to create my RESTful API, and **JavaScript/TypeScript** and **React with Redux** in the front end to create my client-facing UI. I used **PostgreSQL** to manage my database, and hosted the servers on **Heroku** for my back end and **Google Firebase** for my front end. Finally, I relied on **BeautifulSoup** to do my web-scraping.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install packages from requirements.txt file.

Windows
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
MacOS
```bash
python3 -m venv venv
venv/bin/activate
pip3 install -r requirements.txt
```

## Usage
Make sure you set your ENV variables in your .env file

The `FLASK_APP` should be False in production. This variable does not need to be declared in production.\
The `FLASK_DEBUG` should be False in production.\
The `SECRET_KEY` should be a random string.\
The `DATABASE_URL` is the connection string to your database.\
The `FRONTEND_URL` should be wherever you host your client server. Probably http://localhost:5173\
The `GOOGLE_APP_PASSWORD` is you App Password from your Google Account dashboard to send SMTP emails\
The `GOOGLE_EMAIL_SENDER` is the account which you want to send your notification emails from.

```.env
FLASK_APP=run.py
FLASK_DEBUG=True
SECRET_KEY=1234
DATABASE_URL=
FRONTEND_URL=
GOOGLE_APP_PASSWORD=
GOOGLE_EMAIL_SENDER=
```
In order to run the flask backend server, you first need to initialize your database.\
This command only needs to be run once at the beginning.
```bash
flask db init
flask db migrate
flask db upgrade
```

Finally, you are ready to run the server with the command:

```bash
flask run
```

All you need to do is run your Vite-React frontend application and it should begin making requests to this server.

## About the Project

- ### A brief discussion of any challenges faced and how they were overcome
    There were several challenges. The main one was being able to consistently web scrape price information off of Amazon's website. I noticed that they had several measures to try and block robots from scanning their sites. First, I ran into HTTP `503 Service Unavailable`, which I was able to work around by adding a `User-Agent` header. Then I ran into issues thinking it was because they were dynamically adding content after the initial load. I thought I would have to resort to using something more heavy weight like Selenium but somehow my request started going through after a night of sleeping on it, so I was able to just use BeautifulSoup. Some of the URL links are inconsistent and have multiple prices. I am still figuring out the perfect way to grab the price every time.\
\
Another challenge I faced was actually notifying the users about the price drop. I wanted to use a 3rd party service for both Emailing and SMS messaging. I tried going with Twilio and SendGrid but they have a long process to get approved to use their services, and their customer service was unresponsive. Also, as of late 2023, there are some stricter federal regulations (US A2P 10DLC Regulations) to combat spam auto messaging, which makes using SMS a lot harder for a quick project like this. From my understanding, You need to be approved with a business identification number, so I pivoted to simply using SMTP emailing with my own Gmail.

- ### Any additional features implemented beyond the basic requirements and / or any extension to the project that is desired
    - First, I expanded on the original prompt and allowed users to track more than just an iPad. They can search through Amazon and can "subscribe" to any product(s) that they want to.
    - Next, I provided users with the option to pick their method of alert (email or SMS or both). This works in my sandbox environment but SMS is not working in production as I will need to go through the approval process afore mentioned.
    - I implemented caching to the queries / API calls made from the client to server to optimized speeds and avoid unnecessary requests.
    - Also, I incorporated the use of JWT tokens to authenticate users, allowing people to use the application at scale to handle authentication. 
    - Finally, I illustrated the history of price changes using a Multi Line Chart. All notifications logs are saved into a SQL database for admin use. 

- ### Any details on testing performed as part of the project to ensure the project meets the requirements
    - I wrote basic unit tests utilizing Python's unittest framework to ensure the API endpoints function as expected.