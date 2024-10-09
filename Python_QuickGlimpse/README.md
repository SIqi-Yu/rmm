# Quick Glimpse
## Members:
xunyil - Xun Yi Lim

<andrew-id> - Taiyuan

<andrew-id> - Santiago

<andrew-id> - Siqu


### Running the Project
The `attraction_scraper` and `airbnb` uses **Selenium** which requires installing a `ChromeDriver`. In both files, there is a variable `CHROME_DRIVER_PATH` at the top of the file that must be set to wherever the driver is downloaded. Ensure that the driver has permissions too. On a Mac, this involves

```
chmod 755  /opt/homebrew/bin/chromedriver
xattr -d com.apple.quarantine /opt/homebrew/bin/chromedriver
```
After the `ChromeDriver` has been installed, follow the steps below to run the application.

```
pip3 install -r requirements.txt
python3 main.py
```

This should open up a `Tkinter` GUI. The search currently works for the following cities: ` dallas, new york, los angeles, chicago,  houston, phoenix, philadelphia，san antonio，san diego`. Sometimes, the AirBNB listing website might be down and you will have to try to scrape again.

Fill in the text input with one of the above and click submit. After a brief moment, Chrome browsers will pop up. If the `Scrape from online` option is selected, it will take a brief moment.

