import zipfile
import os

def create_minimal_apk():
    """Crée un APK minimal valide pour les tests"""
    print('Création d\'un APK minimal valide...')
    
    apk_path = 'uploads/minimal_valid.apk'
    os.makedirs('uploads', exist_ok=True)
    
    with zipfile.ZipFile(apk_path, 'w') as apk:
        # Ajouter un AndroidManifest.xml minimal
        manifest = '''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.test.app"
    android:versionCode="1"
    android:versionName="1.0">
    <application android:label="Test App">
        <activity android:name=".MainActivity">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>'''
        apk.writestr('AndroidManifest.xml', manifest.encode('utf-8'))
        
        # Ajouter un classes.dex vide (nécessaire pour un APK valide)
        dex_header = b'dex\x0356' + b'\x00' * 36 + b'\x70\x00\x00\x00' + b'\x00' * 8
        apk.writestr('classes.dex', dex_header)
        
        # Ajouter META-INF
        apk.writestr('META-INF/MANIFEST.MF', b'Manifest-Version: 1.0\n')
        apk.writestr('META-INF/CERT.SF', b'Signature-Version: 1.0\n')
        apk.writestr('META-INF/CERT.RSA', b'fake_cert_data')
    
    print(f'✅ APK minimal créé: {apk_path}')
    print(f'Taille: {os.path.getsize(apk_path)} bytes')
    return apk_path

if __name__ == "__main__":
    create_minimal_apk()
