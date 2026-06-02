import cv2
import numpy as np

ENERGY_MAPPING = {
    "happy": "yüksek",
    "angry": "yüksek",
    "surprised": "yüksek",
    "neutral": "orta",
    "disgusted": "orta",
    "sad": "düşük",
    "fearful": "düşük",
    "calm": "düşük"
}

DUYGU_ACIKLAMALARI = {
    "happy"    : "Neşeli ve enerjik görünüyorsun 😄",
    "sad"      : "Biraz hüzünlü görünüyorsun 😢",
    "angry"    : "Sinirli bir ruh halindesin 😠",
    "surprised": "Şaşkın görünüyorsun 😲",
    "fearful"  : "Endişeli görünüyorsun 😨",
    "disgusted": "Rahatsız bir ifaden var 😒",
    "neutral"  : "Sakin ve nötr görünüyorsun 😐",
    "calm"     : "Huzurlu ve rahat görünüyorsun 😌"
}

DUYGU_ETIKETLERI = {
    "happy"    : "Mutlu",
    "sad"      : "Hüzünlü",
    "angry"    : "Sinirli",
    "surprised": "Şaşkın",
    "fearful"  : "Endişeli",
    "disgusted": "Rahatsız",
    "neutral"  : "Nötr",
    "calm"     : "Sakin"
}

def analyze_emotion(image: np.ndarray) -> dict:
    """
    Verilen görüntü üzerinde yüz ifadesinden duygu analizi yapar.
    """
    try:
        from deepface import DeepFace
        # Parlaklık artırma (karanlık ortam için)
        img = cv2.convertScaleAbs(image, alpha=1.5, beta=30)
        
        # Minimum boyutlandırma
        h, w = img.shape[:2]
        if h < 224 or w < 224:
            scale = max(224.0 / h, 224.0 / w)
            img = cv2.resize(img, (int(w * scale), int(h * scale)))
        
        # detector fallback zinciri
        sonuc = None
        used_backend = "none"
        for backend in ["retinaface", "mtcnn", "opencv"]:
            try:
                sonuc = DeepFace.analyze(
                    img,
                    actions=["emotion"],
                    enforce_detection=False,
                    detector_backend=backend
                )
                used_backend = backend
                break
            except Exception as e:
                print(f"[DeepFace] {backend} failed: {e}")
                continue
                
        if not sonuc:
            raise ValueError("Tüm dedektörler başarısız oldu.")
            
        if isinstance(sonuc, list):
            sonuc = sonuc[0]
            
        duygular = sonuc.get("emotion", {})
        sirali = sorted(duygular.items(), key=lambda x: x[1], reverse=True)
        ana_duygu = sirali[0][0]
        guven = float(sirali[0][1]) / 100.0
        
        # Neutral bias düzeltmesi
        if ana_duygu == "neutral" and guven < 0.60 and len(sirali) > 1:
            ana_duygu = sirali[1][0]
            guven = float(sirali[1][1]) / 100.0
            
        tum_duygular = {k: float(v) / 100.0 for k, v in duygular.items()}
        guven = float(guven)
        
        yuz_algilandi = True
        if ana_duygu == "neutral" and guven < 0.4:
            yuz_algilandi = False
            
        enerji_seviyesi = ENERGY_MAPPING.get(ana_duygu, "orta")
        aciklama = DUYGU_ACIKLAMALARI.get(ana_duygu, "Tanımlanamayan duygu 😐")
        etiket = DUYGU_ETIKETLERI.get(ana_duygu, "Bilinmeyen")
        
        print(f"[DeepFace] detector: {used_backend}")
        print(f"[DeepFace] ana_duygu: {ana_duygu} guven: {guven:.2f}")
        
        return {
            "ana_duygu": ana_duygu,
            "etiket": etiket,
            "guven": guven,
            "tum_duygular": tum_duygular,
            "enerji_seviyesi": enerji_seviyesi,
            "aciklama": aciklama,
            "yuz_algilandi": yuz_algilandi
        }
        
    except Exception as e:
        print(f"[EmotionService] Hata: {e}")
        return {
            "ana_duygu": "neutral",
            "etiket": DUYGU_ETIKETLERI["neutral"],
            "guven": 1.0,
            "tum_duygular": {"neutral": 1.0},
            "enerji_seviyesi": ENERGY_MAPPING["neutral"],
            "aciklama": DUYGU_ACIKLAMALARI["neutral"],
            "yuz_algilandi": False
        }
