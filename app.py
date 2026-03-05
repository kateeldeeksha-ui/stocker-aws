from flask import Flask, render_template, request, redirect, url_for, flash, session
import uuid
import hashlib
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = "stocker_secret_2024"

# ── In-Memory Database (simulates DynamoDB) ────────────────────────────────────
USERS        = {}
STOCKS       = {}
PORTFOLIO    = {}
TRANSACTIONS = []

# ── Seed Sample Stocks ─────────────────────────────────────────────────────────
def seed_stocks():
    sample = [
        {"symbol":"AAPL",  "name":"Apple Inc.",       "price":182.45, "market_cap":"2.8T", "sector":"Technology",    "industry":"Consumer Electronics"},
        {"symbol":"GOOGL", "name":"Alphabet Inc.",     "price":175.20, "market_cap":"2.1T", "sector":"Technology",    "industry":"Internet Services"},
        {"symbol":"MSFT",  "name":"Microsoft Corp.",   "price":415.60, "market_cap":"3.1T", "sector":"Technology",    "industry":"Software"},
        {"symbol":"AMZN",  "name":"Amazon.com Inc.",   "price":185.30, "market_cap":"1.9T", "sector":"Consumer",      "industry":"E-Commerce"},
        {"symbol":"TSLA",  "name":"Tesla Inc.",        "price":245.80, "market_cap":"780B", "sector":"Automotive",    "industry":"Electric Vehicles"},
        {"symbol":"META",  "name":"Meta Platforms",    "price":520.10, "market_cap":"1.3T", "sector":"Technology",    "industry":"Social Media"},
        {"symbol":"NVDA",  "name":"NVIDIA Corp.",      "price":875.30, "market_cap":"2.1T", "sector":"Technology",    "industry":"Semiconductors"},
        {"symbol":"NFLX",  "name":"Netflix Inc.",      "price":680.50, "market_cap":"290B", "sector":"Entertainment", "industry":"Streaming"},
    ]
    for s in sample:
        sid = str(uuid.uuid4())
        STOCKS[sid] = {"id":sid, "date_added":datetime.utcnow().isoformat(), **s}

seed_stocks()

# Pre-load admin account
admin_id = str(uuid.uuid4())
USERS["admin@stocker.com"] = {
    "id":admin_id, "username":"Admin", "email":"admin@stocker.com",
    "password":hashlib.sha256("admin123".encode()).hexdigest(),
    "role":"admin", "is_active":True, "created_at":datetime.utcnow().isoformat()
}

# ── Helpers ────────────────────────────────────────────────────────────────────
def hash_password(p): return hashlib.sha256(p.encode()).hexdigest()
def get_user_by_email(e): return USERS.get(e.lower())
def get_stock_by_id(sid): return STOCKS.get(sid)
def get_all_stocks(): return list(STOCKS.values())
def get_traders(): return [u for u in USERS.values() if u['role']=='trader']

def get_user_portfolio(user_id):
    result = []
    for stock_id, item in PORTFOLIO.get(user_id, {}).items():
        stock = get_stock_by_id(stock_id)
        if stock:
            result.append({**item, "symbol":stock["symbol"], "name":stock["name"],
                           "price":stock["price"],
                           "market_value":round(stock["price"]*item["quantity"],2)})
    return result

def get_user_transactions(user_id):
    return [t for t in TRANSACTIONS if t['user_id']==user_id]

# ── Decorators ─────────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard_trader'))
        return f(*args, **kwargs)
    return decorated

