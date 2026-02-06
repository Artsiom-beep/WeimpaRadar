<?php
header('Content-Type: text/html; charset=utf-8');
header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
header('Pragma: no-cache');

function load_prompt(array $cands): string {
  foreach ($cands as $rel) {
    $path = __DIR__ . '/' . $rel;
    if (is_readable($path)) {
      $s = file_get_contents($path);
      if ($s !== false) return $s;
    }
  }
  return '';
}

$P_SALES = load_prompt([
  'prompts/default/sales_note.txt',
  'sales_note.txt',
  'py/radar_py/prompts/default/sales_note.txt',
]);

$P_REPORT = load_prompt([
  'prompts/default/report_md.txt',
  'prompts/default/report.md',
  'report.md',
  'py/radar_py/prompts/default/report_md.txt',
]);

$P_COMP_NOTE = load_prompt([
  'prompts/default/competitor_note.txt',
  'competitor_note.txt',
  'py/radar_py/prompts/default/competitor_note.txt',
]);

$P_COMPARE = load_prompt([
  'prompts/default/compare.txt',
  'compare.txt',
  'py/radar_py/prompts/default/compare.txt',
]);

$P_QUICK = load_prompt([
  'prompts/default/quick_wins.txt',
  'quick_wins.txt',
  'py/radar_py/prompts/default/quick_wins.txt',
]);
?>
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Radar</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 860px; margin: 24px auto; padding: 0 12px; }
    label { font-weight: 600; }
    .row { margin: 14px 0; }
    input[type="text"], select, textarea { width: 100%; padding: 8px; box-sizing: border-box; }
    textarea { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace; font-size: 12px; }
    .hint { font-size: 12px; color: #666; margin-top: 6px; line-height: 1.3; }
    .btn { padding: 6px 10px; }
    .comp-row { display:flex; gap:8px; margin-top:8px; }
    .comp-row input { flex:1; }
    .comp-row button { width:44px; }
    hr { margin: 18px 0; }
    details > summary { cursor: pointer; font-weight: 700; }
    .inline { display:flex; gap:8px; align-items:center; }
    .inline > * { flex: 1; }
    .inline button { flex: 0 0 auto; }
  </style>
</head>
<body>
  <h1>Radar</h1>

  <form action="run.php" method="post" enctype="multipart/form-data">
    <input type="hidden" name="mode" value="sales" />

    <div class="row">
      <label>Client domain</label><br/>
      <input name="client_domain" type="text" required placeholder="103telemed.pl" />
    </div>

    <div class="row">
      <label>Market</label><br/>
      <select name="market" id="market">
        <option value="PL" selected>PL</option>
        <option value="Global">Global</option>
        <option value="EU">EU</option>
        <option value="US">US</option>
      </select>
    </div>

    <div class="row">
      <label>Semrush database</label><br/>
      <div class="inline">
        <select name="semrush_database" id="semrush_database">
          <option value="">(auto = market)</option>
        </select>
        <button type="button" id="semrush_db_detect" class="btn">Определить</button>
      </div>
      <div class="hint">Если пусто — берём Market автоматически. Global → us.</div>
    </div>

    <div class="row">
      <label>Language</label><br/>
      <select name="language" id="language">
        <option value="pl" selected>pl</option>
        <option value="en">en</option>
        <option value="ru">ru</option>
        <option value="de">de</option>
        <option value="fr">fr</option>
        <option value="es">es</option>
        <option value="it">it</option>
        <option value="nl">nl</option>
        <option value="pt">pt</option>
        <option value="tr">tr</option>
        <option value="uk">uk</option>
        <option value="cs">cs</option>
        <option value="sk">sk</option>
        <option value="hu">hu</option>
        <option value="ro">ro</option>
        <option value="el">el</option>
        <option value="sv">sv</option>
        <option value="no">no</option>
        <option value="da">da</option>
        <option value="fi">fi</option>
        <option value="ar">ar</option>
        <option value="he">he</option>
        <option value="hi">hi</option>
        <option value="id">id</option>
        <option value="th">th</option>
        <option value="vi">vi</option>
        <option value="ja">ja</option>
        <option value="ko">ko</option>
        <option value="zh">zh</option>
        <option value="zh-TW">zh-TW</option>
      </select>
      <div class="hint">Отчёт/нота генерируются моделью, язык может быть любой.</div>
    </div>

    <div class="row">
      <label>Competitors (optional)</label><br/>
      <div id="competitors_box"></div>
      <button type="button" id="add_competitor" class="btn" style="margin-top:8px;">+</button>
      <div class="hint">До 5 конкурентов. 1 строка = 1 домен. “-” удаляет строку.</div>
    </div>

    <div class="row">
      <label>Semrush auto screenshots</label><br/>
      <label style="font-weight:400;">
        <input type="checkbox" name="semrush_auto" value="1" />
        Включить
      </label>
      <div class="hint">Если Semrush не залогинен — сделай логин в профиль runs/_semrush_profile через ops/semrush_login_web.sh.</div>
    </div>

    <div class="row">
      <label>Semrush screenshots (many files)</label><br/>
      <input name="semrush_files[]" type="file" multiple accept="image/png,image/jpeg" />
      <div class="hint">Если не используешь авто-скрины — загрузи пачку картинок Semrush.</div>
    </div>

    <div class="row">
      <label>Competitor screenshots (optional)</label><br/>
      <input name="competitor_files[]" type="file" multiple accept="image/png,image/jpeg" />
      <div class="hint">Если сайт конкурента не открывается автоматически — загрузи 1–3 скрина главной/оффера.</div>
    </div>

    <div class="row">
      <label>Blocked screen (optional)</label><br/>
      <input name="blocked_screen" type="file" accept="image/png,image/jpeg" />
      <div class="hint">Если сайт режет ботов (капча/403/пустая страница), blocked screen помогает объяснить, что мешает сбору и что делать дальше.</div>
    </div>

    <button type="submit" class="btn">Run</button>

    <hr/>

    <details>
      <summary>Prompts (debug)</summary>

      <div class="row">
        <label>sales_note</label>
        <button type="button" class="btn" onclick="resetPrompt('sales_note_prompt')">Reset to default</button>
        <textarea name="sales_note_prompt" id="sales_note_prompt" rows="14"><?php echo htmlspecialchars($P_SALES); ?></textarea>
      </div>

      <div class="row">
        <label>report_md</label>
        <button type="button" class="btn" onclick="resetPrompt('report_md_prompt')">Reset to default</button>
        <textarea name="report_md_prompt" id="report_md_prompt" rows="14"><?php echo htmlspecialchars($P_REPORT); ?></textarea>
      </div>

      <div class="row">
        <label>competitor_note</label>
        <button type="button" class="btn" onclick="resetPrompt('competitor_note_prompt')">Reset to default</button>
        <textarea name="competitor_note_prompt" id="competitor_note_prompt" rows="14"><?php echo htmlspecialchars($P_COMP_NOTE); ?></textarea>
      </div>

      <div class="row">
        <label>compare</label>
        <button type="button" class="btn" onclick="resetPrompt('compare_prompt')">Reset to default</button>
        <textarea name="compare_prompt" id="compare_prompt" rows="14"><?php echo htmlspecialchars($P_COMPARE); ?></textarea>
      </div>

      <div class="row">
        <label>quick_wins</label>
        <button type="button" class="btn" onclick="resetPrompt('quick_wins_prompt')">Reset to default</button>
        <textarea name="quick_wins_prompt" id="quick_wins_prompt" rows="14"><?php echo htmlspecialchars($P_QUICK); ?></textarea>
      </div>

      <button type="button" class="btn" onclick="resetAllPrompts()">Reset all to default</button>
    </details>

  </form>

  <script>
  window.__PROMPT_DEFAULTS = {
    sales_note_prompt: <?php echo json_encode($P_SALES, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES); ?>,
    report_md_prompt: <?php echo json_encode($P_REPORT, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES); ?>,
    competitor_note_prompt: <?php echo json_encode($P_COMP_NOTE, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES); ?>,
    compare_prompt: <?php echo json_encode($P_COMPARE, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES); ?>,
    quick_wins_prompt: <?php echo json_encode($P_QUICK, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES); ?>,
  };

  function resetPrompt(id){
    var el = document.getElementById(id);
    if (!el) return;
    el.value = (window.__PROMPT_DEFAULTS[id] || '');
  }
  function resetAllPrompts(){
    resetPrompt('sales_note_prompt');
    resetPrompt('report_md_prompt');
    resetPrompt('competitor_note_prompt');
    resetPrompt('compare_prompt');
    resetPrompt('quick_wins_prompt');
  }

  (function(){
    // competitors +/-
    var box = document.getElementById('competitors_box');
    var btn = document.getElementById('add_competitor');

    function countInputs(){ return box.querySelectorAll('input[name="competitors[]"]').length; }
    function addRow(v){
      if (countInputs() >= 5) return;
      var wrap = document.createElement('div');
      wrap.className = 'comp-row';

      var inp = document.createElement('input');
      inp.type = 'text';
      inp.name = 'competitors[]';
      inp.placeholder = 'telemedpolska.pl';
      inp.value = v || '';

      var rm = document.createElement('button');
      rm.type = 'button';
      rm.textContent = '-';
      rm.className = 'btn';
      rm.addEventListener('click', function(){ wrap.remove(); });

      wrap.appendChild(inp);
      wrap.appendChild(rm);
      box.appendChild(wrap);
    }

    if (box && btn){
      addRow('');
      btn.addEventListener('click', function(){ addRow(''); });
    }

    // semrush db detect + sync to market
    var market = document.getElementById('market');
    var dbSel = document.getElementById('semrush_database');
    var dbBtn = document.getElementById('semrush_db_detect');

    function marketToDb(mv){
      mv = (mv || '').trim().toLowerCase();
      if (!mv) return '';
      if (mv === 'global') return 'us';
      return mv.toLowerCase();
    }

    function syncDbToMarket(){
      if (!market || !dbSel) return;
      var mv = marketToDb(market.value);
      var dv = (dbSel.value || '').trim().toLowerCase();
      if (dv === '' || dv === mv) dbSel.value = mv;
    }

    function fillDb(list){
      var cur = (dbSel.value || '').trim().toLowerCase();
      dbSel.innerHTML = '<option value="">(auto = market)</option>';
      for (var i=0; i<list.length; i++){
        var v = String(list[i] || '').trim().toLowerCase();
        if (!v) continue;
        var opt = document.createElement('option');
        opt.value = v;
        opt.textContent = v;
        dbSel.appendChild(opt);
      }
      if (cur) dbSel.value = cur;
      syncDbToMarket();
    }

    function loadDbs(){
      fetch('semrush_dbs.php', {cache:'no-store'})
        .then(function(r){ return r.json(); })
        .then(function(j){
          if (j && j.ok && Array.isArray(j.dbs)) fillDb(j.dbs);
          else syncDbToMarket();
        })
        .catch(function(){ syncDbToMarket(); });
    }

    if (dbBtn) dbBtn.addEventListener('click', loadDbs);
    if (market) market.addEventListener('change', function(){ syncDbToMarket(); });

    // автозагрузка баз
    loadDbs();
    syncDbToMarket();
  })();
  </script>
</body>
</html>
