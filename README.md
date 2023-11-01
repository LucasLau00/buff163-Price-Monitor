This is a personal for fun project made for website https://buff.163.com that is a website that sells CSGO/CS2 skins.
I made this to monitor for price changes there are definitely some flaws which could be easily fixed.

If the max_workers threads are increased too much it is possible where it would get rate limited from the api.
Make sure to change the paths of the files and add necessary webhooks and image links.

Example of commands:
ItemLink: https://buff.163.com/goods/42986
Using !add 42986 will store it into the txtfile and the json file
Using !rem 42986 will remove it from the txtfile and remain stored in json file
Using !show will list all the IDs being monitored for price changes
Using !file will send the entire json file.
