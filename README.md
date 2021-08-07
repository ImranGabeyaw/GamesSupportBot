GamesSupportBot
========================


  - requirements
    - Python >= 3.7
    - PyTesseract
    - Pipenv

 
About 
------------
  GamesSupportBot is a discord bot that was created to assist in the quality of life, education, or improvement of skill for certain video games (currently Maplestory and 
  Rainbow Six Siege).
  
  Main functions;
  1. Building a flame profile from an image of a Maplestory item using OCR to gather the required data. 
    A recoomendation on how to proceed with flaming the item is given based on the gathered data.
  2. Multiplayer quiz in which you must identify certain sections of Rainbow Six Siege maps to serve as a callout trainer.
  3. A scheduled ping to users with a certain role to serve as a reminder that they have 30 seconds to perform a certain action in-game.

Examples
-----------------------

  - !flame command
  
  ![alt text](https://github.com/ImranAgraw/GamesSupportBot/blob/main/flame.png?raw=true)
  - !quiz command
  
  ![alt text](https://github.com/ImranAgraw/GamesSupportBot/blob/main/quiz.png?raw=true)
  - scheduled ping
  
  ![alt text](https://github.com/ImranAgraw/GamesSupportBot/blob/main/ping.png?raw=true)
  
Usage
-----------------------
After adding a discord bot to your server, get your bot's token and set it in the .env file.
 
Open CMD and execute the following commands
 ###
    cd 'GamesSupportBot path'
    py supportbot.py
    
 Finally, use !flame or !quiz commands in your discord server as to your liking
    
