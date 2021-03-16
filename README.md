# wikirender
Provides jinja templates to create wiki page files form JSON input
## Install
```json
python setup.py install
```
check if it worked with
```
wikirender -h
```

### Example Pipeline
For example, we have a json file with information about events with which we want to update the Event templates in the wikibackup.
```
cat test.json | wikirender -t Event -id Acronym -stdin --BackupPath "."
```
The data is provided to wikirender through *stdin* and updates the template *Event* with the provided data.
As page name the key *Acronym* is used.
The update to the templates is applied to the files as shown in the diagram below.

![](docs/figures/event_update_example.png)
#### Sample Input Data
```json
{
    "data":
    [
        {
            "Acronym": "SMWCon 2020",
            "Title": "SMWCon",
            "Year": "2020",
            "Description": "test value"
        },
        {
            "Acronym": "SMWCon 2021",
            "Title": "SMWCon",
            "Year": "2021",
            "Description": "test value\\n with line break"
        }
    ]
}
```
