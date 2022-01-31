# Computational Creativity Seminar, LMU, WS 2021/22

## Project Topic: Multidimensional Monopoly

### Creators: Laura Luckert & Shaoqiu Zhang

#### Project Description:
Following the example of the parlor game "Monopoly", a creative system is generating new dimensions for the Monopoly game every time a player passes "START". The new dimension represents a new thematic world in comparison to the classic Monopoly. 

#### Target:
The aim of the project is to develop a creative system that is following the concepts of computational creativity as taught in the seminar by Philipp Wicke. The creative system is generating new dimensions, locations and action cards for each monopoly round. For details about the functionality of the creative system, please refer to the handout provided in the seminar.

#### Components:
- Generation of a new dimension (Topic)
- Generation of new locations
- Generation of new action cards and their interpretation, i.e., the action the players have to take when drawing an "event card" or a "community card"
- Graphical representation of the game, dimensions incl. pictures, locations, action cards
- Simulation of the course of the game and the actions

#### Functionality of the Game:
- The game is started via a click on "start game" by the user
- Two players are playing multidimensional monopoly
- Each player starts with 2000 €
- The user can interact with the game by rolling the dices for both players
- Once Player 1 passes "GO" a new dimension is created, a new image is retrieved for the dimension and new locations and action cards are generated
- When passing "GO", the respective player receives 200 €
- The game ends if 
	- the user is clicking the "X" exit field
	- one of the two players has no money left and the other player wins the game. The user can decide if they want to continue: if continuing, both players are initialized with the starting amount of money and location ownership is reset
	- after 5 new dimensions have been created, the user can decide if they want to continue
- When a player is passing a location and this place is not owned by the other player yet, they are automatically purchasing the location
- If a place is already owned by one of the players and the other player passes the place, they must pay rent to the owner
- Once an action card is drawn, the action card is displayed and must be accepted by the user to proceed
- An action card will result in
	- the player is moving to the location named in the action card AND/OR
	- the player receives money (sentiment = positive, neutral) OR the player has to pay money (sentiment = negative)
	OR
	- no action, because no location was named in the action card and no amount of money was named


#### Resources used in the game:
- Movie Dataset: tmdb_5000_movies.csv.zip via https://www.kaggle.com/tmdb/tmdb-movie-metadata?select=tmdb_5000_movies.csv
- Action Verbs: (encoded in the file) via https://www.citationmachine.net/resources/grammar-guides/verb/list-verbs/
- Original Monopoly Action Cards: monopoly_action_cards_keywords.csv, the data was manually generated from the original monopoly game
- Wikipedia API via https://pypi.org/project/Wikipedia-API/0.3.5/
- Regularization via https://github.com/dariusk/wordfilter
- Key-to-Text Inference API: https://huggingface.co/blog/few-shot-learning-gpt-neo-and-inference-api


#### How To:
- Unzip the file tmdb_5000_movies.csv.zip to tmdb_5000_movies.csv
- Install all required packages listed in the requirements.txt
- The game can be started via main.py
- You can select whether to generate new dimensions or to load pre-generated dimensions. Set the variable load_from_save in main.py respectively
- The file dimensions_file.json contains 5 example dimensions for exploration 
- PLEASE NOTE: The generation of new dimensions is taking ca. 2 min, while waiting, check the console output for information what the creative system is computing in the back :-)
- dimension.py contains the development of the creative content in the game
- Due to the image API, for some topics there are no proper images found and in the map are no images displayed
- The folders contain the images that are needed to display the game

