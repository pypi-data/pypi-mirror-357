# PeopleSoft Components Library

A Python library designed to simplify finding and interacting with PeopleSoft components using Selenium WebDriver. This library provides abstractions for commonly used UI elements in PeopleSoft applications, such as buttons, tiles, and input fields.

## Features

- **Modular Components**: Includes Button, Image, TextInput, PasswordInput, and Tile components, each designed to make interaction with PeopleSoft UI elements straightforward.
- **Robust Base Class**: Provides `BaseComponent` class for building custom components.
- **Selenium Integration**: Fully compatible with Selenium WebDriver.

---

## Installation

Install the package directly from the GitLab Package Registry:

```bash
pip install peoplesoft-selenium-components
```

---

## Usage

### General Usage

Import the components and use them to interact with PeopleSoft UI elements in your Selenium scripts:

```python
from selenium import webdriver
from peoplesoft_components import Button, TextInput, Tile


driver = webdriver.Chrome()
driver.get("https://your-peoplesoft-url.com")

# Interact with a button
button = Button.find(driver, "Submit")
button.click()

# Fill a text input field
text_input = TextInput.find(driver, "Username")
text_input.set_value("my_username")

# Interact with a tile
tile = Tile.find(driver, "Student Center")
tile.click()
```

---

### Components

This library provides several pre-defined components for interacting with PeopleSoft UI elements.  
Below are details for each component, including how to find and interact with them.  

#### Button

Represents a button element (`<input>` with the class `ps-button`).

- **Methods**:
  - `Button.find(driver, label)`: Finds a button by its label (the `value` attribute of the `<input>`).

Example:

```python
from peoplesoft_components import Button


button = Button.find(driver, "Submit") 
button.click()
```

---

#### TextInput

Represents a text input element (`<input>` with type `text`).

- **Methods**:
  - `TextInput.find(driver, label)`: Finds a text input field by its associated `<label>` text.

Example:

```python
from peoplesoft_components import TextInput


text_input = TextInput.find(driver, "Username")
text_input.set_value("my_username")
```

---

#### PasswordInput

Represents a password input element (`<input>` with type `password`).

- **Methods**:
  - `PasswordInput.find(driver, label)`: Finds a password input field by its associated `<label>` text.

Example:

```python
from peoplesoft_components import PasswordInput


password_input = PasswordInput.find(driver, "Password")
password_input.set_value("my_password")
```

---

#### Tile

Represents a tile element, typically found in dashboards or navigation areas.

- **Methods**:
  - `Tile.find(driver, label)`: Finds a tile by its visible label text.

Example:

```python
from peoplesoft_components import Tile


tile = Tile.find(driver, "Student Center")
tile.click()
```

---

#### Image

Represents an image element (`<img>`).

- **Methods**:
  - `Image.find(driver, alt_text)`: Finds an image by its `alt` attribute.

Example:

```python
from peoplesoft_components import Image


image = Image.find(driver, "Logo") 
assert image.is_displayed()
```

---

## Getting Started with Development

To set up the project for development:

### 1. Clone the Repository

```bash
git clone https://gitlab.com/campus-solutions-automated-testing-group/peoplesoft-selenium-components.git  
cd peoplesoft-selenium-components
````

### 2. Install Dependencies

Use a virtual environment and install the required dependencies:

```bash
python -m venv venv  
source venv/bin/activate  # On Windows: venv\Scripts\activate  
pip install -r requirements.txt
```

### 3. Build the Package

Build the package locally to test distribution:

```bash
python -m build
```

---

## Resources

- **Homepage**: [Project Homepage](https://gitlab.developers.cam.ac.uk/uis/qa/peoplesoft-selenium-components)
- **Selenium Documentation**: [Selenium](https://www.selenium.dev/documentation/)

---

## Contributing

Contributions are welcome! Please fork the repository, create a feature branch, and submit a merge request.

---

## License

This project is licensed under the terms specified in the `LICENSE` file.
