# script.tagoverview
JAN 20 2021
Updated for Kodi Matrix (python3), no backwards compatibility included.

========================================

Reviving and updating the Tag Overview created by olivaar.   A way to manage tags in Kodi.  You can put this in your keymap to run the script by pressing the t key: &lt;t&gt;RunScript(script.tagoverview)&lt;/t&gt;

Or this using JSON:

jsonrpc?request={"jsonrpc":"2.0","method": "Addons.ExecuteAddon", "params": { "addonid": "script.tagoverview"}, "id": 1 }

A tip if using MYSQL:
>
>Download mysql-connector-python-8.0.17.tar.gz Source from 
>https://pypi.org/project/mysql-connector-python/#files
>copy from zip only folder ../lib/mysql/*.* to ../addons/script.tagoverview/mysql
>
>Add database parameters in CDatabase.py
>under
>class CDatabase:
>
>    baseconfig = {
>    }
>
>Add database parameters in MySQLconfig.py
>under
>class Config(object):

## To make the tagoverview addon functional in Kodi v17 & v18 (Krypton & Leia):

* Accounted for 3 digit database numbers (MyVideos116.db)
* Replaced deprecated functions (e.g. StringCompare)
* Replaced .xml language file with .po
* Smaller UI updates

## Additional improvements:
* Added mouse support (previously selection could only occur with Enter button).  
* Added support for stacked movies (e.g. disk1, disk1) (previously would open Overview instead of tag selector) 
* Updated sorting.  Put selected tags on top of list.  Alphabetized movie/show lists (still doesn't account for articles or sort titles)
* Added context menu, under Manage, for people who don't want to map to a button.  
* Added delete confirmation when deleting entire tag.
* Put Tag name on movie/show window header when adding to a tag from the Overview screen.

## Notes / warnings:
* Not tested in Jarvis or earlier.  Probably won't work due to 2 digit database numbers.
* Also not tested in Matrix.
* The addon was originally coded for Confluence skin and matches that style.  Should still work in other skins (tested in Estuary).
* Be careful when using mouse to select.  If you moved your mouse quickly before the next menu appears, selection may have changed.
* I'm not an experienced coder, so use at your own risk.
