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

---

Wow sometimes I just like complexity too much I am running this on a M series mac,
so only need Docker for my Database. Otherwise I can't use my local instance
of Ollama running and utilize the GPU. Gosh lol sometimes I make my life so hard.

I will say if you did this in Windows or Linux then life would be simple, but
this is more powerful than my Linux desktop, so :(.

Rant over, so basically yeah just use poetry and run.

```sh
poetry run python job_tracker/main.py
```

Also my ooga booga brain just learned about SQL tools. Very nice SQL extension
in VSCode, just need to install the Postgres drivers to get started, but 
overall very solid for interacting with databases.
</details>

<details>
<summary>1/16/2025 - Progres, Poetry, and Docker Resolve Continued</summary>
Lol, lol, lol I finally got some sucess like I found out the best version of
pyscopg to use to interface with Postgres is just `psycopg` instead of 
`psycopg2` because the first is the modern version.

I finally got a working version of Job Tracker. It strikes me as a janky, but 
hey its working pretty well. I will need to add some examples. Also I sorta
prefer working with OpenAi model or something else too. We will see. 

I need to add the ability to read the user's resume and store that context so 
that the LLM can then compare the user's skills and experiecne to the requested.
There are a few applications with this mainly the one being that of modifying
the user's resume for the job.

Also decided to exclude the job description "required experience" since it 
is often the case many apps ask way more than necessary in most cases. So to
not deter applicants let's just ignore it for now. 

</details>
