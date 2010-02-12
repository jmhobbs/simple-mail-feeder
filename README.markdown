# What?
Simple Mail Feeder, or SMF, is a Python tool to feed RSS to your e-mail (or actually to lots of e-mails).  It's simple and unobtrusive.

# Why
I personally need it.

I love existing solutions like [feedmyinbox](http://www.feedmyinbox.com/pricing/) but I **don't** want to pay for something this basic (I know, I'm cheap) and I **do** need better than once a day updates.

[RSSFwd](http://rssfwd.wordpress.com/) was a good option, but they couldn't afford to run it for everyone. This way everyone can have speedy delivery and just use their own resources.

# Usage

* Install it somewhere.
* Run manage.py
  * Create config file
  * Create database
  * Create first user
* Run server.py
* Visit http://localhost:8080/
* Enjoy

# Requirements

* [web.py](http://www.webpy.org/)
* [bcrypt](http://www.mindrot.org/projects/py-bcrypt/)