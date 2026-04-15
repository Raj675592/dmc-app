# Signals and Circuits Web App

This is a Streamlit-based web application for signal and circuit analysis and prediction.

## Live Demo

[Access the live app here](https://dmc-web-app-bynxlkmy3m78nwxftbjby8.streamlit.app/)

> **Replace the above link with your actual Streamlit Cloud deployment URL after deploying.**

## Features

- Upload and analyze signals
- Circuit prediction using a trained model
- Simple and interactive web interface

## Getting Started

### Local Development

1. Clone the repository:
   ```sh
   git clone https://github.com/Raj675592/dmc-web-app.git
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Run the app:
   ```sh
   streamlit run app.py
   ```

### Deploy on Streamlit Community Cloud

1. Push your code to GitHub (public repo).
2. Go to [Streamlit Community Cloud](https://share.streamlit.io/).
3. Sign in with GitHub and deploy your app by selecting this repository and `app.py` as the entry point.
4. After deployment, update the **Live Demo** link above with your app's URL.

## Project Structure

- `app.py` - Main Streamlit app
- `predict.py` - Prediction logic
- `model.pkl` - Trained model file
- `requirements.txt` - Python dependencies

## License

MIT License
