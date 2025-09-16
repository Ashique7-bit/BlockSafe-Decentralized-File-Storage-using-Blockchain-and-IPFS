# BlockSafe-Decentralized-File-Storage-using-Blockchain-and-IPFS
BlockSafe is a mini-project for my MCA 3rd semester. It’s a web app that uses Blockchain + IPFS for decentralized file storage. Files are stored on IPFS, while metadata with Proof-of-Work is recorded on blockchain, ensuring security, immutability, and easy upload/download via a simple web UI.

# BlockSafe: Decentralized File Storage

BlockSafe is a secure and user-friendly decentralized file storage solution that combines the power of blockchain technology with the distributed nature of IPFS. It ensures that files remain safe, accessible, and verifiable at all times.

![BlockSafe](https://img.shields.io/badge/BlockSafe-Decentralized_Storage-blue)
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

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- IPFS installed locally ([Install IPFS](https://docs.ipfs.io/install/))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/BlockSafe.git
   cd BlockSafe
