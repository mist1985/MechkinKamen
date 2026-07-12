# Google Play listing — Мечкин Камен

Everything below is ready to paste into Play Console. Assets are in this folder.

---

## Assets (all generated, all in `play/`)

| Play Console field | File | Required size |
|---|---|---|
| App icon | `play-icon-512.png` | 512×512 ✓ |
| Feature graphic | `play-feature-1024x500.png` | 1024×500 ✓ |
| Phone screenshots | `screenshots/*.png` | 2340×1080 ✓ (min 2, max 8) |
| App bundle | `../android/app/build/outputs/bundle/release/app-release.aab` | 2.9 MB ✓ |
| Privacy policy | https://mist1985.github.io/MechkinKamen/privacy.html | ✓ |

---

## App details

- **App name:** `Мечкин Камен — 1903`
- **Default language:** Macedonian (mk-MK)
- **App or game:** Game
- **Category:** Action  (Adventure is a reasonable alternative)
- **Tags:** Historical, First-person shooter, Offline
- **Free or paid:** Free
- **Contains ads:** **No** — ads are switched off and the SDK is not linked.
  If you enable ads later you MUST come back and change this.

---

## Short description (max 80 characters)

```
Одбрани го Мечкин Камен. Десет бранови. Слобода или смрт.
```

English (if you add an en-US listing):

```
Hold Mechkin Kamen against ten waves. Freedom or death.
```

---

## Full description (max 4000 characters)

```
12 август 1903. Десетти ден на Крушевската Република — првата република на
Балканот, родена во огнот на Илинденското востание.

Од Битола надоаѓа Бахтијар-паша со илјадници аскери и артилерија. На карпите
над градот, кај Мечкин Камен, застанува четата на војводата Питу Гули. Кога му
предлагаат повлекување, тој одговара: „Овде ќе се умре!"

Сега каменот е твој.

ОДБРАНА
• Десет бранови на аскери, секој потежок од претходниот
• Три оружја: Бердана, Малихерка и топче
• Бомби, камења од карпата и позиции зад заклон
• Држи ја позицијата — Питу Гули и четата ќе ти дојдат на помош

ИГРА
• Целосно офлајн — не бара интернет
• Не собира никакви податоци
• Табела со резултати на твојот телефон
• Управување на допир или со тастатура

Мечкин Камен не е измислена битка. Тука, на 12 август 1903, падна Питу Гули со
четата — и местото остана вечен спомен на слободата.

Слобода или смрт.
```

---

## Content rating questionnaire

Answer **honestly** — a false answer is grounds for removal, and the questionnaire
is easy to get right:

- Category: **Game**
- Violence: **Yes** — the player shoots at soldiers. It is stylised and blocky,
  with no gore, no blood effects on characters, and no dismemberment.
- Blood: **No**
- Sexual content / nudity: **No**
- Profanity: **No**
- Drugs / alcohol / tobacco: **No**
- Gambling / simulated gambling: **No**
- User-generated content, chat, sharing: **No**
- Personal information collected/shared: **No**

Expect roughly **PEGI 12 / ESRB Teen**. Depicting a real historical battle does
not change the rating — the mechanics do.

---

## Data safety form

This is the easy one, because it is all true:

- **Does your app collect or share any of the required user data types?** → **No**
- **Is all of the user data encrypted in transit?** → N/A (nothing is transmitted)
- **Do you provide a way for users to request that their data is deleted?** → N/A

The leaderboard and settings live in `localStorage` on the device. That counts as
local storage, not collection, so it is not declared.

If you turn ads on later, this form changes: you will have to declare the
**advertising ID**, and "Contains ads" becomes Yes.

---

## Target audience

- Target age: **13+** (matching the violence rating)
- Appeals to children: **No**

Choosing 13+ keeps you out of Play's Families policy, which carries extra
requirements you do not want for a game about a battle.
