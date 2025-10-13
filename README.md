# pmv-rag1

👉\[\[\[**This is the initial readme for your
[simple-modern-uv](https://github.com/jlevy/simple-modern-uv) template.** Fill it in and
delete this message!
Below are general setup instructions that you may remove or keep and adapt for your
project.\]\]\]

* * *

## Project Docs

For how to install uv and Python, see [installation.md](installation.md).

For development workflows, see [development.md](development.md).

For instructions on publishing to PyPI, see [publishing.md](publishing.md).

* * *

## Running the Application

To run the application, follow these steps:

1.  **Configure Environment Variables:**

    Copy the `env.example` file to a new file named `.env` and fill in the required environment variables:

    ```bash
    cp env.example .env
    ```

2.  **Install Dependencies:**

    Install the project dependencies using the provided `Makefile` command:

    ```bash
    make install
    ```

3.  **Run the Server:**

    Start the FastAPI server using `uvicorn`. The `--reload` flag enables hot-reloading for development:

    ```bash
    uvicorn src.pmv_rag1.main:app --reload
    ```

*This project was built from
[simple-modern-uv](https://github.com/jlevy/simple-modern-uv).*
