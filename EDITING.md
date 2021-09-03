# Editing Open English WordNet

This document contains guidelines for making changes to Open English WordNet and fixing issues using GitHub and the English WordNet Editor (EWE)

You should take the following steps to implement a change in the resource

## Fork the repository

_This is not necessary if you have the rights to change the repository directly. You only need to do this once_

Choose the 'fork' option in the top right hand corner of the screen. Follow the instructions and you will have a new version of the repository at https://github.com/EXAMPLE/english-wordnet where `EXAMPLE` is your GitHub ID.

## Choose an issue

Choose one of the issues from the [issue list](https://github.com/globalwordnet/english-wordnet/issues). If there is not an issue yet, please first report an issue before making any changes.

## Create a branch for the issue

Create a new branch for the issue which would normally be called `issue-XXX` where `XXX` is the issue number. 

### On the command line
    git checkout -b issue-XXX master
    
### Using GitHub Desktop
![GitHub Desktop Create New Branch Dialog](https://github.com/globalwordnet/english-wordnet/raw/ewe-doc-images/new-branch-wordnet.PNG)

## Implement the change using EWE

You can start EWE with the command

    python scripts/ewe.py
    
Alternatively, on Windows, by running the `ewe` script in the root folder of the repository.

You may need to install the `autocorrect` module using [PIP](https://docs.python.org/3/installing/index.html)

If successful, you should see the EWE interface like this:
![EWE Interface](https://github.com/globalwordnet/english-wordnet/raw/ewe-doc-images/ewe-interface.PNG)

EWE is a menu-driven application. Please choose the relevant changes and save the results

## Commit the changes

You should verify and commit the changes made to the files. Please provide a readable title for the change and include a [GitHub keyword](https://docs.github.com/en/github/managing-your-work-on-github/linking-a-pull-request-to-an-issue) to close the issue.

### Command line

    git commit -a
    
### Using GitHub Desktop

![An example commmit for an issue](https://github.com/globalwordnet/english-wordnet/raw/ewe-doc-images/commit.png)

## Push the changes and create a merge request

Push the changes to GitHub using the 'publish' option on GitHub desktop or by the command

    git push
    
Then [create a new pull request on GitHub.com](https://github.com/globalwordnet/english-wordnet/compare)
