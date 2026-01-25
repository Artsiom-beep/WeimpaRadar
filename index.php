<?php
// index.php
?>

<?php
function read_prompt_file($rel) {
  $p = __DIR__ . '/py/radar_py/prompts/default/' . $rel;
  if (!is_readable($p)) return '';
  return file_get_contents($p);
}
$P_SALES = read_prompt_file('sales_note.txt');
$P_REPORT = read_prompt_file('report.md');
$P_COMP = read_prompt_file('competitor_note.txt');
$P_COMPARE = read_prompt_file('compare.txt');
$P_QW = read_prompt_file('quick_wins.txt');
$PROMPT_DEFAULTS = [
  'sales_note' => $P_SALES,
  'report_md' => $P_REPORT,
  'competitor_note' => $P_COMP,
  'compare' => $P_COMPARE,
  'quick_wins' => $P_QW,
];
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
      <label>Competitor screenshots (optional)</label><br/>
      <input name="competitor_files[]" type="file" multiple accept="image/png,image/jpeg" />
      <div class="hint">
        Если сайт конкурента не открывается автоматически — загрузи 1–3 скрина главной/оффера.
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
  

  <!-- PROMPTS BLOCK -->
  <hr style="margin:24px 0;"/>

  <details>
    <summary style="font-weight:700; cursor:pointer;">Prompts (debug)</summary>
    <div class="row">
      <label>sales_note</label> <button type="button" data-reset-key="sales_note" style="margin-left:10px;">Reset to default</button><br/>
      <textarea name="prompt_sales_note" rows="10" style="width:100%; padding:8px; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;"><?php echo htmlspecialchars($P_SALES); ?></textarea>
      <div class="hint">Reset: reload the page</div>
    </div>

    <div class="row">
      <label>report_md</label> <button type="button" data-reset-key="report_md" style="margin-left:10px;">Reset to default</button><br/>
      <textarea name="prompt_report_md" rows="10" style="width:100%; padding:8px; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;"><?php echo htmlspecialchars($P_REPORT); ?></textarea>
    </div>

    <div class="row">
      <label>competitor_note</label> <button type="button" data-reset-key="competitor_note" style="margin-left:10px;">Reset to default</button><br/>
      <textarea name="prompt_competitor_note" rows="10" style="width:100%; padding:8px; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;"><?php echo htmlspecialchars($P_COMP); ?></textarea>
    </div>

    <div class="row">
      <label>compare</label> <button type="button" data-reset-key="compare" style="margin-left:10px;">Reset to default</button><br/>
      <textarea name="prompt_compare" rows="8" style="width:100%; padding:8px; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;"><?php echo htmlspecialchars($P_COMPARE); ?></textarea>
    </div>

    <div class="row">
      <label>quick_wins</label> <button type="button" data-reset-key="quick_wins" style="margin-left:10px;">Reset to default</button><br/>
      <textarea name="prompt_quick_wins" rows="8" style="width:100%; padding:8px; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;"><?php echo htmlspecialchars($P_QW); ?></textarea>
    </div>
  
    <div class="row">
      <button type="button" id="reset_all_prompts">Reset all to default</button>
    </div>

    <script type="application/json" id="prompt_defaults_json"><?php echo json_encode($PROMPT_DEFAULTS, JSON_UNESCAPED_UNICODE | JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT); ?></script>
    <script>
    (function(){
      var el = document.getElementById('prompt_defaults_json');
      if (!el) return;
      var defaults = {};
      try { defaults = JSON.parse(el.textContent || '{}'); } catch(e) { defaults = {}; }

      function setVal(key){
        var ta = document.querySelector('textarea[name="prompt_' + key + '"]');
        if (ta && typeof defaults[key] === 'string') ta.value = defaults[key];
      }

      document.querySelectorAll('button[data-reset-key]').forEach(function(btn){
        btn.addEventListener('click', function(){
          setVal(btn.getAttribute('data-reset-key'));
        });
      });

      var all = document.getElementById('reset_all_prompts');
      if (all) all.addEventListener('click', function(){
        Object.keys(defaults).forEach(setVal);
      });
    })();
    </script>

</details>

</form>
</body>
</html>
