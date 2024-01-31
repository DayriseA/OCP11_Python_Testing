# gudlift-registration

## 1. Why

This is a proof of concept (POC) project to show a light-weight version of our competition booking platform. The aim is the keep things as light as possible, and use feedback from the users to iterate.

## 2. Getting Started

This project uses the following technologies:

* Python v3.x+

* [Flask](https://flask.palletsprojects.com/en/1.1.x/)

    Whereas Django does a lot of things for us out of the box, Flask allows us to add only what we need. 

* **Tests packages and plugins:**  
    pytest, pytest-flask, pytest-cov, selenium, coverage, locust
    

* [Virtual environment](https://virtualenv.pypa.io/en/stable/installation.html)

    This ensures you'll be able to install the correct packages without interfering with Python on your machine.

    Before you begin, please ensure you have this installed globally. 


## 3. Installation

- After cloning, change into the directory and type <code>virtualenv .</code>. This will then set up a a virtual python environment within that directory.

- Next, type <code>source bin/activate</code>. You should see that your command prompt has changed to the name of the folder. This means that you can install packages in here without affecting affecting files outside. To deactivate, type <code>deactivate</code>

- Rather than hunting around for the packages you need, you can install in one step. Type <code>pip install -r requirements.txt</code>. This will install all the packages listed in the respective file. If you install a package, make sure others know by updating the requirements.txt file. An easy way to do this is <code>pip freeze > requirements.txt</code>

- Flask requires that you set an environmental variable to the python file. However you do that, you'll want to set the file to be <code>server.py</code>. Check [here](https://flask.palletsprojects.com/en/1.1.x/quickstart/#a-minimal-application) for more details

- You should now be ready to test the application. In the directory, type either <code>flask run</code> or <code>python -m flask run</code>. The app should respond with an address you should be able to go to using your browser.

## 4. Current Setup

The app is powered by [JSON files](https://www.tutorialspoint.com/json/json_quick_guide.htm). This is to get around having a DB until we actually need one. The main ones are:
    
* competitions.json - list of competitions
* clubs.json - list of clubs with relevant information. You can look here to see what email addresses the app will accept for login.

*N.B. If you want to run this POC and try to book some places, make sure there is at least one competition with a date in the future.*

## 5. Testing

### Unit & integration tests:

To run all the unit and integration tests just run `pytest --ignore=tests/functional_tests`  
*N.B. Check the **Functional tests** section below before running a global `pytest`*

### Functional tests:

We use Selenium to run our functional tests. Starting from version 4.6.0 (November 4, 2022) selenium comes with Selenium Manager packed in distribution. You can read the details in the [documentation](https://www.selenium.dev/documentation/selenium_manager/).  

So if you don't want to have Firefox and/or its webdrivers installed or if the Selenium Manager does not work as intended (after all it's still in beta while these lines are written), make sure to modify the following line from *tests/functional_test/test_server.py* to better fit your needs:  
`self.driver = webdriver.Firefox()` into `self.driver = webdriver.Chrome()` for example.

Also, due to some unresolved incompatibility bug since Python 3.8, we are not using **live_server** fixture and you will need to start the flask server manually before running a selenium test. (same issue with *Flask-Testing* package and its *LiveServerTestCase*) 

All context now clarified, to run the functional tests, simply run `pytest tests/functional_tests/`

Of course you can also run all these tests with a simple `pytest` command


### Checking coverage:

The *.coveragerc* at the root of the project is configured to omit the **tests** folder from the analysis.  
Thanks to *pytest-cov* you can check the coverage with: `pytest --cov=. --ignore=tests/functional_tests/`  
If you want to generate an html report, use the `--cov-report html` option.  

N.B. You can also do it using coverage like this: `coverage run -m pytest --ignore=tests/functional_tests`


### Performance tests:

1. Make sure you have your flask app running (see the last two points of **3. Installation** section).
2. In an other terminal run `locust -f tests/performance_tests`
3. Go to the address given in your terminal, usually http://localhost:8089
4. Configure your load test parameters and in the *Host* field enter the address of your flask server, usually http://127.0.0.1:5000  
*Note that, in some cases, using 'localhost' instead of '127.0.0.1' causes some noticeable delays*

