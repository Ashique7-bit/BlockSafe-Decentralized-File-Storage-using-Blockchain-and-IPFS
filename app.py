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
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"IPFS Add Error: {response.status_code}")
                    return None
        except Exception as e:
            print(f"Error adding file to IPFS: {e}")
            return None
    
    def get(self, ipfs_hash, download_path):
        try:
            # Ensure download directory exists
            os.makedirs(download_path, exist_ok=True)
            
            # IPFS get command
            params = {'arg': ipfs_hash}
            response = requests.post(f'{self.base_url}/get', params=params, stream=True)
            
            if response.status_code == 200:
                # IPFS saves files in a folder named after the hash
                ipfs_folder = os.path.join(download_path, ipfs_hash)
                os.makedirs(ipfs_folder, exist_ok=True)
                
                # The actual file will be inside this folder
                output_path = os.path.join(ipfs_folder, ipfs_hash)
                
                with open(output_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file.write(chunk)
                
                # Find the actual file in the IPFS directory
                for file_in_dir in os.listdir(ipfs_folder):
                    file_path = os.path.join(ipfs_folder, file_in_dir)
                    if os.path.isfile(file_path) and file_in_dir != ipfs_hash:
                        return file_path
                
                return output_path
            else:
                print(f"IPFS Get Error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error getting file from IPFS: {e}")
            return None

# Initialize IPFS client
ipfs_client = IPFSClient(Config.IPFS_HOST, Config.IPFS_PORT)

# Ensure upload and download directories exist
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(Config.DOWNLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
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
                    flash('Failed to upload to IPFS. Make sure IPFS daemon is running.')
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
                flash('Error: This IPFS hash is not registered in the blockchain')
                return redirect(url_for('download_file'))
            
            # Download from IPFS
            ipfs_file_path = ipfs_client.get(ipfs_hash, Config.DOWNLOAD_FOLDER)
            if not ipfs_file_path:
                flash('Error: File not found on IPFS network')
                return redirect(url_for('download_file'))
            
            # The file will be saved with the IPFS hash as filename
            # Rename file to original name
            original_filename = file_data['filename']
            download_path = os.path.join(Config.DOWNLOAD_FOLDER, original_filename)
            
            if os.path.exists(ipfs_file_path):
                # Copy the file to preserve the original in IPFS folder
                import shutil
                shutil.copy2(ipfs_file_path, download_path)
                
                # Simple file existence check instead of hash comparison
                if os.path.exists(download_path) and os.path.getsize(download_path) > 0:
                    return send_file(
                        download_path,
                        as_attachment=True,
                        download_name=original_filename
                    )
                else:
                    flash('Error: Downloaded file is empty or could not be saved')
                    return redirect(url_for('download_file'))
            else:
                flash('Error: File could not be retrieved from IPFS')
                return redirect(url_for('download_file'))
                
        except Exception as e:
            flash(f'Error downloading file: {str(e)}')
            return redirect(url_for('download_file'))
    
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
    is_valid, errors, details = blockchain.validate_chain()
    return render_template('verify.html', is_valid=is_valid, errors=errors, details=details)

@app.route('/api/files', methods=['GET'])
def api_list_files():
    files = blockchain.get_all_files()
    return jsonify(files)

@app.route('/api/blockchain', methods=['GET'])
def api_blockchain():
    chain_data = blockchain.to_dict()
    return jsonify(chain_data)

# DEMONSTRATION ROUTES - Add these to your existing app.py

@app.route('/demo/tamper-block')
def demo_tamper_block():
    """
    Create a realistic tampering scenario for demonstration
    """
    # Ensure we have enough blocks to demonstrate
    if len(blockchain.chain) <= 1:
        # Add some demo files if blockchain is empty
        demo_files = [
            {
                "filename": "research_paper.pdf", 
                "ipfs_hash": "QmResearchPaper123", 
                "timestamp": str(datetime.now()),
                "file_size": 2048000,
                "uploader": "professor_smith"
            },
            {
                "filename": "project_data.xlsx", 
                "ipfs_hash": "QmProjectData456", 
                "timestamp": str(datetime.now()),
                "file_size": 1024000,
                "uploader": "student_john"
            }
        ]
        
        for file_data in demo_files:
            block = Block(
                index=len(blockchain.chain),
                timestamp=datetime.now(),
                data=file_data,
                previous_hash=blockchain.get_latest_block().hash
            )
            blockchain.add_block(block)
    
    # Now simulate tampering on the most recent block
    if len(blockchain.chain) > 1:
        target_block = blockchain.chain[-1]  # Get the last block
        
        # Store original values for demonstration
        original_filename = target_block.data['filename']
        original_size = target_block.data['file_size']
        
        # Simulate tampering by creating a modified copy (not affecting real data)
        # For demonstration, we'll actually modify the block but in a controlled way
        target_block.data = target_block.data.copy()  # Work with a copy
        target_block.data['filename'] = "malicious_software.exe"
        target_block.data['file_size'] = 999999999
        target_block.data['uploader'] = "unknown_hacker"
        
        # Break the hash to simulate tampering detection
        # In a real attack, the hash would become invalid when data changes
        # We'll simulate this by modifying the hash field directly for demo purposes
        original_hash = target_block.hash
        target_block.hash = "0000TAMPERED_HASH_DEMO"
        
        flash(f'Demo: Block #{target_block.index} tampered! Changed "{original_filename}" to "malicious_software.exe"')
    
    return redirect(url_for('verify_chain'))

@app.route('/demo/corrupt-chain')
def demo_corrupt_chain():
    """
    Simulate a broken blockchain chain for demonstration
    """
    if len(blockchain.chain) > 2:
        # Break the chain by modifying a middle block's previous_hash
        tamper_block = blockchain.chain[2]
        tamper_block.previous_hash = "BROKEN_CHAIN_LINK_123"
        
        flash('Demo: Blockchain chain broken! Previous hash reference corrupted.')
    
    return redirect(url_for('verify_chain'))

@app.route('/demo/invalid-pow')
def demo_invalid_pow():
    """
    Simulate invalid proof-of-work for demonstration
    """
    if len(blockchain.chain) > 1:
        # Create a block with invalid proof-of-work
        tamper_block = blockchain.chain[-1]
        tamper_block.hash = "000INVALID_POW_HASH"  # Doesn't start with enough zeros
        
        flash('Demo: Invalid proof-of-work detected! Hash does not meet difficulty requirement.')
    
    return redirect(url_for('verify_chain'))

@app.route('/demo/reset-demo')
def demo_reset():
    """
    Reset the blockchain to a valid state after demonstration
    """
    global blockchain
    
    # Reinitialize with a clean blockchain
    blockchain = Blockchain()
    
    # Add some demo files for presentation
    demo_files = [
        {
            "filename": "important_document.pdf", 
            "ipfs_hash": "QmValidHash1", 
            "timestamp": str(datetime.now()),
            "file_size": 1048576,
            "uploader": "demo_user"
        },
        {
            "filename": "project_report.docx", 
            "ipfs_hash": "QmValidHash2", 
            "timestamp": str(datetime.now()),
            "file_size": 2097152,
            "uploader": "demo_user"
        }
    ]
    
    for file_data in demo_files:
        block = Block(
            index=len(blockchain.chain),
            timestamp=datetime.now(),
            data=file_data,
            previous_hash=blockchain.get_latest_block().hash
        )
        blockchain.add_block(block)
    
    flash('Blockchain reset to valid state for demonstration')
    return redirect(url_for('verify_chain'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)