import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv

from utils.image_utils import decode_base64_image, validate_image
from services.emotion_service import analyze_emotion
from services.spotify_service import muzik_oner, TUR_MAP

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response


@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Kullanıcı görüntüsünü analiz eder ve Türkçe Spotify sonuçları döner.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"basari": False, "hata": "JSON verisi bulunamadı"}), 400
            
        base64_img = data.get("image")
        tur = data.get("tur", "pop") # Artık 'genre' yerine 'tur' bekleniyor
        
        # Geriye dönük uyumluluk (Frontend hala 'genre' atıyorsa)
        if "genre" in data and not "tur" in data:
            tur = data.get("genre")
            
        if not base64_img:
            return jsonify({"basari": False, "hata": "Görüntü bulunamadı"}), 400
            
        try:
            img_matrix = decode_base64_image(base64_img)
        except ValueError as e:
            return jsonify({"basari": False, "hata": str(e)}), 400
            
        if not validate_image(img_matrix):
            return jsonify({"basari": False, "hata": "Görüntü geçersiz veya çok küçük"}), 400
            
        # 1. Duygu Analizi
        duygu_sonucu = analyze_emotion(img_matrix)
        
        # 2. Spotify Önerileri
        parcalar = muzik_oner(duygu=duygu_sonucu["ana_duygu"], tur=tur)
        
        return jsonify({
            "basari": True,
            "duygu": duygu_sonucu,
            "parcalar": parcalar
        })
        
    except Exception as e:
        print(f"[App] Beklenmeyen hata: {e}")
        return jsonify({"basari": False, "hata": "Sunucu içi hata oluştu."}), 500

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "durum": "ok",
        "uygulama": "Moodify",
        "deepface": True,
        "spotify": True
    })

@app.route("/genres", methods=["GET"])
def get_genres():
    return jsonify({
        "basari": True,
        "turler": list(TUR_MAP.keys())
    })

if __name__ == "__main__":
    PORT = int(os.getenv("FLASK_PORT", 5000))
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
