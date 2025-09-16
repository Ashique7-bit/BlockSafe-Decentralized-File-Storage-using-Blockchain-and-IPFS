# BlockSafe-Decentralized-File-Storage-using-Blockchain-and-IPFS

![Blockchain](https://img.shields.io/badge/Blockchain-Immutable%20Ledger-brightgreen)
![IPFS](https://img.shields.io/badge/IPFS-Distributed%20Storage-orange)
![Security](https://img.shields.io/badge/Security-Tamper--Proof-red)

BlockSafe is a mini-project for my MCA 3rd semester. It’s a web app that uses Blockchain + IPFS for decentralized file storage. Files are stored on IPFS, while metadata with Proof-of-Work is recorded on blockchain, ensuring security, immutability, and easy upload/download via a simple web UI.

![Python](https://img.shields.io/badge/Python-3.9%2B-green)
![Flask](https://img.shields.io/badge/Flask-2.3.3-lightgrey)
![IPFS](https://img.shields.io/badge/IPFS-Integrated-orange)

## ✨ Features

- **Secure File Upload**: Upload files of any type or size through a clean web interface
- **Blockchain Metadata Storage**: File metadata (name, IPFS hash, timestamp) is stored on a custom blockchain
- **Easy File Download**: Download files by entering the IPFS hash; system restores original filename
- **Data Integrity Verification**: SHA-256 hashing ensures file integrity during download
- **Decentralized Storage**: Files are stored on IPFS network, eliminating single points of failure
- **Tamper-Proof Records**: Blockchain ensures metadata cannot be altered
- **User-Friendly Interface**: Modern, responsive web design with intuitive navigation

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- IPFS installed locally ([Install IPFS](https://docs.ipfs.io/install/))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/BlockSafe.git
   cd BlockSafe
   ```
2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Initialize IPFS (in a separate terminal)**
   ```bash
   ipfs init
   ipfs daemon
   ```
5. **Run the application**
   ```bash
   python app.py
   ```
6. **Access the application**
   Open your browser and go to http://localhost:5001
## 📋 Requirements
   The requirements.txt file contains:

   ```text
   Flask==2.3.3
   ipfshttpclient==0.8.0a2
   requests==2.31.0
   python-dotenv==1.0.0
   ```
### 📖 Usage
   ## Uploading a File
   - Navigate to the home page
   - Click on the upload area or drag and drop a file
   - Optionally enter your name
   - Click "Secure Upload to IPFS & Blockchain"
   - Save the IPFS hash that's displayed after upload

   ## Downloading a File
   - Enter the IPFS hash in the download section
   - Click "Download from IPFS"
   - The file will be downloaded with its original name

   ## 🏗️ System Architecture
   - Frontend: Flask web interface
   - Backend: Python Flask server
   - Storage: IPFS for decentralized storage
   - Ledger: Custom blockchain for metadata
   - Security: SHA-256 hashing

### 📁 Project Structure

```text
BlockSafe/
├── app.py                
├── blockchain.py          
├── config.py          
├── requirements.txt       
├── templates/            
│   ├── index.html         
│   ├── success.html      
│   ├── files.html        
│   ├── blockchain.html 
│   └── verify.html       
├── uploads/              
└── downloads/
```

### 🛠️ Technologies Used
- Backend: Python, Flask
- Frontend: HTML5, CSS3, JavaScript, Bootstrap
- Decentralized Storage: IPFS (InterPlanetary File System)
- Blockchain: Custom Python implementation with Proof-of-Work
- Cryptography: hashlib for SHA-256 hashing
- Styling: Custom CSS with glassmorphism design

### 📜 License
   This project is licensed under the MIT License - see the LICENSE file for details.

### 🙏 Acknowledgments
- This project was developed as part of the Master of Computer Applications program at APJ Abdul Kalam Technological University
- Thanks to the IPFS and Flask communities for their excellent tools and documentation
- Inspired by research in decentralized storage and blockchain technology

### 📞 Support
   If you have any questions or issues, please open an issue on GitHub or contact:
   - Name: Muhammed Ashique U K
   - Email: ashiqueuk123nyd@gmail.com
   - Institution: Government Engineering College, Thrissur
   - Course: Master of Computer Applications

<div align="center"> Made with ❤️ using Python, Flask, and IPFS </div> 
