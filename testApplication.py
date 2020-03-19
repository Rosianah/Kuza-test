import logging, json, os, difflib, re, traceback
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
import time
from tkinter import Button, filedialog,Label,Frame, StringVar, Tk, IntVar, Radiobutton
import requests
import subprocess


#Bot test window(front end)
class BotTest(Frame):
    def __init__(self,tk, url = 'http://51.144.49.229:8080'): #tk is tkinter its a GUI package
        self.url=url+"/webhook"
        Frame.__init__(self,tk)
        tk.geometry('650x600') #window size

        tk.title("Welcome to Caawiye Tests App")#Intrface/window title

        self.conversations = {}
        self.test_counter, self.question_counter = 0,0
        self.conversationReset = True

        self.statusupdate = StringVar() #stringVar has been imported from tkinter
        self.statusupdate.set('Awaiting test  file to be loaded') #current status of the test app (at the bottom)

        #labels 
        lbl = Label(tk, text="Please select Bot instance to test", font=("Arial Bold", 15))

        #pack geometry manager
        lbl.pack(side="top", fill='both', expand=True, padx=1, pady=1)

        #select file button has a selectfile() function call
        self.fileSelector = Button(self,text='Select test file',command=lambda : self.selectfile(), font=("Arial Bold", 12))
        self.fileSelector.pack(side="top", fill='both', expand=True, padx=4, pady=4)

        #value holdr for integer values values and set the variable to a value 1 
        self.v = IntVar()
        self.v.set(1)

        #pack() anchors define where text is positioned
        Label(self, text="Do you want to validate bot responses?").pack(anchor='w',side="top", fill='both', expand=True, padx=4, pady=4)
        
        Radiobutton(self, text="Yes", variable=self.v, value=1).pack(anchor='e')
        Radiobutton(self, text="No", variable=self.v, value=0).pack(anchor='e')

        #function call to load the bots file
        self.loadBots("bots.json")

        

    #quit button
    def quit(self):
        global root
        root.quit()

    def cancel(self,client):
        client.disconnect

    #sending a reset message function
    #converstation reset becomes false after a reset message has been send
    def reset_conversation(self,client,bot):
        text = 'Reset'
        client.send_message(bot, text) #bot id then message
        self.conversationReset = False

    #selecting a file using explorer 
    def selectfile(self):
        #tkinter module to ask a file to open. Filedialog class and askopenfilename function
        file = filedialog.askopenfilename(title='Choose a test file')
        try:
            if file != None: 
                self.conversations = self.load_json(file) #call load_json()
                 #count the number of converstations, size of the array tests
                self.conversationLabel = Label(self, text=str(len(self.conversations['tests'])) + " test found in file " + os.path.basename(file), font=("Arial", 12))
                self.conversationLabel.pack(side="top", fill='both', expand=True, padx=4, pady=4) #the geometry
        #if out of the norm occurs
        except Exception as e:
            print(e)
            self.conversationLabel = Label(self, text="You have chosen an invalid json file")
            self.conversationLabel.pack(side="top", fill='both', expand=True, padx=4, pady=4)

    #show the output at teh bottom while the bot test is running ---displayStatus
    def show_output(self,text_output):
        self.statusupdate.set(text_output)
        # print(text_output)
        self.update_idletasks()

    #send message to the bot ==== out
    async def send_to_bot(self,client,bot,text,type):
        if type == 'message':#***
            # Send message to bot
            client.send_message(bot, text)

    def reset_tests(self):
        self.question_counter = 0
        self.test_counter = 0
        self.conversationReset = True

    #loading bots and having a button for each bot
    def loadBots(self,file):
        bots = self.load_json(file)

        #Display the bots
        for bot in bots:
            button = Button(self, text=bot, width=20, font=("Lucinda Sans", 12),command= lambda name = bot, id = bots[bot]: self.run_test(name,id))
            button.pack(side="top", expand=False, padx=(10, 10), pady=(10, 10))
            

    


    #compare strings
    def string_compare(self,first,second):
        ratio = difflib.SequenceMatcher(None,first, second).ratio() #ratio returns similarity score between input strings
        isFirstInSecond = second.find(first)
        result = ratio < 0.75 and isFirstInSecond < 0
        # print("First: " + first + " Second: "+ second)
        # print("ratio: " + "{0:0.2f}".format(ratio) + " isFirstInSecond: "+ str(second.find(first)))
        # print(result)
        return result

    #load the json files in the explorer
    def load_json(self,file): 
        json_file = open(file, "rb")
        return json.load(json_file)

    #Reading conversations and matching the ids with the expected output, validate responses
    def load_expected_text(self,expected_response):
        response = ""
        filtered = {}

        json = self.load_json(expected_response['file']) #load the file in the conversations eg intents.json
        match = [i for i in json if i["id"] == expected_response['id']][-1] #if id in json file(eg intents) matches with the id in the expected conversation (conversation.json)

        #where there are filters
        if "filters" in expected_response:
            key_prop = expected_response["filters"]["property"]
            match = match[key_prop] #match with the key using the id
            
            for item in match: #for key(filter, property) 
                for i in list(expected_response["filters"])[1:]: #for any item in list of filters
                    if item[i] == expected_response["filters"][i]: #if items in the filters match with the expected response
                        filtered = item 
        else:
            filtered = match
        
        keys = expected_response["property"].split(".") #split where there's . eg prompts.promptWithHints

    #    Will find a better way to filter this part and make it dynamic
        if len(keys) > 1: #if length of keys is > 1
            filtered = filtered[keys[0]] #filtered first item in keys
            if isinstance(filtered,dict): #check if filtered is an instance of dict
                filtered = filtered[keys[1]] #filtered is the second item of keys

        key_results = self.findkeys(filtered, keys[-1]) #call the findkeys func
        return self.remove_placeholders(list(key_results))

    def remove_placeholders(self, items):
        formated_string = []
        for i in items:
            if isinstance(i,list):
                [formated_string.append(re.sub("\$\w+", '', j)) for j in i] 
            else:
                formated_string.append(re.sub("\$\w+", '', i))
        return formated_string
    
    def findkeys(self,node, kv):
        if isinstance(node, list):
            for i in node:
                for x in self.findkeys(i, kv):
                    yield x #return
        elif isinstance(node, dict):
            if kv in node:
                yield node[kv]
            for j in node.values():
                for x in self.findkeys(j, kv):
                    yield x


    def post(self, text):
        data = {
            "from":"+254741219183",
            "to":"21393",
            "text": text
        }
        res = requests.post(self.url, json = data)
        print (res.status_code)


    #running test, provide api id and hash
    def run_test(self,name,bot_id):
        #        conversations from TelegramInterface.selectfile
        # testNumbers = self.load_json("testers.json")
        self.question_counter = 0
        self.test_counter = 0
        self.conversations = self.load_json("_conversations.json")
        
        #reset conversation if not conversation reset is true
        if self.conversationReset is False:
            self.post(self.conversations['tests'][self.test_counter]['questions'][self.question_counter])
        else:
            self.post("reset")
            self.conversationReset = False

        from multiprocessing import Process, Pipe
        from server import run

        parent_conn, child_conn = Pipe()
        server_process = Process(target=run, args=(child_conn, 5001, True,))
        server_process.start()
        # convo = subprocess.run(flaskapp.run())
        print(parent_conn.recv())

        server_process.join()



root = Tk()
frame = BotTest(root).pack()
Button(root, text="Quit", command=quit).pack()
root.mainloop()

