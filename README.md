# Sport Items Catalog Project


Hello and welcome to the Sport Items Catalog Project! This project is created for users to log in the web application, create their own sport categories and then proceed to adding their own items in their respective niche.

To get this baby up and running, simply clone this project, <code> cd</code> into the directory you just cloned, and run <code> python views.py </code>. It should be noted that the port number is <code>5000</code>. Once that's done, head on to your favourite web browser and go to <code>localhost:5000/login</code>. 
![screen shot 2018-02-02 at 6 33 51 pm](https://user-images.githubusercontent.com/5374699/35759523-340bc8a4-0848-11e8-9319-d8474452ba94.png)

Login using your favourite social media platform and you'll be taken to the home page. In the home page, you'll see cards that display each individual category (created by users).
![screen shot 2018-02-02 at 6 33 07 pm](https://user-images.githubusercontent.com/5374699/35759521-32fb13ac-0848-11e8-81fa-4f774f594c5c.png)

It contains the name, description and a footer of different icons. If a category doesn't belong to you or you're not logged in, then it displays a block sign (seen below).
![screen shot 2018-02-02 at 6 32 40 pm](https://user-images.githubusercontent.com/5374699/35759520-308f58bc-0848-11e8-8ec3-4901179440fd.png)

However, if the card belongs to you and you're logged in, then it shows the edit/delete icon.
![screen shot 2018-02-02 at 6 31 58 pm](https://user-images.githubusercontent.com/5374699/35759515-2caacba0-0848-11e8-868b-68f9ae9d6261.png)

Clicking on the card title (name of the sport) will take you to a page where it display the sport's items. 
![screen shot 2018-02-02 at 6 32 21 pm](https://user-images.githubusercontent.com/5374699/35759519-305bf7c4-0848-11e8-88d6-16ea8ca9e4d2.png)

There, you can create your own cards and also edit/delete cards. It should be noted that while you can access a sports category's items page when you're logged out or if it doesn't belong to you, you can't add a new card 
Click at the plus sign on the top right corner to create a sports category or an item.



NOTE: You must install the right packages in order for this to work:
<ul>
  <li><a href="https://pypi.python.org/pypi/Flask">Flask</a></li>
  <li><a href="https://www.sqlalchemy.org/download.html"> SQLAlchemy </a> </li>
  <li><a href="https://github.com/google/oauth2client"> OAuth2.0</a></li>
</ul>


This repository is
meant to be open-source, so you can fork it, make your own modifications and request to pull it back. We can then discuss whether it is a good feature to be uploaded, or not!
