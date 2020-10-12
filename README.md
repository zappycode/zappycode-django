  
# ![](sitewide/static/sitewide/ZappyCodeLogoMini.png) ZappyCode - Coding is Fun
Learning to code should also be fun. That's why we built Zappycode! A community of learners that don't like doing things the boring way. Join and see what it's all about. 

## Issues
Feel free to submit issues and enhancement requests under the issues tab. 

## Contributing
Zappycode welcomes contributions from the community and is an open source project. When contributing please be kind and respectful. In general, we follow the "fork-and-pull" Git workflow.

1. **Fork** the repo on Github, top right-hand corner.
2. **Clone** the project to your own machine.
`git clone https://github.com/<yourusername>/zappycode-django.git`
3. **Commit** changes to your own branch
Create a new branch:
`git checkout -b new_branch`
Create a new remote for the upstream repo:
`git remote add upstream https://github.com/<your username>/zappycode-django`
4. **Push** your work back up to your fork
`git push -u origin new_branch`
5. Submit a **Pull Request** so that we can review your changes.

### Windows: How to run zappycode locally?

1. **Fork** the repo on Github, top right-hand corner.
	This creates a new copy of my demo repo under your GitHub user account with a URL like: https://github.com/<YourUserName>/zappycode-django

2. **Clone** the project to your own machine.
	`git clone https://github.com/<YourUserName>/zappycode-django`

3. **Commit** changes to your own branch
	Create a new branch:
		`git checkout -b new_branch`
		(name it whatever you like. Here, it is new_branch)
	Create a new remote for the upstream repo:
		`git remote add upstream https://github.com/<your username>/zappycode-django`

4. Make a **Virtual Environment** using- `conda create --name zappycodeenv python=3.6.9`
  If virtual environment isn't activated automatically, enter: `conda activate zappycodeenv`

5. Install **Requirements**:-
   The Pipfile and Pipfile.lock contain dependencies. Read [pipfiles](https://www.jetbrains.com/help/pycharm/using-pipfile.html)
   to know how to use them to install dependecies. If that doesn't work, do as directed below:
	
	1) If you don't have pipenv, install it using `pip install pipenv`

	2) Enter: `pipenv lock -r` (You need to be present in the zappycode directory!)

	3) When it says "Successfully created virtual environment!"
	  copy and paste Everything below virtualenv location in a text file and save it in the zappycode project cloned folder by the name of requirements.txt.

	4) Enter: `pip install -r requirements.txt` in shell. 

6. Now you can make changes to the code.

7. **Push** it! `git push -u origin new_branch`

8. Once you push the changes to your repo, the compare & pull request button will appear in GitHub. Click it!

9. Add some info about the changes you made and click 'Create pull request' button.

10. Done!

### Mac: How to run zappycode locally?

Make sure **Python v3.6.9** is installed on your machine. Already have a version installed? See [here](https://realpython.com/intro-to-pyenv/) for help. 

1. Follow :page_with_curl:**Steps 1 - 3** under contributing.
2. Setup :computer:**Virtual Environment** inside the zappycode working directory.
* run `pipenv install` in your terminal to setup the venv.
* then `pipenv shell` to activate the venv.
* to deactivate the venv run `exit`
3. Start **Contributing**! :smiley:
4. :rocket:**Push** your work back up to your fork
`git push -u origin new_branch`
* Click the create pull request link in terminal.
* Add some info about your changes
* Submit pull request
5. :tada:Done! **You're Awesome**:star:
