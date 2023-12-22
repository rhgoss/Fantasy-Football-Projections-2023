# Fantasy-Football-Projections-2023

## Project Description
This project was based upon the old saying "The house always wins". In order to give myself an edge in my fantasy football leagues, I scraped data (fantasy_football_scrape.py) from DraftKings.com and ESPN.com to create improved player projects based on a player's season projections from a major sportsbook. Instead of relying on ESPN's projections to draft like many people do, I built a stronger projection based on a major sportsbook's player projections and using ESPN data when that data was unavailable. Sportsbooks make their money by accurately predicting outcomes, so by using their projections I was able to capitalize on that to gain an edge over my competition. Once the data was collected, I built an RShiny (ff_shiny.R) drafting dashboard so I could make real time decisions during the draft using my scraped data.

## Table of Contents
### fantasy_football_scrape.py
This is where I completed all the scraping from DraftKings.com and ESPN.com and uploaded the data into a PostgreSQL database.

### ff_shiny.R
Contains the code to access the PostgreSQL database where the data was stored and to run the RShiny application. 

## Note
Much of this code would still run if ran on another computer, certain aspects would need to be updated, however. For example, the code is currently written to upload/retrieve data from my local database and that would need changed.
