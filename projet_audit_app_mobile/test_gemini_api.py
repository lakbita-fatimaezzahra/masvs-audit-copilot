import os
from dotenv import load_dotenv
import google.generativeai as genai

# Charger les variables d'environnement
load_dotenv()

# Test de l'API Gemini
api_key = os.environ.get("GEMINI_API_KEY")
print(f"Clé API trouvée: {'Oui' if api_key else 'Non'}")

if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Test simple
        response = model.generate_content("Test simple: réponds par 'API fonctionne'")
        print(f"✅ Test API réussi: {response.text}")
        
    except Exception as e:
        print(f"❌ Erreur API: {e}")
        error_msg = str(e).lower()
        if 'quota' in error_msg or 'rate limit' in error_msg:
            print("📊 Problème de quota détecté")
        elif 'api' in error_msg and 'key' in error_msg:
            print("🔑 Problème de clé API")
else:
    print("❌ Aucune clé API trouvée")
