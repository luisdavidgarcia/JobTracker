# JobTracker
Tired of logging your jobs into a spreadsheet. Why not a database? Overkill? Yes, but it's fun :)

## Notes

<details>
<summary>1/15/2025 - Docker & Poetry Lessons Learned</summary>

Wow it was freaking dumb of me to thinking of putting poetry in a docker 
container, when a docker container is virtually meant for isolation.

Okay so after 3 hours then of perfecting my dockerfile I decied to do:

```sh
poetry export --without-hashes --format=requirements.txt > requirements.txt
```

So much simpler now I can just pip install the requirements.txt, but what no one tells you is that export must be installed. Poetry has plugins! To install just do:

```sh
poetry self add poetry-plugin-export
```

Overall if you ever think of adding a venv, poetry, or some other virtual enviroment in your docker container just don't it is pointless in most cases.

</details>