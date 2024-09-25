The backend and fetch code for https://stocksinseconds.com/

Backend coded in python Flask to create api routes.
Used microsoft msal for authentication.
Hosted on Amazon Web Services (AWS) using lambda functions and API Gateway. Deployed automatically to these with zappa.
Database is NoSql AWS DynamoDB beecause it had a generous forever free tier. Connected through the backend instead of frontend directly to keep secure.

Frontend uses hostinger to design and host the website so the startup owners could design easily. Added embeded code with pure html, javascript, and css to connect with the backend.
