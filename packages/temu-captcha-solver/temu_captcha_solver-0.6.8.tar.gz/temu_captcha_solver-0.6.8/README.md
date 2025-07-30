# Overview
This project is not affiliated with [SadCaptcha](https://www.sadcaptcha.com/register), but it leverages their API to solve the various puzzles.
Instructions for integrating with Selenium, Playwright, and Async Playwright are described below in their respective sections.

Currently it solves the arced slide, puzzle slide, shapes, items, three-by-three, two image, and swap two challenges:

<div align="center">
    <img src="https://sadcaptcha.b-cdn.net/arced-slide-temu-captcha.png" width="175px" height="150px" alt="temu slide Captcha Solver">
    <img src="https://sadcaptcha.b-cdn.net/temu-puzzle.webp" width="175px" height="150px" alt="Temu puzzle Captcha Solver">
    <img src="https://sadcaptcha.b-cdn.net/temu-shapes.webp" width="175px" height="150px" alt="Temu shapes Captcha Solver">
    <img src="https://sadcaptcha.b-cdn.net/temu-items.png" width="175px" height="150px" alt="Temu items Captcha Solver">
    <img src="https://sadcaptcha.b-cdn.net/temu-three-by-three-captcha.webp" width="175px" height="150px" alt="Temu 3x3 Captcha Solver">
    <img src="https://sadcaptcha.b-cdn.net/14.png" width="175px" height="150px" alt="Temu swap two Captcha Solver">
    <img src="https://sadcaptcha.b-cdn.net/Untitled.png" width="175px" height="150px" alt="Temu cats and cars captcha solver">
    <img src="https://sadcaptcha.b-cdn.net/temu-two-image.webp" width="175px" height="150px" alt="Temu two image captcha solver">
</div>

- **Arced Slide** challenge is the one where there is a puzzle piece that travels in an unpredictable trajectory, and there are two possible locations where the solution may be.
- **Puzzle slide** is unique in that the pieces relocate after you drag the slider.
- **Shapes (English only)** challenge shows a picture of various objects and has an associated text challenge.
- **Items (English only)** challenge shows a picture of various objects and has an associated text challenge.
- **Three-by-three** challenge shows a 3x3 grid of images, and asks you to select images according to a text challenge.
- **Swap Two** has two tiles in the wrong order, and asks you to swap two to fix the image.
- **Cats and Cars (English only)** is an adorable challenge but it will wreck your bot.
- **Two image (English only)** is a notorious challenge which presents a text challenge and two side-by-side images.
    
## Requirements
- Python >= 3.10
- **If using Nodriver** - Google chrome installed on system. This is the recommended method.
- **If using Selenium** - Selenium properly installed and in `PATH`
- **If using Playwright** - Playwright must be properly installed with `playwright install`
- **Stealth plugin** - You must use the appropriate `stealth` plugin for whichever browser automation framework you are using.
    - For Selenium, you can use [undetected-chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver)
    - For Playwright, you can use [playwright-stealth](https://pypi.org/project/playwright-stealth/)

## Installation
This project can be installed with `pip`. Just run the following command:
```
pip install temu-captcha-solver
```

## Nodriver Client (Recommended)
Nodriver is the latest advancement in undetected automation technology, and is the recommended method.
Import the function `make_nodriver_solver`
This function will create an noddriver instance patched with the temu Captcha Solver chrome extension.
The extension will automatically detect and solve the captcha in the background, and there is nothing further you need to do.

```py
from temu_captcha_solver.launcher import make_nodriver_solver

async def main():
    launch_args = ["--headless=chrome"] # If running headless, use this option, or headless=new
    api_key = "YOUR_API_KEY_HERE"
    # NOTE: Keyword arguments passed to make_nodriver_solver() are directly passed to nodriver.start()!
    driver = await make_nodriver_solver(api_key, browser_args=launch_args) # Returns nodriver browser 
    # ... [The rest of your code goes here]
```
All keyword arguments passed to `make_nodriver_solver()` are passed directly to `nodriver.start()`.


## Selenium Client 
Import the function `make_undetected_chromedriver_solver`
This function will create an undetected chromedriver instance patched with the temu Captcha Solver chrome extension.
The extension will automatically detect and solve the captcha in the background, and there is nothing further you need to do.

```py
from temu_captcha_solver import make_undetected_chromedriver_solver
from selenium_stealth import stealth
import undetected_chromedriver as uc

api_key = "YOUR_API_KEY_HERE"
driver = make_undetected_chromedriver_solver(api_key) # Returns uc.Chrome instance
stealth(driver) # Add stealth if needed
# ... [The rest of your code goes here]

# Now temu captchas will be automatically solved!
```
You may also pass `ChromeOptions` to `make_undetected_chromedriver_solver()`, as well as keyword arguments for `uc.Chrome()`.

## Playwright Client
Import the function `make_playwright_solver_context`
This function will create a playwright BrowserContext instance patched with the temu Captcha Solver chrome extension.
The extension will automatically detect and solve the captcha in the background, and there is nothing further you need to do.

```py
from temu_captcha_solver import make_playwright_solver_context
from playwright.sync_api import sync_playwright

api_key = "YOUR_API_KEY_HERE"
with sync_playwright() as p:
    context = make_playwright_solver_context(p, api_key) # Returns playwright BrowserContext instance
    # ... [The rest of your code goes here]

```
You may also pass keyword args to this function, which will be passed directly to playwright's call to `playwright.chromium.launch_persistent_context()`.
By default, the user data directory is a tempory directory that is deleted at the end of runtime.

## Async Playwright Client
Import the function `make_async_playwright_solver_context`
This function will create an async playwright BrowserContext instance patched with the temu Captcha Solver chrome extension.
The extension will automatically detect and solve the captcha in the background, and there is nothing further you need to do.

```py
import asyncio
from playwright.async_api import async_playwright
from temu_captcha_solver import make_async_playwright_solver_context

async def main():
    api_key = "YOUR_API_KEY_HERE"
    async with async_playwright() as p:
        context = await make_async_playwright_solver_context(p, api_key) # Returns playwright BrowserContext instance
        # ... [The rest of your code goes here]

asyncio.run(main())
```
You may also pass keyword args to this function, which will be passed directly to playwright's call to `playwright.chromium.launch_persistent_context()`.
By default, the user data directory is a tempory directory that is deleted at the end of runtime.
