# Badminton Tracker
Badminton Tracker is a web app that tracks court signups in real time. \
Current build (for testing): local database, locked current time at "2024-11-06 22:46:00".

## Drag and drop to reserve
Once signed in, your name shows up in the Player Bank, as long as you have not signed up for a currently live court yet.
![Badminton Tracker: Session Page](/resources/badminton-tracker.png)

### Tech Stack
Backend: Python, Flask, SQL \
Frontend: JavaScript, Node, React

## Why Badminton Tracker?

In New York City, free badminton open-play is available at a few Recreation Centers. The current way of maintaining equitable play for attendees is as follows:
* Players may sign their names on a list, when not playing
* Every 15 minutes, an alarm goes off
* The next 16 players on the list play for the next 15 minutes

### The Problem
Equitable play is rarely enforceable:
* Whoever runs faster or ends their game closer to the clipboard is able to sign up for an earlier slot and consistently play more often
* Players often sign 4 names at a time on the clipboard (those who they want to play with on the same court). This means even if you are 5th in line, you may not be able to play at all in the next interval - you would wait two intervals (30 minutes) before playing again. This happens **repeatedly** over the course of a session - certain players play every other interval, where others play every three intervals.

### Reframing the Problem of Equity
If 32 players show up to a session, each player can play exactly 50% of the time. If 24 players show up, each player plays 67% of the time (play 2 intervals, wait 1).

### Intended Use
Badminton Tracker is built to be an tool that members **want** to opt-into; "I am happy to play my fair share of time and want for others to have the same opportunity." A player's `play_density` is not the focus of attention - it is hidden by default. \
\
Imagined use case: \
Player A (who has played 1/3 intervals) says to Player B (who has played 2/3 intervals), "Excuse me, I noticed my `play_density` is 33%, but your `play_density` is 67%. I was unable to sign up for next interval, but you did, which would make my `play_density` 25% and yours 75% after next interval. Can I take your place for the next interval?" If I were Player B, I am happy to let Player A play in my place if it upholds the ideal integrity of our open-play.

### Extending Badminton Tracker
* Suggested signup priority queue - also using past session data (e.g. last session, this player was unlucky and only played 30 / 75 minutes they were present)
* iPad touch support - intuitive for senior players
* iPhone Apple Wallet RFID sign-in - seamless experience
