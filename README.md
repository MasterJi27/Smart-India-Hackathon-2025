# Smart India Hackathon 2025

[![CI Pipeline](https://github.com/MasterJi27/Smart-India-Hackathon-2025/actions/workflows/ci.yml/badge.svg)](https://github.com/MasterJi27/Smart-India-Hackathon-2025/actions)

## 🏗️ System Architecture

\\\mermaid
graph TD
    User([User]) --> Web[Web Interface]
    Web --> API[Node.js API]
    API --> DB[(Database)]
    API --> QR[QR Generator Service]
\\\

## 🚀 Deployment

### Docker
\\\ash
docker build -t sih-2025 .
docker run -p 3000:3000 sih-2025
\\\

## 🛠️ Technical Stack
- **Frontend**: Flutter / React
- **Backend**: Node.js
- **CI/CD**: GitHub Actions
- **Containerization**: Docker
