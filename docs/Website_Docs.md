# Documentation giving an overview of the Website Implementation

The website uses flask as its main development structure. The majority of these files are stored in the app/ folder. Within the folder, there are four python files and a folder with webpage templates.

## Python files
**_init.py_**
\_init\_.py is the main file, which initialises the configuration of the whole website

**forms.py**
This file provides the format and required content of forms in the website, such as the registration and sign in pages. In these forms, the user interacts with the backend database.

**models.py**
This file describes how the database is structured, with key data types specified.

**routes.py** This file contains all of the functions that set up backend operations. It is the most important file as it describes the logic of the website. More specifically, it specifies what the result of a user’s action will be. When the user clicks a link on the website, this file specifies where they will be directed to. Also it specifies the accessibility of each user.

**templates\/\*** The templates folder contains all of the html files that serve as web page templates. These are what users will see, and they are directly linked with routes.py. The file names are very clear and directly indicate their purpose. The most important thing to note is the base.html file. This file provides the basic structure of parts of most of the pages. The idea behind this is that, because most web pages will share some basic features, it makes the design and implementation of the website much easier, and more organised. It will also maintain a level of consistency across the site, which will reduce the confusion of a user.
