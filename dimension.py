import pandas as pd
import os
import wikipediaapi
import json
import random
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
import re
import requests
from scipy import spatial
from datetime import datetime


class Data():
    def __init__(self):
        self.API_TOKEN = "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"
        self.street_names = ['Park', 'Street', 'Boulevard', 'Road', 'Main Street', 'Drive', 'Lane', 'Alley']
        self.question_dict = {"special_1": "What is an important monument in the movie ",
                              "special_2": "What is an expensive location in the movie ",
                              "prison": "Which one is a tragic area in the movie ",
                              "free_parking": "What is the loveliest place in the movie "}
        PATH = "./"
        FILENAME = "tmdb_5000_credits.csv"
        FILENAME_MONOPOLY = "monopoly_action_cards_keywords.csv"
        full_path = os.path.expanduser(PATH)
        os.chdir(full_path)
        movie_characters = pd.read_csv(FILENAME, sep=",")
        self.cast_dict = self.clean_movie_dataset(movie_characters)
        self.monopoly_data = pd.read_csv(FILENAME_MONOPOLY, sep=";")
        ## extracted from orig monopoly data via pos-tagging
        self.action_verbs_monopoly = ["Pay", "Take", "Come", "Go", "Get", "Receive",
                                      "Inherit", "Win", "Pass","Collect", "being released",
                                      "Keep", "Sell"]
        self.action_verbs = ["Act", "Answer", "Approve", "Arrange", "Break", "Build", "Buy", "Coach", "Color",
                             "Cough", "Create","Complete", "Cry", "Dance", "Describe", "Draw", "Drink", "Eat",
                             "Edit", "Enter", "Exit","Imitate", "Invent", "Jump", "Laugh", "Lie", "Listen",
                             "Paint", "Plan", "Play", "Read", "Replace","Run", "Scream", "See", "Shop", "Shout",
                             "Sing", "Skip", "Sleep", "Sneeze", "Solve", "Study","Teach",
                             "Touch", "Turn", "Walk", "Win", "Write", "Whistle", "Yank", "Zip"]
        ## extracted from orig monopoly data via pos-tagging
        self.pronouns = ["you","your","yours"]
        self.generation_prompt_text = self.prepare_generation_prompt(self.monopoly_data)
        self.sent_prompt_text = self.prepare_sentiment_prompt(self.monopoly_data)


    def clean_movie_dataset(self, movie_data):
        """
        :movie_data: Pandas DataFrame holding movie titles, character cast
        Preprocess the data, we only need the characters from the movie in a dict

        :returns: dictionary with key = movie title, value =
        """

        cast_rows = []

        for malformed_string in movie_data.cast:
            imd_string = list(malformed_string[1:(len(malformed_string) - 1)].split("}"))

            new_list = []

            for item in imd_string:
                try:
                    if item[0] != "{":
                        item = item[2:(len(item))]
                    item += "}"
                    new_item = json.loads(item)
                    person = new_item["character"]
                    # gender = new_item["gender"]
                    new_list.append(person)
                except IndexError:
                    break
            cast_rows.append(new_list)

        cast_dict = {}
        for movie, cast in zip(movie_data.title, cast_rows):
            cast_dict[movie] = cast

        return cast_dict

    def prepare_generation_prompt(self, monopoly_data):

        generation_prompt_text = ""

        for text, keywords in zip(monopoly_data["content"], monopoly_data["keywords"]):
            imd = "key: " + keywords + "\ntweet: " + text + "\n###"
            generation_prompt_text += imd

        return generation_prompt_text

    def prepare_sentiment_prompt(self, monopoly_data):

        sent_prompt_text = ""

        for text, sentiment in zip(monopoly_data["content"], monopoly_data["bias"]):
            imd = "Tweet: " + text + "\nSentiment: " + sentiment + "\n###"
            sent_prompt_text += imd

        return sent_prompt_text

