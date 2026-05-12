import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

def test_gemini():
    api_key = os.environ.get("GEMINI_API_KEY")
    print(f"--- Test de connexion Gemini ---")
    print(f"Clé trouvée : {'Oui' if api_key else 'Non'}")
    
    if not api_key:
        print("Erreur : GEMINI_API_KEY manquante dans le fichier .env")
        return

    try:
        genai.configure(api_key=api_key)
        
        print("Listing des modèles disponibles pour votre clé :")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f" - {m.name}")
        
        # Tentative avec gemini-2.5-flash
        print("\nTentative de connexion avec 'models/gemini-2.5-flash'...")
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content("Connexion test.")
        print(f"Réponse : {response.text.strip()}")
        print("--- Succès avec gemini-2.5-flash ! ---")
        
    except Exception as e:
        print(f"--- Test échoué ! ---")
        print(f"Erreur : {type(e).__name__}")
        print(f"Message : {str(e)}")

if __name__ == "__main__":
    test_gemini()
