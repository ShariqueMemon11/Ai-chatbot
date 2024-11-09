import json
from difflib import get_close_matches
from typing import Optional
import requests

# Load and save functions for the knowledge base
def load_knowledge_base(file_path: str) -> dict:
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        # Ensure "coins" key exists in knowledge base
        if "coins" not in data:
            data["coins"] = {}
        return data
    except (FileNotFoundError, json.JSONDecodeError):
        # Initialize with "questions" and "coins" keys if file is missing or corrupt
        return {"questions": [], "coins": {}}

def save_knowledge_base(file_path: str, data: dict):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

# Similarity matching functions
def find_best_match(user_question: str, questions: list[str]) -> Optional[str]:
    matches = get_close_matches(user_question, questions, n=1, cutoff=0.6)
    return matches[0] if matches else None

def get_answer_for_question(question: str, knowledge_base: dict) -> Optional[str]:
    for q in knowledge_base["questions"]:
        if q["question"] == question:
            return q["answer"]
    return None

# CoinGecko API functions
def get_coin_id(coin_name: str) -> Optional[str]:
    try:
        url = "https://api.coingecko.com/api/v3/coins/list"
        response = requests.get(url)
        response.raise_for_status()
        coins_data = response.json()
        # Search by name or symbol (case-insensitive)
        for coin in coins_data:
            if coin['name'].lower() == coin_name.lower() or coin['symbol'].lower() == coin_name.lower():
                return coin['id']
    except requests.RequestException:
        print("Bot: Unable to connect to the internet.")
    return None

def get_coin_data(coin_id: str) -> Optional[dict]:
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None

def get_coin_price_history(coin_id: str, days: int = 7) -> Optional[list]:
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days={days}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data["prices"]
    except requests.RequestException:
        return None

def predict_trend(price_history: list) -> str:
    if len(price_history) < 2:
        return "Not enough data to make a prediction."
    
    # Calculate percentage change from the earliest to the latest price
    initial_price = price_history[0][1]
    latest_price = price_history[-1][1]
    percent_change = ((latest_price - initial_price) / initial_price) * 100
    
    if percent_change > 5:
        return "It looks like the coin might pump soon based on recent trends and analysis."
    elif percent_change < -5:
        return "It seems the coin might dump soon based on recent trends."
    else:
        return "The coin seems stable, with no significant trend detected."

# Main chat function with cryptocurrency integration
def chat_bot():
    file_path = 'knowledge_base.json'
    knowledge_base = load_knowledge_base(file_path)
    
    while True:
        user_input = input('You: ')
        if user_input.lower() == 'quit' or user_input.lower() == 'byy' or user_input.lower() == 'ok by':
            break
        
        # Check for cryptocurrency question
        if "price of" in user_input.lower() or "information about" in user_input.lower() or "prediction about" in user_input.lower() or "analysis about" in user_input.lower():
            coin_name = user_input.split("about")[-1].strip() if "about" in user_input.lower() else user_input.split("price of")[-1].strip()
            coin_id = get_coin_id(coin_name)
            latest_data = None
            
            # Try to fetch latest data if online
            if coin_id:
                latest_data = get_coin_data(coin_id)
                if latest_data:
                    price = latest_data['market_data']['current_price']['usd']
                    market_cap = latest_data['market_data']['market_cap']['usd']
                    liquidity = latest_data['market_data'].get('total_volume', {}).get('usd', 'N/A')
                    print(f"Bot: [Updated Data]\nName: {latest_data['name']},\nSymbol: {latest_data['symbol'].upper()},\nCurrent Price: ${price},\nMarket Cap: ${market_cap},\nLiquidity: ${liquidity}")
                    
                    # Fetch historical data and make a prediction
                    price_history = get_coin_price_history(coin_id)
                    prediction = predict_trend(price_history) if price_history else "No prediction available."
                    print(f"Bot: Prediction - {prediction}")
                    
                    # Save latest data to knowledge base
                    knowledge_base["coins"][coin_name] = {
                        "name": latest_data['name'],
                        "symbol": latest_data['symbol'].upper(),
                        "price": price,
                        "market_cap": market_cap,
                        "liquidity": liquidity,
                        "prediction": prediction
                    }
                    save_knowledge_base(file_path, knowledge_base)
            
            # Fallback to cached data if no updated data available
            if not latest_data:
                if coin_name in knowledge_base["coins"]:
                    cached_data = knowledge_base["coins"][coin_name]
                    print(f"Bot: [Cached Data]\nName: {cached_data['name']},\nSymbol: {cached_data['symbol']},\nCurrent Price: ${cached_data['price']},\nMarket Cap: ${cached_data['market_cap']},\nLiquidity: ${cached_data.get('liquidity', 'N/A')}")
                    print(f"Bot: Prediction - {cached_data.get('prediction', 'No prediction available.')}")
                else:
                    print("Bot: Sorry, I couldn't find that coin in my data and I couldn't fetch it online.")
        
        # Default question matching
        else:
            best_match = find_best_match(user_input, [q["question"] for q in knowledge_base["questions"]])
            if best_match:
                answer = get_answer_for_question(best_match, knowledge_base)
                print(f'Bot: {answer}')
            else:
                print("Bot: I don't know the answer. Can you teach me?")
                new_answer = input("Type the answer or `Skip` to skip: ")
                if new_answer.lower() != "skip":
                    knowledge_base["questions"].append({"question": user_input, "answer": new_answer})
                    save_knowledge_base(file_path, knowledge_base)
                    print("Bot: Thank you! I learned a new response!")

if __name__ == '__main__':
    chat_bot()

