<?php
// index.php
?>
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Radar</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 860px; margin: 24px auto; padding: 0 12px; }
    label { font-weight: 600; }
    .row { margin: 14px 0; }
    input[type="text"], select { width: 100%; padding: 8px; }
    .hint { font-size: 12px; color: #666; margin-top: 6px; }
  </style>
</head>
<body>
  <h1>Radar</h1>

  <form action="run.php" method="post" enctype="multipart/form-data">
    <div class="row">
      <label>Client domain</label><br/>
      <input name="client_domain" type="text" required placeholder="103telemed.pl" />
    </div>

    <div class="row">
      <label>Market</label><br/>
      <select name="market">
        <option value="Global" selected>Global</option>
        <option value="PL">PL</option>
        <option value="EU">EU</option>
        <option value="US">US</option>
      </select>
    </div>

    <div class="row">
      <label>Language</label><br/>
      <select name="language">
        <option value="en" selected>en</option>
        <option value="ru">ru</option>
        <option value="pl">pl</option>
      </select>
    </div>

    <div class="row">
      <label>Mode</label><br/>
      <select name="mode">
        <option value="sales" selected>sales</option>
        <option value="onboarding">onboarding</option>
      </select>
    </div>

    <div class="row">
      <label>Competitor (optional)</label><br/>
      <input name="competitor_1" type="text" placeholder="telemedpolska.pl" />
      <div class="hint">
        Можно оставить пустым. Тогда Radar попробует вытащить конкурентов из Semrush-скринов.
      </div>
    </div>

    <div class="row">
      <label>Semrush auto screenshots</label><br/>
      <input type="checkbox" name="semrush_auto" value="1" />
      <div class="hint">
        Откроется окно браузера. Первый раз нужен ручной логин. Потом будет помнить вход.
      </div>
    </div>

    <div class="row">
      <label>Semrush database</label><br/>
      <select name="semrush_db">
        <option value="pl" selected>pl</option>
        <option value="us">us</option>
        <option value="ru">ru</option>
      </select>
    </div>

    <div class="row">
      <label>Semrush screenshots (many files)</label><br/>
      <input name="semrush_files[]" type="file" multiple accept="image/png,image/jpeg" />
      <div class="hint">
        Если не используешь авто-скриншоты, можно вручную выбрать много картинок.
      </div>
    </div>

    <div class="row">
      <label>Semrush PDF (optional)</label><br/>
      <input name="semrush_pdf" type="file" accept="application/pdf" />
      <div class="hint">
        Один PDF вместо пачки картинок, если есть лимит PDF — не используй.
      </div>
    </div>

    <div class="row">
      <label>Blocked screen (optional)</label><br/>
      <input name="blocked_screen" type="file" accept="image/png,image/jpeg" />
    </div>

    <input type="hidden" name="slide_limit" value="5" />

    <div class="row">
      <button type="submit">Run</button>
    </div>
  </form>
</body>
</html>
