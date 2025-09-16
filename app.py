from flask import Flask, render_template, request, redirect, url_for, send_file, flash, jsonify
import os
import json
import hashlib
import requests
from datetime import datetime
from werkzeug.utils import secure_filename
from blockchain import Blockchain, Block
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

# Initialize blockchain
blockchain = Blockchain()

# Custom IPFS client using requests
class IPFSClient:
    def __init__(self, host='127.0.0.1', port=5001):
        self.base_url = f'http://{host}:{port}/api/v0'
    
    def add(self, file_path):
        try:
            with open(file_path, 'rb') as file:
                files = {'file': file}
                response = requests.post(f'{self.base_url}/add', files=files)
                return response.json()
        except Exception as e:
            print(f"Error adding file to IPFS: {e}")
            return None
    
    def get(self, ipfs_hash, download_path):
        try:
            params = {'arg': ipfs_hash}
            response = requests.post(f'{self.base_url}/get', params=params, stream=True)
            
            # Ensure download directory exists
            os.makedirs(download_path, exist_ok=True)
            
            # Save the file
            output_path = os.path.join(download_path, ipfs_hash)
            with open(output_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
            
            return output_path
        except Exception as e:
            print(f"Error getting file from IPFS: {e}")
            return None

# Initialize IPFS client
ipfs_client = IPFSClient(Config.IPFS_HOST, Config.IPFS_PORT)

# Ensure upload and download directories exist
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(Config.DOWNLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    # Allow all file types
    return '.' in filename

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            try:
                # Save file temporarily
                filename = secure_filename(file.filename)
                file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
                file.save(file_path)
                
                # Upload to IPFS
                ipfs_result = ipfs_client.add(file_path)
                if not ipfs_result:
                    flash('Failed to upload to IPFS')
                    return redirect(request.url)
                
                ipfs_hash = ipfs_result['Hash']
                
                # Prepare metadata for blockchain
                file_metadata = {
                    "filename": filename,
                    "file_extension": filename.rsplit('.', 1)[1].lower() if '.' in filename else '',
                    "file_size": os.path.getsize(file_path),
                    "ipfs_hash": ipfs_hash,
                    "timestamp": str(datetime.now()),
                    "uploader": request.form.get('uploader', 'anonymous')
                }
                
                # Add to blockchain
                new_block = Block(
                    index=len(blockchain.chain),
                    timestamp=datetime.now(),
                    data=file_metadata,
                    previous_hash=blockchain.get_latest_block().hash
                )
                
                blockchain.add_block(new_block)
                
                # Clean up temporary file
                os.remove(file_path)
                
                return render_template('success.html', 
                                     ipfs_hash=ipfs_hash,
                                     filename=filename,
                                     block_index=new_block.index)
                
            except Exception as e:
                flash(f'Error uploading file: {str(e)}')
                return redirect(request.url)
        
        flash('Invalid file type')
        return redirect(request.url)
    
    # If it's a GET request, show the upload form
    return render_template('upload.html')

@app.route('/download', methods=['GET', 'POST'])
def download_file():
    if request.method == 'POST':
        ipfs_hash = request.form.get('ipfs_hash', '').strip()
        
        if not ipfs_hash:
            flash('Please enter an IPFS hash')
            return redirect(url_for('download_file'))
        
        try:
            # Get file metadata from blockchain
            file_data = blockchain.get_file_by_hash(ipfs_hash)
            if not file_data:
                flash('File not found in blockchain records')
                return redirect(url_for('download_file'))
            
            # Download from IPFS
            ipfs_file_path = ipfs_client.get(ipfs_hash, Config.DOWNLOAD_FOLDER)
            if not ipfs_file_path:
                flash('Failed to download file from IPFS')
                return redirect(url_for('download_file'))
            
            # The file will be saved with the IPFS hash as filename
            # Rename file to original name
            original_filename = file_data['filename']
            download_path = os.path.join(Config.DOWNLOAD_FOLDER, original_filename)
            
            if os.path.exists(ipfs_file_path):
                os.rename(ipfs_file_path, download_path)
                
                # Verify file integrity
                with open(download_path, 'rb') as f:
                    file_content = f.read()
                    calculated_hash = hashlib.sha256(file_content).hexdigest()
                    # You could compare this with stored hash if needed
                
                return send_file(
                    download_path,
                    as_attachment=True,
                    download_name=original_filename
                )
            else:
                flash('File not found in IPFS network')
                return redirect(url_for('download_file'))
                
        except Exception as e:
            flash(f'Error downloading file: {str(e)}')
            return redirect(url_for('download_file'))
    
    # If it's a GET request, show the download form
    return render_template('download.html')

@app.route('/files')
def list_files():
    files = blockchain.get_all_files()
    return render_template('files.html', files=files)

@app.route('/blockchain')
def view_blockchain():
    chain_data = blockchain.to_dict()
    return render_template('blockchain.html', chain=chain_data)

@app.route('/verify')
def verify_chain():
    is_valid = blockchain.is_chain_valid()
    return render_template('verify.html', is_valid=is_valid)

@app.route('/api/files', methods=['GET'])
def api_list_files():
    files = blockchain.get_all_files()
    return jsonify(files)

@app.route('/api/blockchain', methods=['GET'])
def api_blockchain():
    chain_data = blockchain.to_dict()
    return jsonify(chain_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)