# referral
An application for users to give each other referrals.


## Requirements:
Rather than a blog I require a business referral platform so the post would be a referral (exactly the same just named referral rather than post), the functionality would be the same as a blog but some of the titles and wording will be slightly different.

Functionality:

[x] A detail view to show a single post/referral. Click a post’s title to go to its page.

[ ] Request a post/referral (similar to a Like / unlike button but just named request), delete original request.

[ ] Comments. [Does this need to be shown in detailed view?]

[ ] Tags. Clicking a tag shows all the posts with that tag. [Need clarification: are tags predefined?]

[ ] A search box that filters the index page by member name. [Should search only accept usernames?]

[x] Paged display. Only show 5 posts per page.

[ ] An RSS feed and email alert of new posts, opt-in/out via members page.

[ ] A members details page, which will include how many posts a particular member has made and also how many requests (likes) they have made and been awarded. With a description box about the member.

[ ] An 'awarded too' button on each post. [Need clarification, where will this be displayed, what is the functionality?]

[x] When expanded an individual post is to show what members have requested the post with a click through link to each individual members page. i.e. a user can click on a post title, this will take them to a detailed view of the post and on that page there will be a list of members that have requested that post with the members names being a click through to there individual member details page. (Still need to implement comments/tags/request for the post)

[x] The post box is to have five input areas: 1) Referral Title, 2) Employee #, 3) Annual Turnover, 4) Project date, 5) Budget, 6) Description (description is a larger text input box than the others).

The code is to be all in Python using Flask and Jinja2 and uploaded to a Git repository. Also needs to be deployed via pythonanywhere using a free account (or another hosting provider) so that the functionality can be seen to work. Needs to be viewable on both desktop and mobile. Web-app rather than specific mobile app.

This is only a MVP so just requires the above functionality to work, doesn’t need to look perfect and polished.
