# Master Thesis archive: "A social network for philatelist"

## Introduction

This project is an archive of my MSc dissertation and related source code.
While I do not have much use of this project myself, I hope that sharing my observations/source code could help some future students working on similar project.


## The dissertation

This project involved building a simple website allowing management and trading of stamps collection between users, with an image matching mechanism to facilitate identification and classification of stamps previously unknown to the user.

While the main topic might not appear glamorous in the tech community, the idea was to play around with various reverse image retrieval algorithms selected through literature review (final benchmark including SIFT, SURF, ORB, BRISK and FREAK), in aim to test and analyze efficiency and tolerance to defects.
The website was built using Python and Django; stamps image database was gathered via web-scraping of specialized websites (Scrapy), while the various images matching algorithms implementations were done with the help of OpenCV.


## Side-notes

Feel free to judge me on the ugly looking interface on this project, looking into it a few years later I also judge myself... The focus was to get the features in, since this is what a dissertation is graded on ;)


## Licenses

The dissertation document is licensed under the [Creative Commons Attribution 4.0 license](https://creativecommons.org/licenses/by/4.0/), while the source code itself is released under [The Unlicense](http://unlicense.org/).
