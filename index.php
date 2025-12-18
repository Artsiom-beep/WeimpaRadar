<?php
// index.php
?>
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Radar</title>
</head>
<body>
  <h1>Radar run</h1>

  <form action="run.php" method="post" enctype="multipart/form-data">
    <div>
      <label>Client domain</label><br/>
      <input name="client_domain" type="text" required placeholder="weimpa.com" />
    </div>

    <div>
      <label>Market</label><br/>
      <select name="market">
        <option value="Global" selected>Global</option>
        <option value="PL">PL</option>
        <option value="EU">EU</option>
        <option value="US">US</option>
      </select>
    </div>

    <div>
      <label>Language</label><br/>
      <select name="language">
        <option value="en" selected>en</option>
        <option value="ru">ru</option>
        <option value="pl">pl</option>
      </select>
    </div>

    <div>
      <label>Mode</label><br/>
      <select name="mode">
        <option value="sales" selected>sales</option>
        <option value="onboarding">onboarding</option>
      </select>
    </div>

    <div>
      <label>Competitor</label><br/>
      <input name="competitor_1" type="text" placeholder="brightcall.ai" />
    </div>

    <div>
      <label>Semrush Domain Overview (png)</label><br/>
      <input name="semrush_overview" type="file" accept="image/png,image/jpeg" />
    </div>

    <div>
      <label>Blocked screen (png)</label><br/>
      <input name="blocked_screen" type="file" accept="image/png,image/jpeg" />
    </div>

    <input type="hidden" name="slide_limit" value="5" />

    <div style="margin-top:12px;">
      <button type="submit">Run</button>
    </div>
  </form>
</body>
</html>
