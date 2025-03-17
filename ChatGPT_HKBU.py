import configparser
import requests
import os

class HKBU_ChatGPT():
    '''
    A class for interacting with the HKBU ChatGPT service.

    Methods:
        submit(message): Submits a message to the HKBU ChatGPT service and returns the response.
    '''
    def __init__(self):
        pass
    
    def submit(self, message, model="gemini"):
        """
        Submits a message to either ChatGPT or Gemini API based on the specified model type.

        :param message: The message to send to the API.
        :type message: str
        :param model: The type of model to use ("chatgpt" or "gemini"). Defaults to "chatgpt".
        :type model: str
        :return: The response from the API, or an error message.
        :rtype: str
        :raises ValueError: If an unsupported model type is provided.
        """
        if model.lower() == "chatgpt":
            conversation = [{"role": "user", "content": message}]
            url = ((os.environ['BASICURL']) +
                   "/deployments/" + (os.environ['MODELNAME']) +
                   "/chat/completions/?api-version=" +
                   (os.environ['APIVERSION']))
            headers = {
                'Content-Type': 'application/json',
                'api-key': (os.environ['ACCESS_TOKEN_LLM'])
            }
            payload = {'messages': conversation}
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content']
            else:
                return f"ChatGPT Error: {response.status_code} - {response.text}"

        elif model.lower() == "gemini":
            # Assuming you have environment variables for Gemini API
            gemini_api_key = os.environ.get("GEMINI_API_KEY")
            gemini_model = os.environ.get("GEMINI_MODEL")
            if not gemini_api_key:
                return "Error: GEMINI_API_KEY environment variable not set."
            
            gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent?key={gemini_api_key}"
            headers = {'Content-Type': 'application/json'}
            payload = {
                "contents": [{
                    "role": "user",
                    "parts": [ { "text": message } ]
                }],
                "generationConfig": {
                    "temperature": 1,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": os.environ.get("MAX_TOKEN"),
                    "responseMimeType": "text/plain"
                }
            }
            response = requests.post(gemini_url, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                try:
                    return data['candidates'][0]['content']['parts'][0]['text']
                except (KeyError, IndexError):
                    return "Error: Unexpected response format from Gemini API."
            else:
                return f"Gemini Error: {response.status_code} - {response.text}"

        else:
            raise ValueError(f"Unsupported model type: {model}. Supported types are 'chatgpt' and 'gemini'.")
        
if __name__ == "__main__":
    ChatGPT_test = HKBU_ChatGPT()

    while True:
        user_input = input("Typing anything:\t")
        response = ChatGPT_test.submit(user_input)
        print(response)
