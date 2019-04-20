# referral
An application for users to give each other referrals.

## Deployment instructions:
- Create a virtualenv using Python3:
  ```
  $ virtualenv -p /usr/bin/python3 venv
  $ source venv/bin/activate
  ```
- Install requirements.
  ```
  (venv)$ pip install -r requirements.txt
 if above does not work try
  sudo python -m pip install -r requirements.txt

  ```
- Edit `settings.py` to specify the database, posts per page and default tags.
  ```pytohn
  DB_URL = 'sqlite:///database.db'  # Refer to SQLAlchemy documentation to use a different database.
                                    # SQLite will work out of the box
  post_limit = 5
  tags = ["tag_1", "tag_2", "tag_3"]
  ```
- Build database and models and insert initial data.
  ```
  (venv)$ cd referral
  (venv)$ python models.py
  // A default user called test will be created (username:test, password:test)
  ```

- On a different terminal, run the mail alerting service
  ```
  (venv)$ python mail.py
  // Keep the terminal open, or optionally use `python mail.py &` to run in the background
  ```

- Run the server using gunicorn:
  ```
  (venv)$ gunicorn --workers 5 --timeout 60 --bind 0.0.0.0:8088 app:app
  // App should be up and running on http://localhost:8088, if there is a public IP for your server, you can access at http://[public_hostname]:8088
  // You can change the workers/timeout(secs)/host/port accordingly
  ```

- [Optional] You can also run the server in debug mode, to see live changes made to the code
  ```
  (venv)$ python app.py 0.0.0.0 8088
  // App should be up and running on http://localhost:8088 in debug mode
  ```

## Current Functionality:
- A detail view to show a single post/referral. Click a post’s title to go to its page.

- Request a post/referral (similar to a Like / unlike button but just named request), delete original request.

- Comments. Needs to be on the ‘detail view’ as well.

- Tags. Clicking a tag shows all the posts with that tag.

- A search box that filters the index page by member name.

- Paged display. Only show 5 posts per page.

- An RSS feed and email alert of new posts, opt-in/out via members page.

- A members details page, which will include how many posts a particular member has made and also how many requests (likes) they have made and been awarded. With a description box about the member.

- An 'awarded too' button on each post.

- When expanded an individual post is to show what members have requested the post with a click through link to each individual members page. i.e. a user can click on a post title, this will take them to a detailed view of the post and on that page there will be a list of members that have requested that post with the members names being a click through to there individual member details page.

- The post box is to have five input areas: 1) Referral Title, 2) Employee #, 3) Annual Turnover, 4) Project date, 5) Budget, 6) Description (description is a larger text input box than the others).

## Possible additional improvements:
- A proposal added along with each request to help user decide who the referral must be awarded to.
- A point based rating system, that rates users based on their referrals, experience, etc. This will help users choose which referrals to request and which to not.
- A more general search for posts based on keywords rather than username. This should be able to handle complex queries, like matching words with similar meaning rather than a simple text to text matching.
- A better UI design using bootstrap templates to make the website user friendly and eye appealing on all devices.
- Profile pictures, resumes, work experience on the user profile page that tells us more about a given user.
- A reccomendation system to recommend other users for referrals you may think they will be interested in.
- User chat for users to communicate one to one on the website rather than just through comments
- Location based referrals that allow only users in the same geographical location to be able to request.(Useful for referrals that require local users)
- Referral expiry to automatically remove outdated referrals.
- Optimisation of database models and access for faster responses. Would be useful when application is scaled to a large user base. 
