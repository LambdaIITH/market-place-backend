## Market Place Backend

This repository contains the code for the backend of a college market place application.

### Tech Stack

<ul>
<li>
<a href="https://fastapi.tiangolo.com/?h=installation#installation">FastAPI - A Backend Python Framework</a>
</li>
<li>
<a href="https://python-poetry.org/docs/basic-usage/">Poetry - A Dependency Management tool in Python</a>
</li>
<li>
<a href="https://www.postgresql.org">PostgreSQL - Database</a>
</li>
</ul>

### File Structure

- `pyproject.toml` - Contains the dependecies.
- `main.py` - Contains the backend API routes.
- `db/init.sql` - Schema for the database.
- `.env.example` - Format for the .env file to connect to PostgreSQL.

### Steps

- Install the above tools. </br>
- Install the dependencies from the `pyproject.toml` file. </br>
- Refer to the sql file in `db/init.sql` to get the models used in the database.
- Add a `.env` file, following `.env.example` accordingly.

### Bonus

- Bonus points for making use of other open source tools to make the code cleaner and readable. For example [aiosql](https://nackjicholson.github.io/aiosql/), [pydantic](https://docs.pydantic.dev)
