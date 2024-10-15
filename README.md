# ChoreBoss

<div style="text-align: center;">
  <img src="web/static/images/chore-boss_v1.svg" alt="ChoreBoss Logo" height="512" style="width:auto;">
</div>
ChoreBoss is a Flask Web App designed to help you track and manage chores between household members.

## Table of Contents

- [Installation](#installation)
- [Usage Details](#details)
- [License](#license)

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/toann1980/choreboss.git
   cd choreboss
   ```

2. Create and activate a virtual environment:

   ```sh
   python -m venv .venv
   source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
   ```

3. Install the dependencies:

   ```sh
   On Linux:
   pip install -r requirements_linux.txt

   On Windows:
   pip install -r requirements_windows.txt
   ```

4. Run the application:

   ```sh
   For debugging:
   flask --app run.py run

   For Linux:
   gunicorn --bind 0.0.0.0:8055 run:app

   For Windows:
   waitress-serve --host=0.0.0.0 --port=8055 run:app
   ```

5. Open your browser and navigate to `http://127.0.0.1:8055`.

## Usage Details

- **Add and Edit Chores**: Easily add and edit new chores with a name and description of the chore.
- **Add and Edit People**: Add and edit people responsible for chores. Chores are PIN protected.
- **Change the Sequence Order**: Chores are assigned by an editable sequence. Once a person completes a chore, the next person is automatically assigned.
- **Mark as complete**: The admin or the next person in line has to approve the chore is complete.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
