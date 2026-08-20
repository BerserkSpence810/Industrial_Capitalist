"""Self-contained play-test harness the integration tests run on.

`harness` boots the real game loop headless with pygame's input redirected to a
scripted player; `gameplay` holds the player actions (boot, build, wire power,
inspect). Kept inside tests/ so the suite runs from a clean checkout.
"""
