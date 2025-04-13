from flask import Flask, request, jsonify
import google.generativeai as genai

# Setup Gemini API
genai.configure(api_key="AIzaSyB-vDeXO84-0LJ4X_OPnGWKZeKniKkmcPU")  # Replace with your Gemini API Key
gemini_model = genai.GenerativeModel('gemini-1.5-pro')

app = Flask(__name__)

# ========================== PREDICT API ==============================
@app.route('/predict', methods=['POST'])
def predict_water_quality():
    data = request.json

    ph = data['pH']
    hardness = data['hardness']
    tds = data['TDS']
    turbidity = data['turbidity']

    # 🔍 Step 1: Predict Safe/Unsafe
    check_prompt = f"""
You are a water quality expert.

Given the following parameters:
- pH Level: {ph}
- Hardness: {hardness} mg/L
- TDS: {tds} ppm
- Turbidity: {turbidity} NTU

Just answer in **one word only**: "Safe" or "Unsafe" for drinking.
"""

    check_response = gemini_model.generate_content(check_prompt)
    status = check_response.text.strip().lower()

    # 🧠 Step 2: Based on result, decide response
    if "safe" in status:
        return jsonify({
            'status': "Safe",
            'message': "✅ Water is safe for drinking.",
            'explanation': None
        })

    else:
        # If Unsafe, generate full explanation
        reason = "One or more parameters are beyond safe drinking limits."

        explain_prompt = f"""
Analyze the water quality based on the following parameters:

🔹 **pH Level:** {ph}  
🔹 **Hardness:** {hardness} mg/L  
🔹 **Total Dissolved Solids (TDS):** {tds} ppm  
🔹 **Turbidity:** {turbidity} NTU  

The ML model has classified the water as **"Unsafe"** because:  
**"{reason}"**

### 📌 Required Response:
1️⃣ **Scientific Explanation:** Explain the role of each parameter in determining water quality and mention safe limits.  
2️⃣ **Detailed Analysis Based on Given Parameters:** Discuss the effect of the specific values provided.  
3️⃣ **Filtration Techniques for Improvement:** Suggest effective filtration methods tailored to the detected issues.  
4️⃣ **Preventive Measures to Maintain Water Quality:** List practical steps for ensuring long-term water safety.  
5️⃣ **Step-by-Step Water Purification Process:** Offer a clear, actionable guide to filtering and purifying the water.  
6️⃣ **Uses of Clean Water:** Mention common important uses of clean and safe water.
"""

        explanation_response = gemini_model.generate_content(explain_prompt)

        return jsonify({
            'status': "Unsafe",
            'message': "⚠️ Water is unsafe for drinking.",
            'explanation': explanation_response.text
        })

# ========================== CHATBOT API ==============================
@app.route('/chat', methods=['POST'])
def chat_with_bot():
    data = request.json
    user_message = data.get('message')

    if not user_message:
        return jsonify({'error': 'No message provided.'}), 400

    chat_prompt = f"""
You are a helpful water expert chatbot 💧.

Answer user questions related to water, drinking water safety, purification methods, water quality, health impacts, etc.

Be friendly and short. If question is not related to water, politely say:
"I can only help with water-related questions 💧🙂"

User: {user_message}
"""

    chat_response = gemini_model.generate_content(chat_prompt)

    return jsonify({
        'bot_response': chat_response.text.strip()
    })

# ========================== RUN ==============================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4002, debug=True)