class Dimension(Data):
    def __init__(self):
        Data.__init__(self)
        self.topic = None
        self.topic = random.choice(list(self.cast_dict))
        self.cast = None
        self.topic_text = self.get_wiki_data_for_topic()
        self.new_field = {"streets": {"1-3": [], "4-6": [], "7-9": [], "10-12": [],
                                 "13-15": [], "16-18": [], "expensive": [], "cheap": []},
                     "stations": [],"prison": [],"free_parking": [], "special": {"1": [], "2": []}}
        self.locations = ["GO"]
        self.prison = ""
        self.action_cards = []

    def change_topic(self):

        self.topic = random.choice(list(self.cast_dict))
        self.get_wiki_data_for_topic()
        self.cast = self.cast_dict[self.topic]
        if len(self.cast) < 27:
            print('Cast list is too short, select a new topic.')
            self.change_topic()
        else:
            print('Select ' + self.topic + ' as new topic.')

    def get_wiki_data_for_topic(self):

        wiki_en_wiki = wikipediaapi.Wikipedia(
            language='en',
            extract_format=wikipediaapi.ExtractFormat.WIKI)

        ## check if page for topic exists
        if wiki_en_wiki.page(self.topic).exists():
            print("Topic is ok.")
            wiki_page = wiki_en_wiki.page(self.topic)
            topic_text = wiki_page.text
        else:
            topic_text = ""
            print("Find a new topic")
            self.change_topic()

        return topic_text

    def __generate_basic_locations(self):
        """
        assign cast characters to basic locations
        :return: void
        """
        self.new_field["streets"]["expensive"] = [x + " Avenue" for x in self.cast[0:2]]
        self.new_field["streets"]["cheap"] = [x + " Drive" for x in self.cast[6:8]]
        self.new_field["streets"]["1-3"] = [x + " " + random.choice(self.street_names) for x in self.cast[8:11]]
        self.new_field["streets"]["4-6"] = [x + " " + random.choice(self.street_names) for x in self.cast[11:14]]
        self.new_field["streets"]["7-9"] = [x + " " + random.choice(self.street_names) for x in self.cast[14:17]]
        self.new_field["streets"]["10-12"] = [x + " " + random.choice(self.street_names) for x in self.cast[17:20]]
        self.new_field["streets"]["13-15"] = [x + " " + random.choice(self.street_names) for x in self.cast[20:23]]
        self.new_field["streets"]["16-18"] = [x + " " + random.choice(self.street_names) for x in self.cast[23:26]]
        self.new_field["stations"] = [x + " Station" for x in self.cast[2:6]]

    def __generate_special_locations(self):

        model_name = "deepset/roberta-base-squad2"
        model = AutoModelForQuestionAnswering.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        q_a = pipeline('question-answering', model=model, tokenizer=tokenizer)

        for category, question_body in self.question_dict.items():
            question = question_body + self.topic + "?"

            QA_input = {
                'question': question,
                'context': self.topic_text
            }
            response = q_a(QA_input)

            if category == "special_1":
                self.new_field["special"]["1"] = [response["answer"]]
            elif category == "special_2":
                self.new_field["special"]["2"] = [response["answer"]]
            else:
                self.new_field[category] = [response["answer"]]

        self.prison = self.new_field["prison"][0]

    def __store_locations(self):

        ## locations into flat list
        for _, value in self.new_field["streets"].items():
            for item in value:
                self.locations.append(item)
        for _, value in self.new_field["special"].items():
            for item in value:
                self.locations.append(item)
        for item in self.new_field["stations"]:
            self.locations.append(item)
        self.locations.append(self.new_field["prison"][0])
        self.locations.append(self.new_field["free_parking"][0])

    def generate_locations(self):

        self.__generate_basic_locations()
        self.__generate_special_locations()
        self.__store_locations()

    def keyword_generation(self):
        first_verb = random.choice(self.action_verbs_monopoly).lower()
        second_verb = random.choice(self.action_verbs).lower()
        pronoun = random.choice(self.pronouns).lower()
        location = random.choice(self.locations)
        number = 2000
        select_number = random.choice([0, 1])

        ## create keyword list for generation
        if select_number == 1:
            keyword_list = [first_verb, second_verb, pronoun, location, number]
        else:
            keyword_list = [first_verb, second_verb, pronoun, location]
        keyword_string = self.helper_keywords(keyword_list)

        return location, keyword_string

    def helper_keywords(self, keyword_list):
        keyword_string = ""

        for item in keyword_list:
            if keyword_string == "":
                keyword_string += str(item)
            else:
                keyword_string += ", " + str(item)

        return keyword_string

    def query(self, payload='',
              parameters={'max_new_tokens': 25, 'temperature': 1, 'end_sequence': "###"},
              options={'use_cache': False}):
        API_URL = "https://api-inference.huggingface.co/models/EleutherAI/gpt-neo-2.7B"
        headers = {"Authorization": f"Bearer {self.API_TOKEN}"}
        body = {"inputs": payload, 'parameters': parameters, 'options': options}
        response = requests.request("POST", API_URL, headers=headers, data=json.dumps(body))
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            return "Error:" + " ".join(response.json()['error'])
        else:
            return response.json()[0]['generated_text']

    def __preprocess(self, sent):
        sent = nltk.word_tokenize(sent)
        sent = nltk.pos_tag(sent)
        return sent

    def __pos_distribution(self, pos_tuples_of_sentence):
        """
        :pos_tuple_of_sentences: tuple (token, pos_tag) as returned from preprocess function

        crop pos tags into relevant groups (first two letters)
        count occurences of pos tags in input sentence

        :returns: pandas DataFrame with pos_tag and its frequency

        """
        pos_df = pd.DataFrame(pos_tuples_of_sentence, columns=["token", "long_pos_tag"])
        pos_df["pos_tag"] = [x[0:2] for x in pos_df["long_pos_tag"]]
        freq_df = pos_df["pos_tag"].value_counts()

        return freq_df

    def __eval_compare_structure(self, reference, new_sentence):
        ## preprocess both
        reference = self.__preprocess(reference)
        new_sentence = self.__preprocess(new_sentence)

        ## pos distribution
        reference = self.__pos_distribution(reference)
        new_sentence = self.__pos_distribution(new_sentence)

        ## merge vectors
        merged_df = pd.merge(reference, new_sentence, how="outer", left_index=True, right_index=True).fillna(0)
        merged_df.columns = ["reference", "target"]

        ## calc cosine similarity
        similarity_score = 1 - spatial.distance.cosine(merged_df["reference"], merged_df["target"])

        return similarity_score

    def __eval_compare_lengths(self, reference, new_sentence):

        reference = reference.split(" ")
        new_sentence = new_sentence.split(" ")
        len_ref = len(reference)
        len_new = len(new_sentence)

        if len_ref >= len_new:
            len_score = len_new / len_ref
        else:
            len_score = len_ref / len_new

        return len_score

    def __score_weighting(self, similarity_score, len_score, alpha=0.3):
        score = alpha * len_score + (1 - alpha) * similarity_score

        return score

    def __eval_sentence(self, reference, new_sentence):
        similarity_score = self.__eval_compare_structure(reference, new_sentence)
        len_score = self.__eval_compare_lengths(reference, new_sentence)

        score = self.__score_weighting(similarity_score, len_score)

        return score

    def __get_reference_for_sentence(self, location, sentiment):  ## monopoly_data):

        if location == self.prison:
            if sentiment == "positiv":
                reference = "You will be released from prison! You must keep this card until you need it or sell it."
            else:
                reference = "Go to the prison! Go directly there. Do not pass Go. Do not collect DM 4000,-."
        else:
            if sentiment == "positiv":
                pos_data = self.monopoly_data['content'][self.monopoly_data['bias'] == "positiv"]
                pos_data = list(pos_data)
                reference = random.choice(pos_data)
            elif sentiment == "negativ":
                neg_data = self.monopoly_data['content'][self.monopoly_data['bias'] == "negativ"]
                neg_data = list(neg_data)
                reference = random.choice(neg_data)
            elif sentiment == "neutral":
                neu_data = self.monopoly_data['content'][self.monopoly_data['bias'] == "neutral"]
                neu_data = list(neu_data)
                reference = random.choice(neu_data)
            else:
                reference = "Go to the prison! Go directly there. Do not pass Go. Do not collect DM 4000,-."

        return reference

    def __action_from_action_card(self, action_card):
        ## search action card for locations
        for location in self.locations:
            ## exact matching for GO
            if location == "GO":
                if action_card.find(location) != -1:
                    go_to_location = location
                    break
                else:
                    go_to_location = None
            else:
                if action_card.lower().find(location.lower()) != -1:
                    go_to_location = location
                    break
                else:
                    go_to_location = None
        ## if action card contains "prison", go to the current prison location
        ## same for station
        if go_to_location is None:
            if action_card.lower().find("prison") != -1:
                go_to_location = self.prison
            elif action_card.lower().find("station") != -1 :
                go_to_location = random.choice(self.new_field["stations"])
            else:
                go_to_location = None

        ## extract number, if existing
        m = re.search('[0-9]+', action_card)
        try:
            m.group(0)
        except AttributeError:
            number = None
        else:
            number = m.group(0)

        return go_to_location, number

    def generate_action_cards(self, counter=0, number_of_cards=2):

        print("Counter is: ", counter)

        ## stop generation of action cards
        if counter > number_of_cards:
            return self.action_cards

        else:
            ## keyword generation
            location, keyword_string = self.keyword_generation()
            print("This is the keyword string: ", keyword_string)

            ## action card generation
            generation_prompt = self.generation_prompt_text + "\nkey: " + keyword_string + "\ntweet:"
            data = self.query(generation_prompt)
            action_card = re.findall(r"(?<=tweet:\s).*", data)[-1]

            print("Action card: ", action_card)

            ## sentiment classification for action card
            sent_prompt = self.sent_prompt_text + "\nTweet: " + action_card + "\nSentiment:"
            #print("Sentiment analysis prompt: ", sent_prompt)
            sentiment = self.query(sent_prompt)
            #print(sentiment)
            action_sentiment = re.findall(r"(?<=Sentiment:\s).*", sentiment)[-1]

            print("Action sentiment is: ", action_sentiment)

            ## get reference
            reference = self.__get_reference_for_sentence(location, action_sentiment)

            ## evaluate action card against reference
            score = self.__eval_sentence(reference, action_card)

            ## if action card OK, append
            if score >= 0.5:
                location, number = self.__action_from_action_card(action_card)
                self.action_cards.append((action_card, action_sentiment, location, number))
                counter += 1
                self.generate_action_cards(counter)
            else:
                self.generate_action_cards(counter)


