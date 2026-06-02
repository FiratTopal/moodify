import os
import random
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

DUYGU_ARAMA_TERIMLERI_EN = {
    "happy"    : ["feel good", "happy vibes", "upbeat"],
    "sad"      : ["sad songs", "heartbreak", "emotional"],
    "angry"    : ["rage", "aggressive", "hard rock"],
    "surprised": ["epic", "unexpected", "wow"],
    "fearful"  : ["dark ambient", "tense", "eerie"],
    "disgusted": ["punk", "grunge", "dark"],
    "neutral"  : ["chill vibes", "lo fi", "background"],
    "calm"     : ["relaxing", "meditation", "peaceful"]
}

DUYGU_ARAMA_TERIMLERI_TR = {
    "happy"    : ["mutlu", "neşeli", "eğlenceli"],
    "sad"      : ["hüzünlü", "damar", "duygusal", "ağlatan"],
    "angry"    : ["öfkeli", "agresif", "sert"],
    "surprised": ["epik", "şaşırtıcı", "heyecanlı"],
    "fearful"  : ["karanlık", "gerilim", "korku"],
    "disgusted": ["isyankar", "alternatif", "punk"],
    "neutral"  : ["sakin", "arka plan", "lo-fi türkçe"],
    "calm"     : ["huzurlu", "dinlendirici", "akustik"]
}

TUR_MAP = {
    "türkçe pop" : "turkish",
    "türkçe"     : "turkish",
    "pop"        : "pop",
    "rock"       : "rock",
    "caz"        : "jazz",
    "klasik"     : "classical",
    "elektronik" : "electronic",
    "hip-hop"    : "hip-hop",
    "r&b"        : "r-n-b",
    "indie"      : "indie",
    "metal"      : "metal",
    "blues"      : "blues"
}

def muzik_oner(duygu: str, tur: str, limit: int = 10) -> list:
    """
    Get Spotify track recommendations based on emotion and genre using fallback search logic.
    """
    try:
        # Check credentials
        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        
        if not client_id or not client_secret:
            print("[Spotify] Kimlik bilgileri eksik (Credentials missing)")
            return []
            
        auth_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        sp = spotipy.Spotify(auth_manager=auth_manager)
        
        en_terim = random.choice(DUYGU_ARAMA_TERIMLERI_EN.get(duygu.lower(), ["chill"]))
        tr_terim = random.choice(DUYGU_ARAMA_TERIMLERI_TR.get(duygu.lower(), ["türkçe pop"]))
        tur_mapped = TUR_MAP.get(tur.lower(), "pop")
        
        half_limit = max(1, limit // 2)
        
        # İngilizce arama
        q_en = f"{en_terim} genre:{tur_mapped}"
        res_en = sp.search(q=q_en, type="track", limit=half_limit)
        tracks_en = res_en.get("tracks", {}).get("items", [])
        if not tracks_en:
            tracks_en = sp.search(q=en_terim, type="track", limit=half_limit).get("tracks", {}).get("items", [])
            
        # Türkçe arama
        q_tr = f"{tr_terim} genre:{tur_mapped}" if tur_mapped != "turkish" else tr_terim
        res_tr = sp.search(q=q_tr, type="track", limit=half_limit)
        tracks_tr = res_tr.get("tracks", {}).get("items", [])
        if not tracks_tr:
            tracks_tr = sp.search(q=tr_terim, type="track", limit=half_limit).get("tracks", {}).get("items", [])
            
        parcalar = []
        for i in range(max(len(tracks_en), len(tracks_tr))):
            if i < len(tracks_tr): parcalar.append(tracks_tr[i])
            if i < len(tracks_en): parcalar.append(tracks_en[i])
            
        print(f"[Spotify] Bulunan toplam parça sayısı: {len(parcalar)} (TR: {len(tracks_tr)}, EN: {len(tracks_en)})")
        
        return [
            {
                "isim"         : p.get("name"),
                "sanatci"      : p.get("artists", [{}])[0].get("name") if p.get("artists") else "Bilinmeyen Sanatçı",
                "album"        : p.get("album", {}).get("name"),
                "onizleme_url" : p.get("preview_url"),
                "spotify_url"  : p.get("external_urls", {}).get("spotify"),
                "kapak_url"    : p.get("album", {}).get("images", [{}])[0].get("url") if p.get("album", {}).get("images") else None
            }
            for p in parcalar
        ]
        
    except Exception as e:
        print(f"[SpotifyService] Hata: {e}")
        return []
