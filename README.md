# Rural Education (SIH 2025)

A lightweight Flutter application designed to digitalize the rural education system. This project was developed for the **Smart India Hackathon 2025**.

## 🚀 Features

- **Authentication & User Management**
  - Secure login using Firebase Authentication.
  - Google Sign-In support.

- **Digital Classroom Tools**
  - **Timetable Management**: Organized scheduling for classes.
  - **PDF Tools**: Generate, view, and print PDF documents directly from the app.
  - **Connectivity Smart**: Optimized for areas with intermittent internet (`connectivity_plus`).

- **Smart Utilities**
  - **QR Code System**: Generate and scan QR codes for attendance or resource sharing.
  - **OCR & Photomath**: Built-in camera integration with ML Kit for text recognition and solving math problems.
  - **Wi-Fi & Local Info**: Access local network information.

## 🛠️ Tech Stack

- **Framework**: [Flutter](https://flutter.dev/)
- **Backend**: Firebase (Core, Auth)
- **ML & AI**: Google ML Kit (Text Recognition, Digital Ink)
- **State & Utilities**: `provider` (implied), `shared_preferences`, `http`

## 📦 Dependencies

This project relies on several key packages:
- `firebase_auth` & `google_sign_in` for security.
- `pdf`, `printing`, & `pdfx` for document handling.
- `mobile_scanner` & `qr_flutter` for QR operations.
- `google_mlkit_text_recognition` & `math_expressions` for the AI solver.

## 🏁 Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/MasterJi27/SIH2025.git