# print(datetime.now())
# new_dimension = Dimension()
# new_dimension.generate_locations()
# print(new_dimension.locations)
# print(datetime.now())

# new_dimension.locations = ['GO',
#  'Mr. Nobody Street',
#  'Deckard Shaw Drive',
#  'Han Drive',
#  'Sean Boswell Lane',
#  'Elena Boulevard',
#  'Hector Road',
#  'Owen Shaw Drive',
#  'Safar Road',
#  'Jack Lane',
#  'Samantha Hobbs Alley',
#  'Letty Fan Park',
#  'Female Racer Park',
#  'Race Starter Lane',
#  'Hot Teacher Drive',
#  'Doctor Park',
#  'Merc Tech Road',
#  'Weapons Tech Lane',
#  'Dominic Toretto Avenue',
#  "Brian O'Conner Avenue",
#  'Kiet Drive',
#  'Kara Drive',
#  'Walker',
#  'Los Angeles',
#  'Letty Station',
#  'Roman Station',
#  "Tej (as Chris 'Ludacris' Bridges) Station",
#  'Mia Station',
#  'Walker',
#  'Abu Dhabi']
#
# new_dimension.new_field = {'streets': {'1-3': ['Mr. Nobody Street', 'Deckard Shaw Drive', 'Han Drive'],
#   '4-6': ['Sean Boswell Lane', 'Elena Boulevard', 'Hector Road'],
#   '7-9': ['Owen Shaw Drive', 'Safar Road', 'Jack Lane'],
#   '10-12': ['Samantha Hobbs Alley', 'Letty Fan Park', 'Female Racer Park'],
#   '13-15': ['Race Starter Lane', 'Hot Teacher Drive', 'Doctor Park'],
#   '16-18': ['Merc Tech Road', 'Weapons Tech Lane'],
#   'expensive': ['Dominic Toretto Avenue', "Brian O'Conner Avenue"],
#   'cheap': ['Kiet Drive', 'Kara Drive']},
#  'stations': ['Letty Station',
#   'Roman Station',
#   "Tej (as Chris 'Ludacris' Bridges) Station",
#   'Mia Station'],
#  'prison': ['Walker'],
#  'free_parking': ['Abu Dhabi'],
#  'special': {'1': ['Walker'], '2': ['Los Angeles']}}
#
# #new_dimension.generate_locations()
# new_dimension.generate_action_cards()




