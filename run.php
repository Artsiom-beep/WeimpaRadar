<?php
// run.php

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

$client_domain = trim($_POST['client_domain'] ?? '');
$market = trim($_POST['market'] ?? 'Global');
$language = trim($_POST['language'] ?? 'en');
$mode = trim($_POST['mode'] ?? 'sales');
$competitor_1 = trim($_POST['competitor_1'] ?? '');
$slide_limit = intval($_POST['slide_limit'] ?? 0);

if ($client_domain === '') {
  http_response_code(400);
  echo "client_domain is required";
  exit;
}

$run_id = date('Y-m-d') . '__' . slug($client_domain) . '__' . $mode . '__' . $language;

$base = __DIR__;
$runs_dir = $base . DIRECTORY_SEPARATOR . 'runs';
$run_dir  = $runs_dir . DIRECTORY_SEPARATOR . $run_id;
$uploads_dir = $run_dir . DIRECTORY_SEPARATOR . 'uploads';

ensure_dir($uploads_dir);

// IMPORTANT: Python cmd_run читает uploads из runs/{run_id}/uploads :contentReference[oaicite:2]{index=2}
save_upload('semrush_overview', $uploads_dir . DIRECTORY_SEPARATOR . 'semrush_overview.png');
save_upload('blocked_screen', $uploads_dir . DIRECTORY_SEPARATOR . 'blocked_screen.png');

$competitors = [];
if ($competitor_1 !== '') $competitors[] = $competitor_1;

$payload = [
  'cmd' => 'run',
  'client_domain' => $client_domain,
  'market' => $market,
  'language' => $language,
  'mode' => $mode,
  'competitors' => $competitors,
  'run_id' => $run_id
];

// slide_limit передаём только если > 0 (Python включает слайды только при наличии ключа) :contentReference[oaicite:3]{index=3}
if ($slide_limit > 0) $payload['slide_limit'] = $slide_limit;

$json = json_encode($payload, JSON_UNESCAPED_UNICODE);

// Вызов Python через stdin -> stdout JSON :contentReference[oaicite:4]{index=4}
$cmd = 'python py/cli.py';
$descriptors = [
  0 => ['pipe', 'r'],
  1 => ['pipe', 'w'],
  2 => ['pipe', 'w']
];

$proc = proc_open($cmd, $descriptors, $pipes, $base);
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
</head>
<body>
  <h1>Result</h1>

  <pre><?php
    echo htmlspecialchars("exit_code=$code\n\nstdout:\n$out\n\nstderr:\n$err");
  ?></pre>

  <?php if (is_array($res) && ($res['ok'] ?? false)): ?>
    <?php
      $paths = $res['paths'] ?? [];
      $runDirRel = 'runs/' . $run_id;
    ?>
    <h2>Artifacts</h2>
    <ul>
      <li><a href="<?php echo $runDirRel . '/sales_note.txt'; ?>">sales_note.txt</a></li>
      <li><a href="<?php echo $runDirRel . '/report.md'; ?>">report.md</a></li>
      <li><a href="<?php echo $runDirRel . '/data.json'; ?>">data.json</a></li>
      <li><a href="<?php echo $runDirRel . '/data.csv'; ?>">data.csv</a></li>
    </ul>

    <h2>Screenshots</h2>
    <?php
      $ssDir = $runDirRel . '/screenshots';
      if (is_dir(__DIR__ . DIRECTORY_SEPARATOR . $ssDir)) {
        $files = scandir(__DIR__ . DIRECTORY_SEPARATOR . $ssDir);
        foreach ($files as $f) {
          if ($f === '.' || $f === '..') continue;
          if (!preg_match('/\.(png|jpg|jpeg|webp)$/i', $f)) continue;
          $src = $ssDir . '/' . $f;
          echo '<div style="margin:10px 0;">';
          echo '<div>' . htmlspecialchars($f) . '</div>';
          echo '<img src="' . htmlspecialchars($src) . '" style="max-width: 980px; border:1px solid #ddd;" />';
          echo '</div>';
        }
      }
    ?>
  <?php endif; ?>
</body>
</html>
