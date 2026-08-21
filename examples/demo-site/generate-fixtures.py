#!/usr/bin/env python3
"""
Creates the fixtures the demo site needs but that must NOT live in git:

  hero.jpg        a 1.2 MB "image", to exercise the oversized-image check
  leaked-key.html a page with a fake Stripe-style key, to exercise the
                  hardcoded-credential check

The key is assembled from fragments at runtime. Committing a literal that
matches a real credential pattern gets your push blocked by GitHub secret
scanning - which is exactly the failure this scanner exists to catch, so we
practise what we preach.

Run automatically by the test suite; run by hand to scan the demo yourself.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

HERO = os.path.join(HERE, "hero.jpg")
if not os.path.exists(HERO):
    with open(HERO, "wb") as f:
        f.write(b"\xff\xd8\xff\xe0" + b"\x00" * 1_200_000)
    print(f"created {HERO}")

FAKE_KEY = "sk" + "_" + "live" + "_" + "51H8xQ2eZvKYlo2C0abcdefgh"   # not a real key
LEAK = os.path.join(HERE, "leaked-key.html")
with open(LEAK, "w") as f:
    f.write(f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Checkout · Demo Site for the web-qa scanner</title>
  <meta name="description" content="A fixture page carrying a fake credential so the scanner's hardcoded-secret check can be exercised by the test suite.">
</head>
<body>
  <main>
    <h1>Checkout</h1>
    <script>const STRIPE_KEY = "{FAKE_KEY}";</script>
  </main>
</body>
</html>
""")
print(f"created {LEAK}")
