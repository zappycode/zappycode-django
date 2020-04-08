How to run zappycode locally and contribute to it?

DISCLAIMER: Following steps are for WINDOWS and Anaconda installed
	    but procedure for different setups is similar. 

1. There must be a "Fork" button in the top right corner of Github page.
	This creates a new copy of my demo repo under your GitHub user account with a URL like:
	https://github.com/<YourUserName>/django3-todowoo-project

2.Next, clone the repo by opening the Anaconda prompt on your computer and running the command:
	git clone https://github.com/<YourUserName>/django3-todowoo-project

3.Once the repo is cloned, you need to do two things:
	Create a new branch by issuing the command:
		`git checkout -b new_branch`
		(name it whatever you like. Here, it is new_branch)
	Create a new remote for the upstream repo with the command:
		git remote add upstream https://github.com/<your username>/django3-todowoo-project

4.Make a virtual environment using- conda create --name zappycodeenv python=3.6.9
  If virtual environment isn't activated automatically, enter: conda activate zappycodeenv

5. Install requirements:-
   The Pipfile and Pipfile.lock contain dependencies. Read https://www.jetbrains.com/help/pycharm/using-pipfile.html
   to know how to use them to install dependecies. If that doesn't work, do as directed below:
	
	0)If you don't have pipenv, install it using `pip install pipenv`
	1)Enter: `pipenv lock -r` (You need to be present in the zappycode directory!)
	2)When it says "Successfully created virtual environment!"
	  copy and paste Everything below virtualenv location in a text file and save it in the zappycode project cloned folder
	  by the name requirements.txt.
	3)Enter: `pip install -r requirements.txt` in shell. 

	Run the server using `python manage.py runserver`, open a browser and go to http://127.0.0.1:8000/ or localhost:8000

6. Now you can make changes to the code.

7. Push it! `git push -u origin new_branch`

8. Once you push the changes to your repo, the Compare & pull request button will appear in GitHub. Click it!

9. Add some info about the changes you made and click 'Create pull request' button.

10. Done!
