# zoom-participant-download

Downloads all participants in all Zoom meetings for the last 30 days.

To use:
* Install Selenium: `pip install selenium`
  - Will install webdriver automatically for Linux/Mac.
* Run `python zoom_participants.py` in project root.
* Log in to Zoom when Firefox opens (you must complete 2FA within 2
  minutes).
* Don't touch window after logging in (all scripted actions are
  visible in the browser).
* Browser closes automatically when finished.
* Participant lists are downloaded into `data/tmp`.

