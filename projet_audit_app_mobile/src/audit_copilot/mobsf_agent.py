import os
import json
import requests
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin
from .models import Finding

class MobSFAgent:
    """Agent pour communiquer avec l'API MOBSF et analyser des APK"""
    
    def __init__(self, mobsf_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        self.mobsf_url = mobsf_url.rstrip('/')
        self.api_key = api_key or os.getenv('MOBSF_API_KEY')
        self.session = requests.Session()
        self.session.headers.update({
            'X-Mobsf-Api-Key': self.api_key,
            'Content-Type': 'application/json'
        })
        
    def test_connection(self) -> bool:
        """Teste la connexion à MOBSF"""
        try:
            # Utiliser /api_docs pour tester la connexion (endpoint qui existe)
            response = requests.get(f"{self.mobsf_url}/api_docs", timeout=5)
            if response.status_code == 200:
                # Tester également la clé API avec un endpoint simple
                api_test = requests.post(f"{self.mobsf_url}/api/v1/upload", 
                                       headers={'X-Mobsf-Api-Key': self.api_key},
                                       timeout=5)
                return api_test.status_code != 401  # Pas d'erreur d'authentification
            return False
        except:
            return False
    
    def upload_apk(self, apk_path: str) -> Optional[str]:
        """Upload un APK vers MOBSF et retourne le hash du fichier"""
        try:
            with open(apk_path, 'rb') as f:
                files = {'file': (os.path.basename(apk_path), f, 'application/vnd.android.package-archive')}
                # Utiliser une requête directe sans session pour éviter les conflits de headers
                response = requests.post(
                    f"{self.mobsf_url}/api/v1/upload",
                    files=files,
                    headers={'X-Mobsf-Api-Key': self.api_key},
                    timeout=30
                )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('hash')
            else:
                print(f"Erreur upload: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Erreur upload APK: {e}")
            return None
    
    def start_scan(self, file_hash: str) -> bool:
        """Dans MOBSF, l'analyse démarre automatiquement après l'upload"""
        # MOBSF lance automatiquement l'analyse après l'upload
        # On retourne True pour indiquer que le processus est lancé
        print(f"📊 Analyse automatique démarrée pour {file_hash}")
        return True
    
    def get_scan_status(self, file_hash: str) -> Dict[str, Any]:
        """Vérifie le statut du scan"""
        try:
            response = self.session.get(
                f"{self.mobsf_url}/api/v1/scan",
                params={"hash": file_hash}
            )
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            print(f"Erreur vérification statut: {e}")
            return {}
    
    def wait_for_scan_completion(self, file_hash: str, timeout: int = 300) -> bool:
        """Attend la fin du scan avec timeout - approche robuste"""
        print(f"⏳ Attente de la fin de l'analyse (timeout: {timeout}s)...")
        start_time = time.time()
        
        # Attendre un peu pour que MOBSF traite l'upload
        time.sleep(10)
        
        # Vérifier plusieurs fois si le rapport est disponible
        for attempt in range(20):  # 20 tentatives max
            try:
                report = self.get_report_json(file_hash)
                if report:
                    print(f"✅ Analyse complétée en {attempt + 1} tentatives")
                    return True
                    
                print(f"⏳ Tentative {attempt + 1}/20 - Rapport pas encore disponible...")
                time.sleep(15)  # Attendre 15 secondes entre tentatives
                
            except Exception as e:
                print(f"⚠️ Erreur tentative {attempt + 1}: {e}")
                time.sleep(15)
                
            if time.time() - start_time > timeout:
                print(f"⏰ Timeout après {timeout} secondes")
                return False
                
        return False
    
    def get_report_json(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """Récupère le rapport d'analyse au format JSON"""
        try:
            response = self.session.get(
                f"{self.mobsf_url}/api/v1/report_json",
                params={"hash": file_hash}
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Erreur récupération rapport: {e}")
            return None
    
    def analyze_apk(self, apk_path: str, output_dir: str = "reports") -> List[Finding]:
        """Pipeline complet d'analyse d'APK"""
        findings = []
        
        # 1. Upload APK
        print(f"Upload de l'APK: {apk_path}")
        file_hash = self.upload_apk(apk_path)
        if not file_hash:
            return [Finding(
                source="MobSF-Agent",
                title="Erreur Upload APK",
                details="Impossible d'uploader l'APK vers MOBSF",
                severity="high",
                evidence={"error": "upload_failed"},
                tags=["mobsf", "error"]
            )]
        
        # 2. Démarrer le scan
        print(f"Démarrage du scan pour le hash: {file_hash}")
        if not self.start_scan(file_hash):
            return [Finding(
                source="MobSF-Agent",
                title="Erreur Scan APK",
                details="Impossible de démarrer l'analyse MOBSF",
                severity="high",
                evidence={"hash": file_hash, "error": "scan_start_failed"},
                tags=["mobsf", "error"]
            )]
        
        # 3. Attendre la fin du scan
        print("Attente de la fin de l'analyse...")
        if not self.wait_for_scan_completion(file_hash):
            return [Finding(
                source="MobSF-Agent",
                title="Timeout Scan",
                details="L'analyse MOBSF a dépassé le temps imparti",
                severity="medium",
                evidence={"hash": file_hash, "error": "timeout"},
                tags=["mobsf", "error"]
            )]
        
        # 4. Récupérer le rapport
        print("Récupération du rapport d'analyse...")
        report = self.get_report_json(file_hash)
        if not report:
            return [Finding(
                source="MobSF-Agent",
                title="Erreur Rapport",
                details="Impossible de récupérer le rapport MOBSF",
                severity="high",
                evidence={"hash": file_hash, "error": "report_failed"},
                tags=["mobsf", "error"]
            )]
        
        # 5. Sauvegarder le rapport brut
        report_path = Path(output_dir) / f"mobsf_report_{file_hash}.json"
        report_path.parent.mkdir(exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # 6. Ajouter un finding de succès
        findings.append(Finding(
            source="MobSF-Agent",
            title="Analyse MOBSF Complétée",
            details=f"APK analysé avec succès. Hash: {file_hash}",
            severity="info",
            evidence={"hash": file_hash, "report_path": str(report_path)},
            tags=["mobsf", "success"]
        ))
        
        return findings
    
    def get_full_report_for_pipeline(self, apk_path: str, output_dir: str = "reports") -> Optional[str]:
        """Méthode utilitaire pour intégration avec le pipeline existant"""
        findings = self.analyze_apk(apk_path, output_dir)
        
        # Vérifier si l'analyse a réussi
        error_findings = [f for f in findings if "error" in f.tags or f.severity == "high" and "Erreur" in f.title]
        if error_findings:
            return None
        
        # Trouver le chemin du rapport généré
        for finding in findings:
            if finding.evidence and "report_path" in finding.evidence:
                return finding.evidence["report_path"]
        
        return None
