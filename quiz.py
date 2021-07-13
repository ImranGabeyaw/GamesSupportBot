# -*- coding: utf-8 -*-
"""
Quiz / Question classes for quizbot.

@author: drkatnz
"""
import discord
import asyncio
import random
import re
import os

#todo: probably need to remove punctuation from answers



class Quiz:
    
    def __init__(self, client, win_limit=10, hint_time=15):
        #initialises the quiz
        self.__running = False
        self.current_question = None
        self._win_limit = win_limit
        self._hint_time = hint_time
        self._questions = []
        self._asked = []
        self.scores = {}
        self._client = client
        self._quiz_channel = None
        self._cancel_callback = True
        self._map_list = ["bank","border","chalet","club house","coastline","consulate","kafe","kanal","oregon","theme park","villa"]
        self._map_length = [len(os.listdir("quizimages/Bank")), len(os.listdir("quizimages/Border")), len(os.listdir("quizimages/Chalet")),
        len(os.listdir("quizimages/Club House")), len(os.listdir("quizimages/Coastline")), len(os.listdir("quizimages/Consulate")),
        len(os.listdir("quizimages/Kafe Dostoyevsky")), len(os.listdir("quizimages/Kanal")),
        len(os.listdir("quizimages/Oregon")), len(os.listdir("quizimages/Theme Park")), len(os.listdir("quizimages/Villa"))]
        self.map = None
       
        
        #load in some questions
        datafiles = os.listdir('quizdata')
        for df in datafiles:
            filepath = 'quizdata' + os.path.sep + df
            self._load_questions(filepath)
            print('Loaded: ' + filepath)
        print('Quiz data loading complete.\n')
        
    
    
    def _load_questions(self, question_file):
        # loads in the questions for the quiz
        with open(question_file, encoding='utf-8',errors='replace') as qfile:
            lines = qfile.readlines()
        question = None
        category = None
        answer = None
        image = None      
        regex = None
        position = 0

        while position < len(lines):
            if lines[position].strip().startswith('#'):
                #skip
                position += 1
                continue
            if lines[position].strip() == '': #blank line
                #add question
                if question is not None and answer is not None and image is not None:
                    q = Question(question=question, answer=answer, image=image, 
                                 category=category, regex=regex)
                    self._questions.append(q)
                #reset everything
                question = None
                category = None
                answer = None
                image = None
                regex = None
                position += 1
                continue
                
            if lines[position].strip().lower().startswith('category'):
                category = lines[position].strip()[lines[position].find(':') + 1:].strip()
            elif lines[position].strip().lower().startswith('question'):
                question = lines[position].strip()[lines[position].find(':') + 1:].strip()
            elif lines[position].strip().lower().startswith('answer'):
                answer = lines[position].strip()[lines[position].find(':') + 1:].strip()
            elif lines[position].strip().lower().startswith('image'):
                image = lines[position].strip()[lines[position].find(':') + 1:].strip()
            elif lines[position].strip().lower().startswith('regexp'):
                regex = lines[position].strip()[lines[position].find(':') + 1:].strip()
            #else ignore
            position += 1
                
    
    def started(self):
        #finds out whether a quiz is running
        return self.__running
    
    
    def question_in_progress(self):
        #finds out whether a question is currently in progress
        return self.__current_question is not None
    
    
    async def _hint(self, hint_question, hint_number):
        #offers a hint to the user
        if self.__running and self.current_question is not None:
            await asyncio.sleep(self._hint_time)
            if (self.current_question == hint_question 
                 and self._cancel_callback == False):
                if (hint_number >= 5):
                    await self.next_question(self._channel)
                
                hint = self.current_question.get_hint(hint_number)
                await self._channel.send( 'Hint {}: {}'.format(hint_number, hint))
                if hint_number < 5:
                    await self._hint(hint_question, hint_number + 1) 
    
    
    async def start(self, channel, args):
        map_request = ' '.join(args).lower()
        #starts the quiz in the given channel.
        if self.__running:
            #don't start again
            await channel.send('Quiz already started in channel {}, you can stop it with !stop or !halt'.format(self._channel.name))
        elif map_request not in self._map_list and args:
            await channel.send('Please use this command with no arguments or with a valid specific map to be qizzed on')
        else:
            await self.reset()
            self._channel = channel
            await self._channel.send('Quiz starting in 5 seconds...')
            await asyncio.sleep(5)
            self.__running = True
            if args:
                self.map = map_request
            await self.ask_question()
            
            
    async def reset(self):
        if self.__running:
            #stop
            await self.stop()
        
        #reset the scores
        self.current_question = None
        self._cancel_callback = True
        self.__running = False
        self._questions.extend(self._asked)
        self._asked = []
        self.scores = {}
        self.map = None
            
            
    async def stop(self):
        #stops the quiz from running
        if self.__running:
            #print results
            #stop quiz
            await self._channel.send( 'Quiz stopping.')
            if(self.current_question is not None):
                await self._channel.send( 
                     'The answer to the current question is: {}'.format(self.current_question.get_answer()))
            await self.print_scores()
            self.current_question = None
            self._cancel_callback = True
            self.__running = False
        else:
            await self._channel.send('No quiz running, start one with !ask or !quiz')
            
    
    async def ask_question(self):
        #asks a question in the quiz
        if self.__running:
            #grab a random question
            if self.map == "bank":
                qpos = random.randint(0,self._map_length[0] - 1 - len(self._asked))
                self.current_question = self._questions[qpos]
                self._questions.remove(self.current_question)
                self._asked.append(self.current_question)
                question = self.current_question.ask_question()
                await self._channel.send('**Question {}**: {}'.format(len(self._asked), question[0]), file=discord.File(question[1]))
                self._cancel_callback = False
                await self._hint(self.current_question, 1)
            elif self.map == "border":
                qpos = random.randint(self._map_length[0] - len(self._asked), sum(self._map_length[0:2]) - 1 - len(self._asked))
                self.current_question = self._questions[qpos]
                self._questions.remove(self.current_question)
                self._asked.append(self.current_question)
                question = self.current_question.ask_question()
                await self._channel.send('**Question {}**: {}'.format(len(self._asked), question[0]), file=discord.File(question[1]))
                self._cancel_callback = False
                await self._hint(self.current_question, 1)
            elif self.map == "chalet":
                qpos = random.randint(self._map_length[0:2] - len(self._asked), sum(self._map_length[0:3]) - 1 - len(self._asked))
                self.current_question = self._questions[qpos]
                self._questions.remove(self.current_question)
                self._asked.append(self.current_question)
                question = self.current_question.ask_question()
                await self._channel.send('**Question {}**: {}'.format(len(self._asked), question[0]), file=discord.File(question[1]))
                self._cancel_callback = False
                await self._hint(self.current_question, 1)
            elif self.map == "club house":
                qpos = random.randint(sum(self._map_length[0:3]) - len(self._asked), sum(self._map_length[0:4]) - 1 - len(self._asked))
                self.current_question = self._questions[qpos]
                self._questions.remove(self.current_question)
                self._asked.append(self.current_question)
                question = self.current_question.ask_question()
                await self._channel.send('**Question {}**: {}'.format(len(self._asked), question[0]), file=discord.File(question[1]))
                self._cancel_callback = False
                await self._hint(self.current_question, 1)
            elif self.map == "coastline":
                qpos = random.randint(sum(self._map_length[0:4]) - len(self._asked),sum(self._map_length[0:5]) - 1 - len(self._asked))
                self.current_question = self._questions[qpos]
                self._questions.remove(self.current_question)
                self._asked.append(self.current_question)
                question = self.current_question.ask_question()
                await self._channel.send('**Question {}**: {}'.format(len(self._asked), question[0]), file=discord.File(question[1]))
                self._cancel_callback = False
                await self._hint(self.current_question, 1)
            elif self.map == "consulate":
                qpos = random.randint(sum(self._map_length[0:5]) - len(self._asked), sum(self._map_length[0:6]) - 1 - len(self._asked))
                self.current_question = self._questions[qpos]
                self._questions.remove(self.current_question)
                self._asked.append(self.current_question)
                question = self.current_question.ask_question()
                await self._channel.send('**Question {}**: {}'.format(len(self._asked), question[0]), file=discord.File(question[1]))
                self._cancel_callback = False
                await self._hint(self.current_question, 1)
            elif self.map == "kafe":
                qpos = random.randint(sum(self._map_length[0:6]) - len(self._asked), sum(self._map_length[0:7]) - 1 - len(self._asked))
                self.current_question = self._questions[qpos]
                self._questions.remove(self.current_question)
                self._asked.append(self.current_question)
                question = self.current_question.ask_question()
                await self._channel.send('**Question {}**: {}'.format(len(self._asked), question[0]), file=discord.File(question[1]))
                self._cancel_callback = False
                await self._hint(self.current_question, 1)
            elif self.map == "kanal":
                qpos = random.randint(sum(self._map_length[0:7]) - len(self._asked), sum(self._map_length[0:8]) - 1 - len(self._asked))
                self.current_question = self._questions[qpos]
                self._questions.remove(self.current_question)
                self._asked.append(self.current_question)
                question = self.current_question.ask_question()
                await self._channel.send('**Question {}**: {}'.format(len(self._asked), question[0]), file=discord.File(question[1]))
                self._cancel_callback = False
                await self._hint(self.current_question, 1)
            elif self.map == "oregon":
                qpos = random.randint(sum(self._map_length[0:8]) - len(self._asked), sum(self._map_length[0:9]) - 1 - len(self._asked))
                self.current_question = self._questions[qpos]
                self._questions.remove(self.current_question)
                self._asked.append(self.current_question)
                question = self.current_question.ask_question()
                await self._channel.send('**Question {}**: {}'.format(len(self._asked), question[0]), file=discord.File(question[1]))
                self._cancel_callback = False
                await self._hint(self.current_question, 1)
            elif self.map == "theme park":
                qpos = random.randint(sum(self._map_length[0:9]) - len(self._asked), sum(self._map_length[0:10]) - 1 - len(self._asked))
                self.current_question = self._questions[qpos]
                self._questions.remove(self.current_question)
                self._asked.append(self.current_question)
                question = self.current_question.ask_question()
                await self._channel.send('**Question {}**: {}'.format(len(self._asked), question[0]), file=discord.File(question[1]))
                self._cancel_callback = False
                await self._hint(self.current_question, 1)
            elif self.map == "villa":
                qpos = random.randint(sum(self._map_length[0:10]) - len(self._asked), sum(self._map_length[0:11]) - 1 - len(self._asked))
                self.current_question = self._questions[qpos]
                self._questions.remove(self.current_question)
                self._asked.append(self.current_question)
                question = self.current_question.ask_question()
                await self._channel.send('**Question {}**: {}'.format(len(self._asked), question[0]), file=discord.File(question[1]))
                self._cancel_callback = False
                await self._hint(self.current_question, 1)
            else:
                qpos = random.randint(0,len(self._questions) - 1)
                self.current_question = self._questions[qpos]
                self._questions.remove(self.current_question)
                self._asked.append(self.current_question)
                question = self.current_question.ask_question()
                await self._channel.send('**Question {}**: {}'.format(len(self._asked), question[0]), file=discord.File(question[1]))
                self._cancel_callback = False
                await self._hint(self.current_question, 1)
            
            
    async def next_question(self, channel):
        #moves to the next question
        if self.__running:
            if channel == self._channel:
                await self._channel.send( 
                         'Moving onto next question. The answer I was looking for was: **{}**'.format(self.current_question.get_answer()))
                self.current_question = None
                self._cancel_callback = True
                await self.ask_question()
            
            
            
    async def answer_question(self, message):
        #checks the answer to a question
        if self.__running and self.current_question is not None:
            if message.channel != self._channel:
                pass
            
            if self.current_question.answer_correct(message.content):
                #record success
                self._cancel_callback = True
                
                if message.author.name in self.scores:
                    self.scores[message.author.name] += 1
                else:
                    self.scores[message.author.name] = 1
                               
                await self._channel.send( 
                 'Well done, **{}**, the correct answer was: **{}**'.format(message.author.name, self.current_question.get_answer()))
                self.current_question = None
                
                #check win
                if self.scores[message.author.name] == self._win_limit:
                    
                    await self.print_scores()
                    await self._channel.send( '**{}** has won! Congratulations.'.format(message.author.name))
                    self._questions.extend(self._asked)
                    self._asked = []
                    self.__running = False                    
                
                #print totals?
                elif len(self._asked) % 5 == 0:
                    await self.print_scores()                    
                
                    
                await self.ask_question()
                
                
                
                
    async def print_scores(self):
        #prints out a table of scores.
        if self.__running:
            await self._channel.send('Current quiz results:')
        else:
            await self._channel.send('Most recent quiz results:')
            
        highest = 0
        for name in self.scores:
            await self._channel.send('{}:\t{}'.format(name,self.scores[name]))
            if self.scores[name] > highest:
                highest = self.scores[name]
                
        if len(self.scores) == 0:
            await self._channel.send('No results to display.')
                
        leaders = []
        for name in self.scores:
            if self.scores[name] == highest:
                leaders.append(name)
                
        if len(leaders) > 0:
            if len(leaders) == 1:
                await self._channel.send('Current leader: {}'.format(leaders[0]))
            else:
                await self._channel.send('Print leaders: {}'.format(leaders))
        
            
    
    
    
