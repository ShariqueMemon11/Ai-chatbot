                                                         **Ai Chat Bot**
**Libraries Used**

**json:** Handles saving and loading the knowledge base as a JSON file, allowing the bot to retain knowledge across sessions. This knowledge base contains previously answered questions and cached coin data for quick retrieval. 

**difflib.get_close_matches:** Matches user questions with similar previously stored questions. This helps the bot find relevant answers without exact question matches. 

**typing.Optional:** This helps define functions that might return None in certain cases, adding clarity to the bot's handling of different return types. 

**requests:** Manages HTTP requests to CoinGecko’s API, allowing the bot to fetch the latest cryptocurrency data. Error handling with RequestException ensures that if the network is unavailable, the bot can fallback on cached data. 

**API:**

**CoinGecko API**
The CoinGecko API is central to the bot’s cryptocurrency capabilities. It provides information on: 

**Coin Listings**: Used to match user requests with specific cryptocurrency names or symbols. 

**Market Data:** Provides the latest coin price, market cap, and liquidity, allowing the bot to deliver up-to-date information. 

**Price History:** Enables basic trend prediction by analyzing recent price data over time. 

**Main Functions:**

**Knowledge Base Functions:** load_knowledge_base and save_knowledge_base manage the bot’s knowledge, allowing it to learn new answers from users and store cached cryptocurrency data for offline use. 

**Similarity Matching:** find_best_match finds the most similar question to the user’s input, improving response accuracy without requiring an exact match. 

**Coin Data Functions:** get_coin_id finds a coin’s ID, while get_coin_data retrieves live data for that coin. get_coin_price_history obtains historical price data, enabling the bot to give a simple prediction about price trends. 

**Trend Prediction:** predict_trend evaluates price history data to determine whether a coin might experience a price increase, decrease, or remain stable. 

**How It Works** 

**Chat Loop:** The chat_bot function runs the main chatbot loop, responding to user questions by either answering directly, fetching crypto data, or learning a new answer when unknown. 

**User Commands:** Specific phrases like “price of” or “information about” trigger the cryptocurrency functions, while other queries check for matching stored answers. 

In summary, this chatbot combines general Q&A with cryptocurrency functionality, using JSON for knowledge storage, CoinGecko’s API for crypto data, and various Python libraries for error handling and pattern matching. This setup allows it to respond to cryptocurrency inquiries and general knowledge questions, while learning and retaining new information. 
