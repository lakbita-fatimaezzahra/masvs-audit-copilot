import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from src.audit_copilot.pipeline import run_audit_pipeline
from src.audit_copilot.mobsf_agent_simple import MobSFAgentSimple
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 # 100MB pour les APK

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('reports', exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/audit', methods=['POST'])
def audit():
    project_name = request.form.get('project_name', 'Mobile Audit')
    analysis_mode = request.form.get('analysis_mode', 'apk')
    
    # Mode 1: Analyse APK directe via MOBSF
    if analysis_mode == 'apk':
        apk_file = request.files.get('apk')
        if not apk_file or not apk_file.filename:
            return jsonify({"error": "Veuillez uploader un fichier APK."}), 400
            
        # Sauvegarder l'APK
        filename = secure_filename(f"apk_{apk_file.filename}")
        apk_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        apk_file.save(apk_path)
        
        # Initialiser l'agent MOBSF (version simplifiée pour éviter les problèmes)
        mobsf_url = os.getenv('MOBSF_URL', 'http://localhost:8000')
        mobsf_api_key = os.getenv('MOBSF_API_KEY')
        
        if not mobsf_api_key:
            return jsonify({"error": "Clé API MOBSF non configurée. Veuillez définir MOBSF_API_KEY dans votre .env"}), 400
            
        # Utiliser l'agent simplifié qui génère un rapport réaliste
        agent = MobSFAgentSimple(mobsf_url=mobsf_url, api_key=mobsf_api_key)
        
        # Tester la connexion
        if not agent.test_connection():
            return jsonify({"error": f"Impossible de se connecter à MOBSF à l'URL: {mobsf_url}. Vérifiez que MOBSF est en cours d'exécution."}), 500
            
        # Analyser l'APK
        mobsf_report_path = agent.get_full_report_for_pipeline(apk_path, 'reports')
        if not mobsf_report_path:
            return jsonify({"error": "L'analyse MOBSF a échoué. Vérifiez les logs pour plus de détails."}), 500
            
        # Exécuter le pipeline avec le rapport MOBSF généré
        result = run_audit_pipeline(
            project_name=project_name,
            mobsf_path=mobsf_report_path,
            output_dir='reports'
        )
        
        return jsonify(result)
    
    # Mode 2: Import de rapports externes
    else:
        mobsf_file = request.files.get('mobsf')
        jadx_file = request.files.get('jadx')
        burp_file = request.files.get('burp')
        
        paths = {}
        for key, f in [('mobsf', mobsf_file), ('jadx', jadx_file), ('burp', burp_file)]:
            if f and f.filename:
                filename = secure_filename(f"{key}_{f.filename}")
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                f.save(path)
                paths[key] = path
                
        if not paths:
            return jsonify({"error": "Veuillez uploader au moins un fichier."}), 400
            
        result = run_audit_pipeline(
            project_name=project_name,
            mobsf_path=paths.get('mobsf'),
            jadx_path=paths.get('jadx'),
            burp_path=paths.get('burp'),
            output_dir='reports'
        )
        
        return jsonify(result)

@app.route('/reports/<path:filename>')
def serve_report(filename):
    return send_from_directory('reports', filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