class Question:
    # A question in a quiz
    def __init__(self, question, answer, image, category=None, author=None, regex=None):
        self.question = question
        self.answer = answer
        self.image = image
        self.author = author
        self.regex = regex
        self.category = category
        self._hints = 0
        
        
    def ask_question(self):
        # gets a pretty formatted version of the question.
        question_text = ''
        question = []
        if self.category is not None:
            question_text+='**({})** '.format(self.category)
        else:
            question_text+='(General) '
        if self.author is not None:
            question_text+='Posed by {}. '.format(self.author)
        question_text += self.question
        question = [question_text, self.image]
        return question
    
    
    def answer_correct(self, answer):
        #checks if an answer is correct or not.
        
        #should check regex
        if self.regex is not None:
            match = re.fullmatch(self.regex.lower().strip(),answer.lower().strip())
            return match is not None
            
        #else just string match
        return  answer.lower().strip() == self.answer.lower().strip()
    
    
    def get_hint(self, hint_number):
        # gets a formatted hint for the question
        hint = []
        for i in range(len(self.answer)):
            if i % 5 < hint_number:
                hint = hint + list(self.answer[i])
            else:
                if self.answer[i] == ' ':
                    hint += ' '
                else:
                    hint += '-'
                    
        return ''.join(hint)
        
    
    def get_answer(self):
        # gets the expected answer
        return self.answer
    