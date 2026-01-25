<?php

function load_env_file($path) {
  if (!is_readable($path)) return;
  $lines = file($path, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
  foreach ($lines as $line) {
    $line = trim($line);
    if ($line === '' || $line[0] === '#') continue;
    if (strpos($line, '=') === false) continue;
    [$k, $v] = explode('=', $line, 2);
    $k = trim($k);
    $v = trim($v);
    $v = trim($v, "\"'");
    putenv("$k=$v");
    $_ENV[$k] = $v;
    $_SERVER[$k] = $v;
  }
}
load_env_file(__DIR__ . '/.env');


// run.php

set_time_limit(0);
ini_set('max_execution_time', '0');

function slug($s) {
  $s = trim(strtolower($s));
  $s = preg_replace('/^https?:\/\//', '', $s);
  $s = rtrim($s, '/');
  $s = preg_replace('/[^a-z0-9\.\-_]+/', '-', $s);
  return $s ?: 'site';
}

function ensure_dir($path) {
  if (!is_dir($path)) mkdir($path, 0777, true);
}

function save_upload($fileKey, $dstPath) {
  if (!isset($_FILES[$fileKey])) return false;
  if ($_FILES[$fileKey]['error'] !== UPLOAD_ERR_OK) return false;
  return move_uploaded_file($_FILES[$fileKey]['tmp_name'], $dstPath);
}

function save_uploads_array($fileKey, $dstDir, $prefix) {
  if (!isset($_FILES[$fileKey])) return;
  $f = $_FILES[$fileKey];
  if (!is_array($f['name'])) return;

  $count = count($f['name']);
  for ($i = 0; $i < $count; $i++) {
    if (($f['error'][$i] ?? UPLOAD_ERR_NO_FILE) !== UPLOAD_ERR_OK) continue;

    $name = $f['name'][$i] ?? '';
    $ext = strtolower(pathinfo($name, PATHINFO_EXTENSION));
    if ($ext === 'jpeg') $ext = 'jpg';
    if (!in_array($ext, ['png', 'jpg'], true)) $ext = 'png';

    $dst = $dstDir . DIRECTORY_SEPARATOR . sprintf('%s_%02d.%s', $prefix, $i + 1, $ext);
    move_uploaded_file($f['tmp_name'][$i], $dst);
  }
}

function list_images_recursive_1_level($dirAbs, $dirRel) {
  if (!is_dir($dirAbs)) return [];

  $out = [];
  $items = scandir($dirAbs);
  foreach ($items as $it) {
    if ($it === '.' || $it === '..') continue;

    $abs = $dirAbs . DIRECTORY_SEPARATOR . $it;
    $rel = $dirRel . '/' . $it;

    if (is_dir($abs)) {
      $sub = scandir($abs);
      foreach ($sub as $f) {
        if ($f === '.' || $f === '..') continue;
        if (!preg_match('/\.(png|jpg|jpeg|webp)$/i', $f)) continue;
        $out[] = [$rel . '/' . $f, $it . '/' . $f];
      }
      continue;
    }

    if (!preg_match('/\.(png|jpg|jpeg|webp)$/i', $it)) continue;
    $out[] = [$rel, $it];
  }

  return $out;
}

$client_domain = trim($_POST['client_domain'] ?? '');
$market = trim($_POST['market'] ?? 'Global');
$language = trim($_POST['language'] ?? 'en');
$mode = trim($_POST['mode'] ?? 'sales');
$competitor_1 = trim($_POST['competitor_1'] ?? '');
$slide_limit = intval($_POST['slide_limit'] ?? 0);

$semrush_auto = isset($_POST['semrush_auto']) && in_array(strtolower((string)$_POST['semrush_auto']), ['1','on','true','yes'], true);
$semrush_db = trim($_POST['semrush_db'] ?? 'pl');

if ($client_domain === '') {
  http_response_code(400);
  echo "client_domain is required";
  exit;
}

$run_id = date('Y-m-d') . '__' . slug($client_domain) . '__' . $mode . '__' . $language . '__' . date('His');

$base = __DIR__;
$runs_dir = $base . DIRECTORY_SEPARATOR . 'runs';
$run_dir  = $runs_dir . DIRECTORY_SEPARATOR . $run_id;
$uploads_dir = $run_dir . DIRECTORY_SEPARATOR . 'uploads';

ensure_dir($uploads_dir);

// manual semrush images
save_uploads_array('semrush_files', $uploads_dir, 'semrush');

// optional semrush pdf
save_upload('semrush_pdf', $uploads_dir . DIRECTORY_SEPARATOR . 'semrush.pdf');

// optional blocked
save_upload('blocked_screen', $uploads_dir . DIRECTORY_SEPARATOR . 'blocked_screen.png');

$competitors = [];
if ($competitor_1 !== '') $competitors[] = $competitor_1;

// manual competitor screenshots (optional)
if ($competitor_1 !== '') {
  save_uploads_array('competitor_files', $uploads_dir, 'competitor__' . slug($competitor_1));
}

$payload = [
  'cmd' => 'run',
  'client_domain' => $client_domain,
  'market' => $market,
  'language' => $language,
  'mode' => $mode,
  'competitors' => $competitors,
  'run_id' => $run_id,
  'semrush_auto' => $semrush_auto,
  'semrush_db' => $semrush_db,
];

$prompts_override_raw = trim($_POST['prompts_override'] ?? '');
if ($prompts_override_raw !== '') {
  $po = json_decode($prompts_override_raw, true);
  if (is_array($po)) {
    $allowed = ['sales_note','report_md','competitor_note','compare','quick_wins'];
    $filtered = [];
    foreach ($allowed as $k) {
      if (isset($po[$k]) && is_string($po[$k]) && trim($po[$k]) !== '') {
        $filtered[$k] = $po[$k];
      }
    }
    if (!empty($filtered)) $payload['prompts_override'] = $filtered;
  }
}


if ($slide_limit > 0) $payload['slide_limit'] = $slide_limit;


// UI prompt overrides (per-run). Only apply if different from defaults.
function _read_default_prompt($rel) {
  $pp = __DIR__ . '/py/radar_py/prompts/default/' . $rel;
  if (!is_readable($pp)) return '';
  return file_get_contents($pp);
}
function _norm_nl($t) {
  return str_replace("\r\n", "\n", (string)$t);
}

$ui_map = [
  'sales_note'      => ['prompt_sales_note',      'sales_note.txt'],
  'report_md'       => ['prompt_report_md',       'report.md'],
  'competitor_note' => ['prompt_competitor_note', 'competitor_note.txt'],
  'compare'         => ['prompt_compare',         'compare.txt'],
  'quick_wins'      => ['prompt_quick_wins',      'quick_wins.txt'],
];

$ui_overrides = [];
foreach ($ui_map as $key => $pair) {
  $field = $pair[0];
  $defFile = $pair[1];
  if (!isset($_POST[$field])) continue;
  $txt = (string)$_POST[$field];
  if (trim($txt) === '') continue;

  $def = _read_default_prompt($defFile);
  $txtN = _norm_nl($txt);
  $defN = _norm_nl($def);

  if ($defN === '' || $txtN !== $defN) {
    $ui_overrides[$key] = $txtN;
  }
}

if (!empty($ui_overrides)) {
  $existing = $payload['prompts_override'] ?? [];
  if (!is_array($existing)) $existing = [];
  $payload['prompts_override'] = array_merge($existing, $ui_overrides);
}

$json = json_encode($payload, JSON_UNESCAPED_UNICODE);

// ВАЖНО для Windows: -X utf8
$cmd = 'py/.venv/bin/python -X utf8 py/cli.py';

$descriptors = [
  0 => ['pipe', 'r'],
  1 => ['pipe', 'w'],
  2 => ['pipe', 'w']
];

$env = [
  'OPENAI_API_KEY' => getenv('OPENAI_API_KEY') ?: '',
  'HOME' => '/var/www',
];
$proc = proc_open($cmd, $descriptors, $pipes, $base, $env);
if (!is_resource($proc)) {
  http_response_code(500);
  echo "Failed to start python";
  exit;
}

fwrite($pipes[0], $json);
fclose($pipes[0]);

$out = stream_get_contents($pipes[1]);
$err = stream_get_contents($pipes[2]);
fclose($pipes[1]);
fclose($pipes[2]);

$code = proc_close($proc);

$res = json_decode($out, true);
?>
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Radar result</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 980px; margin: 24px auto; padding: 0 12px; }
    pre { white-space: pre-wrap; background:#f6f6f6; padding: 12px; border:1px solid #ddd; }
    img { max-width: 980px; border:1px solid #ddd; }
  </style>
</head>
<body>
  <h1>Result</h1>

  <pre><?php
    echo htmlspecialchars("exit_code=$code\n\nstdout:\n$out\n\nstderr:\n$err");
  ?></pre>

  <?php if (is_array($res) && ($res['ok'] ?? false)): ?>
    <?php $runDirRel = 'runs/' . $run_id; ?>
<?php
$zipRel = $runDirRel . '/run.zip';
$runAbs = __DIR__ . DIRECTORY_SEPARATOR . $runDirRel;
$zipAbs = __DIR__ . DIRECTORY_SEPARATOR . $zipRel;

if (isset($code) && intval($code) === 0) {
  if (file_exists($zipAbs)) { @unlink($zipAbs); }
  if (true) {
    $parts = [];
    foreach (['sales_note.txt','report.md','data.json','data.csv'] as $f) {
      if (file_exists($runAbs . DIRECTORY_SEPARATOR . $f)) $parts[] = escapeshellarg($f);
    }
    foreach (['screenshots','uploads'] as $d) {
      if (is_dir($runAbs . DIRECTORY_SEPARATOR . $d)) $parts[] = escapeshellarg($d);
    }
    if (!empty($parts)) {
      $cmdZip = 'cd ' . escapeshellarg($runAbs) . ' && zip -r ' . escapeshellarg('run.zip') . ' ' . implode(' ', $parts);
      @shell_exec($cmdZip);
    }
  }
}
?>

    <h2>Artifacts</h2>
    <ul>
      <li><a href="<?php echo $runDirRel . '/sales_note.txt'; ?>">sales_note.txt</a></li>
      <li><a href="<?php echo $runDirRel . '/report.md'; ?>">report.md</a></li>
      <li><a href="<?php echo $runDirRel . '/data.json'; ?>">data.json</a></li>
      <li><a href="<?php echo $runDirRel . '/data.csv'; ?>">data.csv</a></li>
    </ul>
<?php if (isset($zipRel) && file_exists(__DIR__ . DIRECTORY_SEPARATOR . $zipRel)) { ?>
  <p><a href="<?php echo htmlspecialchars($zipRel); ?>">Download ZIP</a></p>
<?php } ?>


    <h2>Screenshots</h2>
    <?php
      $ssDirRel = $runDirRel . '/screenshots';
      $ssDirAbs = __DIR__ . DIRECTORY_SEPARATOR . $ssDirRel;

      $imgs = list_images_recursive_1_level($ssDirAbs, $ssDirRel);
      foreach ($imgs as $pair) {
        $src = $pair[0];
        $label = $pair[1];
        echo '<div style="margin:10px 0;">';
        echo '<div>' . htmlspecialchars($label) . '</div>';
        echo '<img src="' . htmlspecialchars($src) . '" />';
        echo '</div>';
      }
    ?>
  <?php endif; ?>
</body>
</html>
