# referral
An application for users to give each other referrals.


## Requirements:
Rather than a blog I require a business referral platform so the post would be a referral (exactly the same just named referral rather than post), the functionality would be the same as a blog but some of the titles and wording will be slightly different.

Functionality:

[x] A detail view to show a single post/referral. Click a post’s title to go to its page.

[x] Request a post/referral (similar to a Like / unlike button but just named request), delete original request. [Implemented as like button, same button to unlike]

[x] Comments. Needs to be on the ‘detail view’ as well. [Done, there is also an option to delete your comments]

[x] Tags. Clicking a tag shows all the posts with that tag. [Done, with pagination for search results. Tags are predefined, author of the post can assign a tag from Dropdown list. You can define using tags in settings.py. Tags can also be removed. Only one tag allowed for a post.]

[x] A search box that filters the index page by member name. [Accept usernames, done with pagination for results]

[x] Paged display. Only show 5 posts per page. [Can be changed with page_limit argument in settings.py]

[ ] An RSS feed and email alert of new posts, opt-in/out via members page. [Pending]

[x] A members details page, which will include how many posts a particular member has made and also how many requests (likes) they have made and been awarded. With a description box about the member. [Only description box is editable.]

[x] An 'awarded too' button on each post. [Dropdown list viewable only by the author of the post, selected user from the list will award that post to that user. List contains only users that have requested the post. Can unaward too. Other users only see an awarded section if post is awarded to some user.]

[x] When expanded an individual post is to show what members have requested the post with a click through link to each individual members page. i.e. a user can click on a post title, this will take them to a detailed view of the post and on that page there will be a list of members that have requested that post with the members names being a click through to there individual member details page. [All mentions of usernames are clickable links. Comments, tags]

[x] The post box is to have five input areas: 1) Referral Title, 2) Employee #, 3) Annual Turnover, 4) Project date, 5) Budget, 6) Description (description is a larger text input box than the others).

The code is to be all in Python using Flask and Jinja2 and uploaded to a Git repository. Also needs to be deployed via pythonanywhere using a free account (or another hosting provider) so that the functionality can be seen to work. Needs to be viewable on both desktop and mobile. Web-app rather than specific mobile app.

This is only a MVP so just requires the above functionality to work, doesn’t need to look perfect and polished.
