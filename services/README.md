# Instruction Engine

`instruction_engine.py` is the governing business rule layer for the application.

The application may provide editable examples, calculations, simulations and advisory views, but those features must not silently change the requirements defined by the Instruction File.

The intended flow is:

Instruction File → Instruction Engine → Case 01 → Case 02 → Case 03 → Consistency Check → Report

The engine is deliberately separate from the user interface so future revisions of the Instruction File can be reflected in one place rather than scattered through `app.py` and the case modules.
