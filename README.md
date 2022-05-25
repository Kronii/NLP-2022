# NLP-2022

[Report](https://github.com/Kronii/NLP-2022/blob/main/report/NLP_2022_final.pdf)

User engagement prediction implementation using deep learing and NLP approaches.

## Installation

Move to `src` directory.

```
$ cd src
```

Create python virtual environment and install requirements.
```
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install -r ../requirements.txt
```

Then download chromedriver from [https://chromedriver.chromium.org/](https://chromedriver.chromium.org/) for selenium web scraper and put it inside `./src` directory.

## Structure

The structure of the project is as follows:

`./src` includes all source files of our models

`./report` includes final [report](https://github.com/Kronii/NLP-2022/blob/main/report/NLP_2022_final.pdf)

`./data` includes data used for our project

> The data and **final trained model** can be accessed also [here](https://drive.google.com/drive/folders/1aQNp4dg_CT_keet5G0OvugG3JYXEMJkT?usp=sharing).

The source of our project (located in directory `./src`) consists out of three main categories:

1. Scrapers (`./src/scrapers`) - Scripts that we used for retrieving the data
2. Parsers (`./src/parsers`) - Scripts used to parse the raw data into usable form
3. Models (`./src/models`) - Prediction models