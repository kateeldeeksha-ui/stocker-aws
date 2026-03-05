# Stocker AWS

Stocker AWS is a simple stock trading web application built using **Python Flask**.  
The application allows users to register, log in, and simulate buying and selling stocks.  
It provides separate dashboards for administrators and traders.

The system uses an **in-memory data structure to simulate a database**, and includes AWS setup scripts for future cloud integration.

## Features
- User signup and login system
- Admin dashboard
- Trader dashboard
- View available stocks
- Buy stocks
- Sell stocks
- Transaction tracking
- Simple UI using HTML and CSS

## Project Structure

stocker-aws/
│
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
│
├── templates/              # HTML templates
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   ├── dashboard_admin.html
│   ├── dashboard_trader.html
│   ├── buy_stock.html
│   └── sell_stock.html
│
├── static/
│   └── css/
│       └── style.css
│
└── aws_setup/              # AWS setup scripts
    ├── create_tables.py
    └── create_sns.py

## Technologies Used
- Python
- Flask
- HTML
- CSS
- AWS (setup scripts included)

## Installation

1. Clone the repository

git clone https://github.com/kateeldeeksha-ui/stocker-aws.git

2. Navigate to the project folder

cd stocker-aws

3. Install dependencies

pip install -r requirements.txt

4. Run the application

python app.py

5. Open the browser and go to

http://127.0.0.1:5000/

## Author
Deeksha Kateel  
MCA Student
