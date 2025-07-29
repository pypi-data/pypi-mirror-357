# pybot/bot.py

import time
import os
import sys
import requests
import textwrap
from colorama import init, Fore, Style

init(autoreset=True)  # for Windows

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-3.5-turbo"

def print_boxed(text, speaker="AI", width=60):
    wrapped_lines = textwrap.wrap(text, width)
    color = Fore.GREEN if speaker == "You" else Fore.CYAN
    border = "─" * (width + 2)
    print(color + "┌" + border + "┐")
    for line in wrapped_lines:
        print(color + f"│ {line.ljust(width)} │")
    print(color + "└" + border + "┘")

def typewriter(text, delay=0.005):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)

def chat(api_key: str):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    chat_history = []

    ascii_art = """
>=>           >===>            >>       >====>     >=> >==>    >=>    >===>    
>=>         >=>    >=>        >>=>      >=>   >=>  >=> >> >=>  >=>  >>    >=>  
>=>       >=>        >=>     >> >=>     >=>    >=> >=> >=> >=> >=> >=>         
>=>       >=>        >=>    >=>  >=>    >=>    >=> >=> >=>  >=>>=> >=>         
>=>       >=>        >=>   >=====>>=>   >=>    >=> >=> >=>   > >=> >=>   >===> 
>=>         >=>     >=>   >=>      >=>  >=>   >=>  >=> >=>    >>=>  >=>    >>  
>=======>     >===>      >=>        >=> >====>     >=> >=>     >=>   >====>    
"""
    typewriter(ascii_art, 0.002)
    time.sleep(1)
    os.system('cls' if os.name == 'nt' else 'clear')

    print(Fore.YELLOW + Style.BRIGHT + "\n🤖 Welcome to PyBot Chat")
    print(Fore.YELLOW + "Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input(Fore.GREEN + Style.BRIGHT + "You: ")
        except KeyboardInterrupt:
            print("\nExiting...")
            break

        if user_input.lower() == "exit":
            break

        print_boxed(user_input, "You")
        chat_history.append({"role": "user", "content": user_input})

        data = {
            "model": MODEL,
            "messages": chat_history
        }

        try:
            response = requests.post(API_URL, headers=headers, json=data)
            response.raise_for_status()
            reply = response.json()["choices"][0]["message"]["content"]
            chat_history.append({"role": "assistant", "content": reply})
            print_boxed(reply, "AI")
        except Exception as e:
            print(Fore.RED + "⚠️ Error:", str(e))
            break