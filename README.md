# getVideos
This script checks for new YouTube videos for all bookmarks found in a Firefox bookmarks folder.

## Getting Started
Place this script in its own folder. When run it will create 2 files.
  - oldContent.txt
  Contains tab delimited data of all the videos the script found in the last run. It is used on the next run to determine if a video is considered new.
  
  - index.html
  Contains possible links for all new videos. Has emulated link visited history that works in private browsing mode and does not require scripts.

Create a bookmarks folder in Firefox called "videos" and add YouTube bookmarks, for example
  https://www.youtube.com/@jawed/videos

Find and set your Firefox binary location, for example
  firefoxBinary = r'C:\Program Files\Mozilla Firefox\firefox.exe'

Find and set your Firefox profile folder, for example
  firefoxProfile = r'C:\Users\Jesse\AppData\Roaming\Mozilla\Firefox\Profiles\7yr6lvv1.default-release'

## Prerequisites
Python, Firefox, Selenium, geckodriver

## License
This project is licensed under the Apache License, Version 2.0. See the LICENSE file for details.

## Acknowledgements
- This project uses Selenium WebDriver, which is licensed under the Apache License, Version 2.0.
https://www.selenium.dev/

- Geckodriver, which is licensed under the Mozilla Public License, is required to run Selenium WebDriver with the Mozilla Firefox browser.
https://github.com/mozilla/geckodriver
