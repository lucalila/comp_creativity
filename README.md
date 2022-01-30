# Computational Creativity Seminar, LMU, WS 2021/22

## Project Topic: Multidimensional Monopoly

### Creators: Laura Luckert & Shaoqiu Zhang

#### Project Description:
Following the example of the parlor game "Monopoly", the dimensions of the Monopoly changes with every "passing GO" of a player. The new dimension represents a new thematic world in comparison to the classic Monopoly. 

#### Target:
The aim of the project is to develop a creative system that is following the concepts of computational creativity as thaugt in the seminar by Philipp Wicke. The creative system is generating new dimensions, locations and action cards for each monopoly round. For details about the functionality of the creative system, please refer to the handout provided in the seminar.

#### Components:
- Generation of a new dimension (Topic)
- Generation of new locations
- Generation of new action cards and their interpretation, i.e., the action the players have to take when drawing an "event card" or a "community card"
- Graphical representation of the game, dimensions incl. pictures, locations, action cards
- Simulation of the course of the game and the actions

#### Functionality of the Game:
- The game is started by the user via a click on "start game"
- Two players are playing multidimensional monopoly
- Each player starts with 2000 €
- The user can interact with the game by rolling the dices for both players
- Once Player 1 passes "GO" a new dimension is created, a new image is retrieved for the dimension and new locations and action cards are generated
- When passing "GO", the respective player receives 200 €
- The game ends if 
	- the user is clicking the "X" exit field
	- one of the two players has no money left and the other player wins the game. The user can decide if they want to continue: if continuing, both players are initialized again with the starting amount of money and location ownership is reset
	- after 5 new dimensions have been created, the user can decide if they want to continue
- When a player is passing a location, they are automatically purchasing the location if the other player does not own the place yet
- If a place is already owned by one of the players and the other player passes the place, they must pay rent to the owner
- Once an action card is drawn, the action card is displayed and must be accepted by the user
- An action card will result in
	- the player is moving to the location named in the action card AND/OR
	- the player receives money (sentiment = positive) OR the player has to pay money (sentiment = negative)
	OR
	- no action, because no location was named in the action card and a neutral sentiment was classified


#### Resources used in the game:
- Movie Dataset: tmdb_5000_movies.zip via https://www.kaggle.com/tmdb/tmdb-movie-metadata?select=tmdb_5000_movies.csv
- Action Verbs: (encoded in the file) via https://www.citationmachine.net/resources/grammar-guides/verb/list-verbs/
- Original Monopoly Action Cards: monopoly_action_cards.csv, the data was manually generated from the original monopoly game
- Wikipedia API via https://pypi.org/project/Wikipedia-API/0.3.5/
- Regularization via https://github.com/dariusk/wordfilter
- Key-to-Text Inference API: https://huggingface.co/blog/few-shot-learning-gpt-neo-and-inference-api


#### How To:
- The requirements.txt contains the packages used in the project
- The game can be started via main.py
- PLEASE NOTE: The generation of new dimensions is taking ca. 2 min, while waiting, check the console output for information what the creative system is computing in the back :-)
- The file dimensions_file.json contains 5 example dimensions for exploration 
- dimension.py contains the development of the creative content in the game
- The folders contain the images that are needed to display the game