# ── Routes ─────────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email    = request.form['email'].strip().lower()
        password = request.form['password']
        role     = request.form.get('role','trader')
        if get_user_by_email(email):
            flash('Email already registered.', 'danger')
            return render_template('signup.html')
        user_id = str(uuid.uuid4())
        USERS[email] = {"id":user_id, "username":username, "email":email,
                        "password":hash_password(password), "role":role,
                        "is_active":True, "created_at":datetime.utcnow().isoformat()}
        print(f"[SNS] New user: {username} ({email}) as {role}")
        flash('Account created! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email    = request.form['email'].strip().lower()
        password = request.form['password']
        user     = get_user_by_email(email)
        if user and user['password'] == hash_password(password):
            session['user_id']  = user['id']
            session['email']    = user['email']
            session['username'] = user['username']
            session['role']     = user.get('role','trader')
            print(f"[SNS] Login: {user['username']} ({email})")
            flash(f"Welcome back, {user['username']}!", 'success')
            return redirect(url_for('dashboard_admin') if session['role']=='admin' else url_for('dashboard_trader'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard/admin')
@login_required
@admin_required
def dashboard_admin():
    return render_template('dashboard_admin.html', stocks=get_all_stocks(),
                           traders=get_traders(), username=session.get('username'))

@app.route('/dashboard/trader')
@login_required
def dashboard_trader():
    return render_template('dashboard_trader.html', stocks=get_all_stocks(),
                           portfolio=get_user_portfolio(session['user_id']),
                           transactions=get_user_transactions(session['user_id']),
                           username=session.get('username'))

@app.route('/buy_stock', methods=['GET','POST'])
@login_required
def buy_stock_route():
    stocks = get_all_stocks()
    if request.method == 'POST':
        stock_id = request.form['stock_id']
        quantity = int(request.form['quantity'])
        stock    = get_stock_by_id(stock_id)
        if not stock:
            flash('Stock not found.', 'danger')
            return render_template('buy_stock.html', stocks=stocks)
        price   = stock['price']
        user_id = session['user_id']
        if user_id not in PORTFOLIO: PORTFOLIO[user_id] = {}
        if stock_id in PORTFOLIO[user_id]:
            h = PORTFOLIO[user_id][stock_id]
            nq = h['quantity'] + quantity
            PORTFOLIO[user_id][stock_id] = {**h, "quantity":nq,
                "average_price":round((h['average_price']*h['quantity']+price*quantity)/nq,4)}
        else:
            PORTFOLIO[user_id][stock_id] = {"id":str(uuid.uuid4()), "user_id":user_id,
                "stock_id":stock_id, "quantity":quantity, "average_price":price}
        TRANSACTIONS.append({"id":str(uuid.uuid4()), "user_id":user_id, "stock_id":stock_id,
            "action":"BUY", "price":price, "quantity":quantity, "status":"COMPLETED",
            "transaction_date":datetime.utcnow().isoformat()})
        print(f"[SNS] {session['username']} BUY {quantity}x {stock['symbol']} @ ${price}")
        flash(f"Bought {quantity} shares of {stock['symbol']} at ${price:.2f}!", 'success')
        return redirect(url_for('dashboard_trader'))
    return render_template('buy_stock.html', stocks=stocks)

@app.route('/sell_stock', methods=['GET','POST'])
@login_required
def sell_stock_route():
    portfolio = get_user_portfolio(session['user_id'])
    if request.method == 'POST':
        stock_id = request.form['stock_id']
        quantity = int(request.form['quantity'])
        stock    = get_stock_by_id(stock_id)
        user_id  = session['user_id']
        holding  = PORTFOLIO.get(user_id,{}).get(stock_id)
        if not holding or holding['quantity'] < quantity:
            flash('Not enough shares to sell.', 'danger')
            return render_template('sell_stock.html', portfolio=portfolio)
        price   = stock['price']
        new_qty = holding['quantity'] - quantity
        if new_qty == 0: del PORTFOLIO[user_id][stock_id]
        else: PORTFOLIO[user_id][stock_id]['quantity'] = new_qty
        TRANSACTIONS.append({"id":str(uuid.uuid4()), "user_id":user_id, "stock_id":stock_id,
            "action":"SELL", "price":price, "quantity":quantity, "status":"COMPLETED",
            "transaction_date":datetime.utcnow().isoformat()})
        print(f"[SNS] {session['username']} SELL {quantity}x {stock['symbol']} @ ${price}")
        flash(f"Sold {quantity} shares of {stock['symbol']} at ${price:.2f}!", 'success')
        return redirect(url_for('dashboard_trader'))
    return render_template('sell_stock.html', portfolio=portfolio)

@app.route('/admin/add_stock', methods=['POST'])
@login_required
@admin_required
def add_stock():
    sid = str(uuid.uuid4())
    STOCKS[sid] = {"id":sid, "symbol":request.form['symbol'].upper().strip(),
                   "name":request.form['name'].strip(), "price":float(request.form['price']),
                   "market_cap":request.form.get('market_cap',''), "sector":request.form.get('sector',''),
                   "industry":request.form.get('industry',''), "date_added":datetime.utcnow().isoformat()}
    flash(f"Stock {request.form['symbol'].upper()} added!", 'success')
    return redirect(url_for('dashboard_admin'))

@app.route('/admin/delete_trader/<trader_id>', methods=['POST'])
@login_required
@admin_required
def delete_trader(trader_id):
    email_to_del = next((e for e,u in USERS.items() if u['id']==trader_id), None)
    if email_to_del:
        del USERS[email_to_del]
        PORTFOLIO.pop(trader_id, None)
        flash('Trader deleted.', 'success')
    else:
        flash('Trader not found.', 'danger')
    return redirect(url_for('dashboard_admin'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
