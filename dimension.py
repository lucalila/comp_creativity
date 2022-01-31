import pandas as pd
import os
import wikipediaapi
import random
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
import re
import requests
from scipy import spatial
from ordered_set import OrderedSet
import json
from wordfilter import Wordfilter


class Data():
    def __init__(self):
        self.API_TOKEN = "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"
        self.street_names = ['Park', 'Street', 'Boulevard', 'Road', 'Street', 'Drive', 'Lane', 'Alley']
        self.question_dict = {"special_1": ["What is an important monument in the movie ",
                                            "What is an extraordinary effect in the movie "],
                              "special_2": ["What is an expensive item in the movie ",
                                            "Which one is a challenging and difficult situation in the movie "],
                              "prison": ["What is the most dramatic and darkest event in the movie ",
                                         "What is the audience afraid of in the movie "],
                              "free_parking": ["What is the loveliest place in the movie ",
                                               "What is the nicest and happiest location in the movie "]}
        PATH = "./"
        FILENAME = "tmdb_5000_credits.csv"
        FILENAME_MONOPOLY = "monopoly_action_cards_keywords.csv"
        full_path = os.path.expanduser(PATH)
        os.chdir(full_path)
        movie_characters = pd.read_csv(FILENAME, sep=",", engine='python')
        self.cast_dict = self.clean_movie_dataset(movie_characters)
        self.monopoly_data = pd.read_csv(FILENAME_MONOPOLY, sep=";")
        ## extracted from orig monopoly data via pos-tagging
        self.action_verbs_monopoly = ["Pay", "Take", "Come", "Go", "Get", "Receive",
                                      "Inherit", "Win", "Pass", "Collect", "being released",
                                      "Keep", "Sell"]
        self.action_verbs = ["Act", "Answer", "Approve", "Arrange", "Break", "Build", "Buy", "Coach", "Color",
                             "Cough", "Create", "Complete", "Cry", "Dance", "Describe", "Draw", "Drink", "Eat",
                             "Edit", "Enter", "Exit", "Imitate", "Invent", "Jump", "Laugh", "Lie", "Listen",
                             "Paint", "Plan", "Play", "Read", "Replace", "Run", "Scream", "See", "Shop", "Shout",
                             "Sing", "Skip", "Sleep", "Sneeze", "Solve", "Study", "Teach",
                             "Touch", "Turn", "Walk", "Win", "Write", "Whistle", "Yank", "Zip"]
        ## extracted from orig monopoly data via pos-tagging
        self.pronouns = ["you", "your", "yours"]
        self.generation_prompt_text = self.prepare_generation_prompt(self.monopoly_data)
        self.sent_prompt_text = self.prepare_sentiment_prompt(self.monopoly_data)
        self.wordfilter = Wordfilter()

    def clean_movie_dataset(self, movie_data):
        """
        :movie_data: Pandas DataFrame holding movie titles, character cast
        Preprocess the data, we only need the characters from the movie in a dict

        :returns: dictionary with key = movie title, value = character cast
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
        """
        :param monopoly_data: pd.DataFrame with training data
        prepare the few-shot prompt for the key-to-text model
        inference api with the original monopoly data
        :return: generation_prompt_text
        """

        generation_prompt_text = ""

        for text, keywords in zip(monopoly_data["content"], monopoly_data["keywords"]):
            imd = "key: " + keywords + "\ntweet: " + text + "\n###"
            generation_prompt_text += imd

        return generation_prompt_text

    def prepare_sentiment_prompt(self, monopoly_data):
        """
        :param monopoly_data: pd.DataFrame with training data
        prepare the few-shot prompt for the sentiment classification
        model api with the original monopoly data
        :return: sent_prompt_text
        """

        sent_prompt_text = ""

        for text, sentiment in zip(monopoly_data["content"], monopoly_data["bias"]):
            imd = "Tweet: " + text + "\nSentiment: " + sentiment + "\n###"
            sent_prompt_text += imd

        return sent_prompt_text


class Dimension(Data):
    def __init__(self):
        Data.__init__(self)
        self.topic = random.choice(list(self.cast_dict))
        self.cast = self.cast_dict[self.topic]
        self.topic_text = self.get_wiki_data_for_topic()
        self.new_field = {"streets": {"1-3": [], "4-6": [], "7-9": [], "10-12": [],
                                      "13-15": [], "16-18": [], "expensive": [], "cheap": []},
                          "stations": [], "prison": [], "free_parking": [], "special": {"1": [], "2": []}}
        self.locations = ["Start"]
        self.prison = ""
        self.action_cards = []

    def check_topic_cast(self):
        """
        check if cast data of the topic is meeting the
        dimension criteria
        clean special characters in character names
        :return:
        """

        if len(self.cast) < 27:
            print('Cast list is too short, a new topic is selected.')
            self.change_topic()
        else:
            print("Topic is ok.")
            new_set = OrderedSet()
            hold_out_set = OrderedSet()
            for character in self.cast:
                position_bracket = character.find("(")
                position_slash = character.find("/")
                if position_bracket != -1:
                    short_character = character[0:position_bracket]
                    if len(short_character) > 25:
                        hold_out_set.add(short_character)
                    else:
                        new_set.add(short_character)
                elif position_slash != -1:
                    short_character = character[0:position_slash]
                    if len(short_character) > 25:
                        hold_out_set.add(short_character)
                    else:
                        new_set.add(short_character)
                else:
                    new_set.add(character)
            if len(hold_out_set) != 0:
                new_set.union(hold_out_set)

            self.cast = list(new_set)

    def change_topic(self):
        """
        If there is no wikipedia page for the selected topic
        or the number of entries in the character cast is too small for the monopoly field
        -> change the topic
        :return: void
        """
        self.topic = random.choice(list(self.cast_dict))
        self.cast = self.cast_dict[self.topic]
        self.get_wiki_data_for_topic()

    def get_wiki_data_for_topic(self):

        print("Selected topic is: ", self.topic)

        wiki_en_wiki = wikipediaapi.Wikipedia(
            language='en',
            extract_format=wikipediaapi.ExtractFormat.WIKI)

        ## check if page for topic exists
        if wiki_en_wiki.page(self.topic).exists():
            self.check_topic_cast()
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
        """
        - use Question Answering with roberta-base-squad2
        to get special locations from wikipedia data
        - Two questions per category are used,
        evaluation of answer is done based on score of
        qa-model, the answer with the higher score is selected

        :return: void
        """

        model_name = "deepset/roberta-base-squad2"
        model = AutoModelForQuestionAnswering.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        q_a = pipeline('question-answering', model=model, tokenizer=tokenizer)

        for category, question_body in self.question_dict.items():
            imd_response = []
            for question_item in question_body:
                question = question_item + self.topic + "?"
                print("Trying to find good locations ... ", question)

                QA_input = {
                    'question': question,
                    'context': self.topic_text
                }
                response = q_a(QA_input)
                print("This the candidate: ", response)
                ## store answer tuples in intermediate list
                imd_response.append((response["score"], response["answer"]))

            ## use answer with higher score
            if imd_response[0][0] > imd_response[1][0]:
                reply = imd_response[0][1]
            else:
                reply = imd_response[1][1]

            if category == "special_1":
                self.new_field["special"]["1"] = [reply]
            elif category == "special_2":
                self.new_field["special"]["2"] = [reply]
            else:
                self.new_field[category] = [reply]

        self.prison = self.new_field["prison"][0]

    def __store_locations(self):
        """
        flatten new_field dict into locations list
        """
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

        print("Generating basic locations ...")
        self.__generate_basic_locations()
        print("Basic locations done. Generation special locations ...")
        self.__generate_special_locations()
        print("Special locations done.")
        self.__store_locations()

    def keyword_generation(self):
        """
        The keyword list consists of a(n) randomly drawn
        - action verb from the orig monopoly data
        - additional action verb from the list
        - pronoun from the orig monopoly data
        - location of the current dimension
        - a fixed number or no number at all
        :return:
        """
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
        """
        gpt-neo api inference call for key-to-text generation
        :return:
        """
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
        """
        :param sent: sentence to preprocess
        :return: tuple (token, pos_tag) of the input sentence
        """
        sent = nltk.word_tokenize(sent)
        sent = nltk.pos_tag(sent)
        return sent

    def __pos_distribution(self, pos_tuples_of_sentence):
        """
        :pos_tuple_of_sentences: tuple (token, pos_tag) as returned from preprocess function

        crop pos tags into relevant groups (first two letters)
        count occurrences of pos tags in input sentence

        :returns: freq_df, pd.DataFrame with pos_tag and its frequency

        """
        pos_df = pd.DataFrame(pos_tuples_of_sentence, columns=["token", "long_pos_tag"])
        pos_df["pos_tag"] = [x[0:2] for x in pos_df["long_pos_tag"]]
        freq_df = pos_df["pos_tag"].value_counts()

        return freq_df

    def __eval_compare_structure(self, reference, new_sentence):
        """
        :param reference: str, the sentence the new action card should be compared to
        :param new_sentence: str, the newly generated action card candidate
        The structure of the two input sentences is compared via their pos
        distribution
        """
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
        """
        compare the length of reference against action card
        candidate
        """
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
        """
        apply the full evaluation
        """
        similarity_score = self.__eval_compare_structure(reference, new_sentence)
        len_score = self.__eval_compare_lengths(reference, new_sentence)

        score = self.__score_weighting(similarity_score, len_score)

        return similarity_score, len_score, score

    def __get_reference_for_sentence(self, location, sentiment):

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
        """
        :param action_card: generated action card
        evaluate the action the player has to do when an action
        card is drawn
        - check against locations and cast to find places
        - extract numbers
        :return: go_to_location (str), number (int)
        """
        ## search action card for locations
        for location in self.locations:
            ## exact matching for Start
            if location == "Start":
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

        ## search action card for character from cast
        for character in self.cast:
            if action_card.lower().find(character.lower()) != -1:
                imd_location = [string for string in self.locations if character in string]
                go_to_location = imd_location[0]
                break
            else:
                go_to_location = None

        ## if action card contains "prison", go to the current prison location
        ## same for station
        if go_to_location is None:
            if action_card.lower().find("prison") != -1:
                go_to_location = self.prison
            elif action_card.lower().find("station") != -1:
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

    def generate_action_cards(self, counter=0, number_of_cards=10):
        """
        :param counter: int, counter is only incremented if an action
        card candidate passed the evaluation test
        :param number_of_cards: int, the number of action cards that are
        generated when creating a new dimension, default is 10

        - keyword selection
        - action card generation via few shot learning
        - action card sentiment classification via few shot learning
        - reference action card selection
        - outer regularization
        - evaluation of action card against reference
        """


        ## stop generation of action cards
        if counter > number_of_cards:
            print("Generation of action cards completed.")
            return self.action_cards
        else:
            print("Generating action cards... ")
            print("Counter is: ", counter)
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
            # print("Sentiment analysis prompt: ", sent_prompt)
            sentiment = self.query(sent_prompt)
            # print(sentiment)
            action_sentiment = re.findall(r"(?<=Sentiment:\s).*", sentiment)[-1]

            print("Action sentiment is: ", action_sentiment)

            ## check sentiment
            if action_sentiment not in ["neutral", "positiv", "negativ"]:
                undefined_sentiment = True
            else:
                undefined_sentiment = False

            ## get reference
            reference = self.__get_reference_for_sentence(location, action_sentiment)
            print("The reference is: ", reference)

            ## evaluate action card against reference
            similarity_score, len_score, score = self.__eval_sentence(reference, action_card)
            # score = self.__eval_sentence(reference, action_card)
            print("The score for the action card is: ", similarity_score, len_score, score)
            ## outer regulator
            regulated = self.wordfilter.blacklisted(action_card)

            ## if action card OK, append
            if not regulated and not undefined_sentiment and score >= 0.5:
                location, number = self.__action_from_action_card(action_card)
                print("Sentiment, Location and number extracted: ", action_sentiment, location, number)
                self.action_cards.append((action_card, action_sentiment, location, number))
                counter += 1
                self.generate_action_cards(counter)
            else:
                print("Action card did not meet criteria, try again...")
                self.generate_action_cards(counter)





## dimension can be tested manually via
#new_dimension = Dimension()
#new_dimension.generate_locations()
#new_dimension.generate_action_cards()

