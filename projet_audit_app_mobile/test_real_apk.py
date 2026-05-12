import requests
import os
from dotenv import load_dotenv

def download_real_apk():
    """Télécharge un APK réel pour les tests"""
    print('Téléchargement d\'un APK réel pour les tests...')
    
    # URL d\'un APK public de test
    test_apk_urls = [
        'https://github.com/obtainable/Android-InsecureBankv2/raw/master/InsecureBankv2.apk',
        'https://github.com/ashishb/Android-InsecureBank/releases/download/v1.0/InsecureBank.apk'
    ]
    
    for url in test_apk_urls:
        try:
            print(f'Tentative de téléchargement depuis: {url}')
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                apk_path = 'uploads/real_test_apk.apk'
                os.makedirs('uploads', exist_ok=True)
                
                with open(apk_path, 'wb') as f:
                    f.write(response.content)
                
                size = len(response.content)
                print(f'✅ APK réel téléchargé: {apk_path}')
                print(f'Taille: {size} bytes ({size/1024/1024:.1f} MB)')
                return apk_path
            else:
                print(f'❌ Erreur {response.status_code}')
        except Exception as e:
            print(f'❌ Erreur téléchargement: {e}')
    
    return None

if __name__ == "__main__":
    download_real_apk()
