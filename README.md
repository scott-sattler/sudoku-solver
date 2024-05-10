# sudoku-solver

~~older project. proof of concept. got bored (neither sufficiently novel nor difficult).~~

This so-called "Sudoku Solver" project is a very old project I revisited while initially trying to repurpose the UI.

I ultimately decided to not reuse the UI (partly due to concerns with Tkinter), rewrote/refactored virtually everything, and added many expected (i.e. typical) features along the way.

Although I do not actually play much Sudoku, I thoroughly enjoy building things!

I have not yet employed DLX (Algorithm X; or dancing links), so the performance suffers accordingly. :(

Random 17 clue board selection was implemented using Fisher-Yates. Given apparent text file limitations, time complexity is O(n), not O(1).

The application currently contains most of the functionality you would find in a typical Sudoku application, despite the title remaining unchanged.

<div align="center">
    <img width="25%" src="https://github.com/scott-sattler/sudoku-solver/blob/58a964767b7cfa62e57f8bbf8a735fd21e658af4/screenshots/readme_image_1.png">
    <img width="25%" src="https://github.com/scott-sattler/sudoku-solver/blob/bad2818cfa2013f85590909518c9cade73421963/screenshots/readme_image_2.png">
    <img width="25%" src="https://github.com/scott-sattler/sudoku-solver/blob/58a964767b7cfa62e57f8bbf8a735fd21e658af4/screenshots/readme_image_3.png">
</div>