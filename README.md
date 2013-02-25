<http://serendipityengineapp.com>

Your personal travel assistant!

Recommends personalized one day itineraries for tourists (like me). Leverages geotags found on Flickr and your recent Facebook likes. Extracts tourist paths from Flickr's geotags, scrapes sights from Lonley Planet, uses latent semantic indexing to match sight descriptions to your Facebook likes, and eventually creates a personalized 6h itinerary that maximes time at your fav sights and minimizes (squared) walking time between sights.

Outline

- `app` contains the Flask app 
  - `my_facebook.py` counts words in a user's 30 most recently liked urls 
	- `my_ranking.py` uses latent semantic indexing to create personalized ranking of sights
	- `my_routing.py` uses a combo of shortest path and random walk to generate itineraries
- `scripts` contains Ruby and Python scripts for 
	- downloading data, 
	- scraping data, and 
	- data munging 