# passrank

This is a Python library that evaluates the strength of passwords using a custom point-based system. It scores the password based on length, character variety, and transitions between characters.

##  Commands

### `evaluate(<password>)`
- Returns the numeric score of the given password.

### `rate(<score>)`
- Returns the human-readable rating (e.g., Weak, Moderate, Strong).

## Disclaimer

> This tool has a high accuracy rate, but not 100%.  
> Use it at your own risk.  
> The author is **not responsible** if your password gets found in a data breach and you get **cooked** i.e incur **any** loss.

---

##  Example

```python
import passrank

score = passrank.evaluate("IlvuM10@")
print(score)  # e.g. 1250

print(passrank.rate(score))  #  Strong
